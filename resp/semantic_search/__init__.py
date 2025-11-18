"""
Semantic search module for RESP library.
Supports embedding-based similarity search and re-ranking.
"""

from resp.semantic_search.embedder import BaseEmbedder, SentenceTransformerEmbedder
from resp.semantic_search.reranker import SemanticReranker
from resp.semantic_search.vector_store import VectorStore

__all__ = [
    'BaseEmbedder',
    'SentenceTransformerEmbedder',
    'SemanticReranker',
    'VectorStore'
]
