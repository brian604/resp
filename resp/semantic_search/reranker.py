"""
Semantic re-ranking for search results.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Callable
from numpy.linalg import norm

from resp.semantic_search.embedder import BaseEmbedder, SentenceTransformerEmbedder


class SemanticReranker:
    """
    Re-rank search results using semantic similarity.

    This takes results from keyword-based search (e.g., from APIs)
    and re-ranks them based on semantic similarity to the query.
    """

    def __init__(
        self,
        embedder: Optional[BaseEmbedder] = None,
        text_field_builder: Optional[Callable] = None,
        hybrid_alpha: float = 1.0
    ):
        """
        Initialize semantic reranker.

        Args:
            embedder: Embedding model to use (defaults to SentenceTransformer)
            text_field_builder: Custom function to build text from paper dict
                               Defaults to using title + abstract
            hybrid_alpha: Weight for semantic score (0-1)
                         1.0 = pure semantic, 0.0 = pure original ranking
                         Can combine with original API ranking if available
        """
        if embedder is None:
            embedder = SentenceTransformerEmbedder()

        self.embedder = embedder
        self.text_field_builder = text_field_builder or self._default_text_builder
        self.hybrid_alpha = hybrid_alpha

    @staticmethod
    def _default_text_builder(paper: Dict) -> str:
        """
        Default text builder: title + abstract.

        Args:
            paper: Paper dictionary

        Returns:
            Text representation of paper
        """
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')

        if abstract:
            return f"{title}. {abstract}"
        return title

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity score
        """
        return float(np.dot(a, b) / (norm(a) * norm(b) + 1e-10))

    def rerank(
        self,
        query: str,
        papers: List[Dict],
        top_k: Optional[int] = None,
        return_scores: bool = True,
        original_score_field: Optional[str] = None
    ) -> List[Dict]:
        """
        Re-rank papers based on semantic similarity to query.

        Args:
            query: Search query
            papers: List of paper dictionaries
            top_k: Number of top results to return (None = all)
            return_scores: Whether to add semantic_score to results
            original_score_field: Field name for original ranking score
                                 (used for hybrid ranking)

        Returns:
            List of papers sorted by semantic similarity
        """
        if not papers:
            return []

        # Embed query
        query_vec = self.embedder.embed(query)
        if query_vec.ndim > 1:
            query_vec = query_vec[0]

        # Build document texts and embed
        doc_texts = [self.text_field_builder(p) for p in papers]
        doc_vecs = self.embedder.embed(doc_texts)

        # Score each paper
        scored_papers = []
        for idx, (paper, doc_vec) in enumerate(zip(papers, doc_vecs)):
            # Compute semantic similarity
            semantic_score = self.cosine_similarity(query_vec, doc_vec)

            # Create copy to avoid modifying original
            paper_copy = paper.copy()

            # Hybrid scoring if original scores available
            if original_score_field and original_score_field in paper:
                original_score = paper[original_score_field]
                # Normalize original score to 0-1 if needed
                if original_score > 1.0:
                    original_score = original_score / 100.0

                final_score = (
                    self.hybrid_alpha * semantic_score +
                    (1 - self.hybrid_alpha) * original_score
                )
                paper_copy['hybrid_score'] = final_score
                paper_copy['semantic_score'] = semantic_score
                paper_copy['original_score'] = original_score
                sort_key = 'hybrid_score'
            else:
                # Pure semantic ranking
                if return_scores:
                    paper_copy['semantic_score'] = semantic_score
                sort_key = 'semantic_score'

            scored_papers.append(paper_copy)

        # Sort by score
        scored_papers.sort(key=lambda x: x[sort_key], reverse=True)

        # Return top k
        if top_k:
            return scored_papers[:top_k]
        return scored_papers

    def rerank_dataframe(
        self,
        query: str,
        papers_df: pd.DataFrame,
        top_k: Optional[int] = None,
        original_score_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Re-rank papers DataFrame based on semantic similarity.

        Args:
            query: Search query
            papers_df: DataFrame of papers
            top_k: Number of top results to return
            original_score_column: Column name for original scores

        Returns:
            Re-ranked DataFrame with semantic_score column
        """
        if papers_df.empty:
            return papers_df

        # Convert to list of dicts
        papers = papers_df.to_dict('records')

        # Re-rank
        ranked_papers = self.rerank(
            query,
            papers,
            top_k=top_k,
            return_scores=True,
            original_score_field=original_score_column
        )

        # Convert back to DataFrame
        return pd.DataFrame(ranked_papers)

    def batch_rerank(
        self,
        queries: List[str],
        papers_list: List[List[Dict]],
        top_k: Optional[int] = None
    ) -> List[List[Dict]]:
        """
        Re-rank multiple queries and their results in batch.

        Args:
            queries: List of search queries
            papers_list: List of paper lists (one per query)
            top_k: Number of top results per query

        Returns:
            List of re-ranked paper lists
        """
        results = []
        for query, papers in zip(queries, papers_list):
            ranked = self.rerank(query, papers, top_k=top_k)
            results.append(ranked)
        return results
