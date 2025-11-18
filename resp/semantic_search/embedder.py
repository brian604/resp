"""
Embedding models for semantic search.
"""

from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class BaseEmbedder(ABC):
    """Abstract base class for embedding models."""

    @abstractmethod
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text(s).

        Args:
            texts: Single text or list of texts to embed

        Returns:
            numpy array of embeddings, shape (n, dim) or (dim,)
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        pass


class SentenceTransformerEmbedder(BaseEmbedder):
    """
    Embedder using SentenceTransformers models.

    Recommended models:
    - 'all-MiniLM-L6-v2' - Fast, lightweight, 384 dim
    - 'multi-qa-MiniLM-L6-cos-v1' - Optimized for Q&A/retrieval, 384 dim
    - 'all-mpnet-base-v2' - Higher quality, slower, 768 dim
    - 'allenai-specter' - Specialized for scientific papers, 768 dim
    """

    def __init__(
        self,
        model_name: str = "multi-qa-MiniLM-L6-cos-v1",
        device: str = None,
        normalize_embeddings: bool = True
    ):
        """
        Initialize SentenceTransformer embedder.

        Args:
            model_name: Name of the SentenceTransformer model
            device: Device to use ('cpu', 'cuda', or None for auto)
            normalize_embeddings: Whether to normalize embeddings (recommended for cosine similarity)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.normalize_embeddings = normalize_embeddings

        try:
            self.model = SentenceTransformer(model_name, device=device)
            self._dimension = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            raise Exception(f"Error loading model {model_name}: {str(e)}")

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text(s).

        Args:
            texts: Single text or list of texts

        Returns:
            numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]

        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=False
            )
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self._dimension


class OpenAIEmbedder(BaseEmbedder):
    """
    Embedder using OpenAI's embedding API.

    Models:
    - 'text-embedding-ada-002' - 1536 dim
    - 'text-embedding-3-small' - 1536 dim (newer, better)
    - 'text-embedding-3-large' - 3072 dim (highest quality)
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str = None,
        base_url: str = None
    ):
        """
        Initialize OpenAI embedder.

        Args:
            model: Model name
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            base_url: Optional custom base URL for compatible APIs
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package not installed. "
                "Install with: pip install openai"
            )

        self.model = model

        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if base_url:
            client_kwargs["base_url"] = base_url

        try:
            self.client = OpenAI(**client_kwargs)
        except Exception as e:
            raise Exception(f"Error initializing OpenAI client: {str(e)}")

        # Dimension mapping
        self._dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
        }
        self._dimension = self._dimensions.get(model, 1536)

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings using OpenAI API.

        Args:
            texts: Single text or list of texts

        Returns:
            numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings)

        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self._dimension
