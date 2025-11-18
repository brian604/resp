"""
Vector database for semantic search with FAISS.
"""

import os
import json
import pickle
from typing import List, Dict, Optional, Tuple
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from resp.semantic_search.embedder import BaseEmbedder, SentenceTransformerEmbedder


class VectorStore:
    """
    Vector database for semantic search using FAISS.

    Supports:
    - Building an index from papers
    - Searching by semantic similarity
    - Persisting to disk
    - Incremental updates
    """

    def __init__(
        self,
        embedder: Optional[BaseEmbedder] = None,
        index_type: str = "flat",
        text_field_builder: Optional[callable] = None
    ):
        """
        Initialize vector store.

        Args:
            embedder: Embedding model to use
            index_type: Type of FAISS index
                       'flat' - Exact search (IndexFlatIP)
                       'ivf' - Inverted file index (faster for large datasets)
                       'hnsw' - Hierarchical NSW (good balance)
            text_field_builder: Function to extract text from paper dict
        """
        if not FAISS_AVAILABLE:
            raise ImportError(
                "faiss not installed. Install with: "
                "pip install faiss-cpu  (or faiss-gpu for GPU support)"
            )

        if embedder is None:
            embedder = SentenceTransformerEmbedder()

        self.embedder = embedder
        self.index_type = index_type
        self.text_field_builder = text_field_builder or self._default_text_builder

        self.dimension = self.embedder.get_dimension()
        self.index = None
        self.paper_metadata = []  # List of paper dicts
        self.paper_ids = []  # List of paper IDs for lookup

        self._init_index()

    @staticmethod
    def _default_text_builder(paper: Dict) -> str:
        """Default text builder: title + abstract."""
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        if abstract:
            return f"{title}. {abstract}"
        return title

    def _init_index(self):
        """Initialize FAISS index based on type."""
        if self.index_type == "flat":
            # Exact search using inner product (on normalized vectors = cosine)
            self.index = faiss.IndexFlatIP(self.dimension)

        elif self.index_type == "ivf":
            # IVF index - faster for large datasets
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(
                quantizer,
                self.dimension,
                100,  # nlist - number of clusters
                faiss.METRIC_INNER_PRODUCT
            )

        elif self.index_type == "hnsw":
            # HNSW index - good balance of speed and accuracy
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 = M parameter

        else:
            raise ValueError(f"Unknown index type: {self.index_type}")

    def build_index(self, papers: List[Dict], show_progress: bool = True):
        """
        Build index from a list of papers.

        Args:
            papers: List of paper dictionaries
            show_progress: Whether to show progress bar
        """
        if not papers:
            print("Warning: No papers provided to build index")
            return

        from tqdm import tqdm

        print(f"Building index for {len(papers)} papers...")

        # Extract texts
        texts = []
        valid_papers = []

        iterator = tqdm(papers) if show_progress else papers

        for paper in iterator:
            text = self.text_field_builder(paper)
            if text:  # Only add papers with text
                texts.append(text)
                valid_papers.append(paper)

        if not texts:
            print("Warning: No valid texts extracted from papers")
            return

        # Generate embeddings in batches
        print("Generating embeddings...")
        batch_size = 32
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.embedder.embed(batch)
            all_embeddings.append(embeddings)

        embeddings = np.vstack(all_embeddings).astype('float32')

        # Train index if needed (for IVF)
        if self.index_type == "ivf":
            print("Training IVF index...")
            self.index.train(embeddings)

        # Add to index
        print("Adding vectors to index...")
        self.index.add(embeddings)

        # Store metadata
        self.paper_metadata = valid_papers
        self.paper_ids = [
            paper.get('id', paper.get('link', f"paper_{i}"))
            for i, paper in enumerate(valid_papers)
        ]

        print(f"Index built successfully with {self.index.ntotal} vectors")

    def search(
        self,
        query: str,
        k: int = 20,
        return_scores: bool = True
    ) -> List[Dict]:
        """
        Search for papers similar to query.

        Args:
            query: Search query
            k: Number of results to return
            return_scores: Whether to include similarity scores

        Returns:
            List of paper dictionaries sorted by similarity
        """
        if self.index is None or self.index.ntotal == 0:
            print("Warning: Index is empty. Build index first.")
            return []

        # Embed query
        query_vec = self.embedder.embed(query)
        if query_vec.ndim == 1:
            query_vec = query_vec.reshape(1, -1)
        query_vec = query_vec.astype('float32')

        # Search index
        if self.index_type == "ivf":
            # Set search parameters for IVF
            self.index.nprobe = 10  # number of clusters to search

        distances, indices = self.index.search(query_vec, k)

        # Build results
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.paper_metadata):
                paper = self.paper_metadata[idx].copy()
                if return_scores:
                    paper['semantic_score'] = float(score)
                results.append(paper)

        return results

    def add_papers(self, papers: List[Dict]):
        """
        Incrementally add papers to existing index.

        Args:
            papers: List of paper dictionaries to add
        """
        if not papers:
            return

        # Extract texts and embeddings
        texts = [self.text_field_builder(p) for p in papers]
        embeddings = self.embedder.embed(texts).astype('float32')

        # Add to index
        self.index.add(embeddings)

        # Update metadata
        self.paper_metadata.extend(papers)
        new_ids = [
            paper.get('id', paper.get('link', f"paper_{len(self.paper_ids) + i}"))
            for i, paper in enumerate(papers)
        ]
        self.paper_ids.extend(new_ids)

        print(f"Added {len(papers)} papers. Total: {self.index.ntotal}")

    def save(self, directory: str):
        """
        Save index and metadata to disk.

        Args:
            directory: Directory to save files
        """
        os.makedirs(directory, exist_ok=True)

        # Save FAISS index
        index_path = os.path.join(directory, "faiss_index.bin")
        faiss.write_index(self.index, index_path)

        # Save metadata
        metadata_path = os.path.join(directory, "metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'paper_metadata': self.paper_metadata,
                'paper_ids': self.paper_ids,
                'dimension': self.dimension,
                'index_type': self.index_type
            }, f)

        # Save config
        config_path = os.path.join(directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump({
                'embedder_model': getattr(self.embedder, 'model_name', 'unknown'),
                'dimension': self.dimension,
                'index_type': self.index_type,
                'num_papers': len(self.paper_metadata)
            }, f, indent=2)

        print(f"Index saved to {directory}")

    def load(self, directory: str):
        """
        Load index and metadata from disk.

        Args:
            directory: Directory containing saved files
        """
        # Load FAISS index
        index_path = os.path.join(directory, "faiss_index.bin")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found at {index_path}")

        self.index = faiss.read_index(index_path)

        # Load metadata
        metadata_path = os.path.join(directory, "metadata.pkl")
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
            self.paper_metadata = data['paper_metadata']
            self.paper_ids = data['paper_ids']
            self.dimension = data['dimension']
            self.index_type = data['index_type']

        print(f"Loaded index with {self.index.ntotal} vectors from {directory}")

    def get_stats(self) -> Dict:
        """
        Get statistics about the index.

        Returns:
            Dictionary with index statistics
        """
        return {
            'num_papers': len(self.paper_metadata),
            'num_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'is_trained': self.index.is_trained if hasattr(self.index, 'is_trained') else True
        }

    def clear(self):
        """Clear the index and metadata."""
        self._init_index()
        self.paper_metadata = []
        self.paper_ids = []
        print("Index cleared")
