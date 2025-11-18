"""
Examples demonstrating semantic search with RESP.

Make sure to install semantic search dependencies:
    pip install -e ".[semantic]"

This includes:
- sentence-transformers (for embeddings)
- faiss-cpu (for vector search)
"""

from resp import Resp


def example1_semantic_reranking():
    """Example 1: Semantic re-ranking of keyword search results."""
    print("\n=== Example 1: Semantic Re-ranking ===\n")

    # Initialize RESP with semantic search enabled
    resp = Resp(enable_semantic_search=True)

    # Search arXiv using keyword search
    query = "attention mechanisms in transformers"
    print(f"Searching for: '{query}'")

    papers = resp.arxiv_direct(query, max_pages=2)
    print(f"Found {len(papers)} papers with keyword search\n")

    # Re-rank using semantic similarity
    print("Re-ranking with semantic search...")
    reranked = resp.semantic_rerank(query, papers, top_k=10)

    print(f"\nTop 10 papers by semantic similarity:\n")
    for i, paper in reranked.head(10).iterrows():
        print(f"{i+1}. {paper['title']}")
        print(f"   Semantic score: {paper.get('semantic_score', 0):.4f}")
        print()


def example2_vector_store():
    """Example 2: Building and searching a vector database."""
    print("\n=== Example 2: Vector Store Search ===\n")

    resp = Resp()

    # Initialize vector store
    print("Initializing vector store...")
    resp.init_vector_store(
        embedder_model="multi-qa-MiniLM-L6-cos-v1",
        index_type="flat"  # or 'hnsw' for larger datasets
    )

    # Collect papers from multiple queries
    print("\nCollecting papers...")
    topics = ["transformers", "attention", "BERT", "GPT"]
    all_papers = []

    for topic in topics:
        print(f"  Fetching papers on: {topic}")
        papers = resp.arxiv_direct(topic, max_pages=1)
        all_papers.append(papers)

    import pandas as pd
    papers_df = pd.concat(all_papers).drop_duplicates('title')
    print(f"\nCollected {len(papers_df)} unique papers")

    # Build vector index
    print("\nBuilding vector index...")
    resp.build_vector_index(papers_df)

    # Search using semantic similarity
    query = "self-attention in neural networks"
    print(f"\nSearching for: '{query}'")

    results = resp.semantic_search(query, k=5)

    print(f"\nTop 5 semantically similar papers:\n")
    for i, paper in results.iterrows():
        print(f"{i+1}. {paper['title']}")
        print(f"   Score: {paper.get('semantic_score', 0):.4f}")
        print()


def example3_persist_vector_store():
    """Example 3: Saving and loading vector store."""
    print("\n=== Example 3: Persistent Vector Store ===\n")

    resp = Resp()
    resp.init_vector_store()

    # Build index
    print("Building index from papers...")
    papers = resp.arxiv_direct("machine learning", max_pages=2)
    resp.build_vector_index(papers)

    # Save to disk
    index_dir = "vector_index"
    print(f"\nSaving index to {index_dir}...")
    resp.save_vector_index(index_dir)

    # Later... load from disk
    print("\nLoading index from disk...")
    resp2 = Resp()
    resp2.load_vector_index(index_dir)

    # Search
    results = resp2.semantic_search("neural networks", k=3)
    print(f"\nFound {len(results)} papers from loaded index")


def example4_hybrid_search():
    """Example 4: Hybrid search combining keyword and semantic."""
    print("\n=== Example 4: Hybrid Search ===\n")

    from resp.semantic_search import SemanticReranker, SentenceTransformerEmbedder

    # Create reranker with hybrid scoring
    embedder = SentenceTransformerEmbedder(model_name="multi-qa-MiniLM-L6-cos-v1")
    reranker = SemanticReranker(
        embedder=embedder,
        hybrid_alpha=0.7  # 70% semantic, 30% original ranking
    )

    resp = Resp()
    query = "deep learning optimization"

    # Get keyword results
    papers = resp.arxiv_direct(query, max_pages=2)
    papers_list = papers.to_dict('records')

    print(f"Keyword search found {len(papers_list)} papers")

    # Re-rank with hybrid scoring
    reranked = reranker.rerank(query, papers_list, top_k=5)

    print(f"\nTop 5 papers (hybrid ranking):\n")
    for i, paper in enumerate(reranked):
        print(f"{i+1}. {paper['title']}")
        if 'hybrid_score' in paper:
            print(f"   Hybrid score: {paper['hybrid_score']:.4f}")
        print()


def example5_custom_embedder():
    """Example 5: Using different embedding models."""
    print("\n=== Example 5: Custom Embedding Models ===\n")

    # Scientific paper specialized model
    resp = Resp(
        enable_semantic_search=True,
        embedder_model="allenai-specter"  # Specialized for scientific papers
    )

    query = "protein folding prediction"
    papers = resp.arxiv_direct("protein folding", max_pages=1)

    print(f"Reranking with SPECTER (scientific paper embeddings)...")
    reranked = resp.semantic_rerank(query, papers, top_k=5)

    print(f"\nTop 5 papers:\n")
    for i, paper in reranked.head(5).iterrows():
        print(f"{i+1}. {paper['title']}")
        print(f"   Score: {paper.get('semantic_score', 0):.4f}")
        print()


def example6_direct_api_usage():
    """Example 6: Direct use of semantic search components."""
    print("\n=== Example 6: Direct API Usage ===\n")

    from resp.semantic_search import (
        SentenceTransformerEmbedder,
        SemanticReranker,
        VectorStore
    )

    # Create embedder
    embedder = SentenceTransformerEmbedder(
        model_name="all-MiniLM-L6-v2",  # Fast, lightweight
        normalize_embeddings=True
    )

    # Create reranker
    reranker = SemanticReranker(embedder=embedder)

    # Example papers
    papers = [
        {
            "title": "Attention Is All You Need",
            "abstract": "We propose the Transformer, a novel architecture based solely on attention mechanisms..."
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "abstract": "We introduce BERT, a new method for pre-training language representations..."
        },
        {
            "title": "GPT-3: Language Models are Few-Shot Learners",
            "abstract": "We show that scaling up language models greatly improves task-agnostic..."
        }
    ]

    # Re-rank
    query = "transformer architecture for NLP"
    ranked = reranker.rerank(query, papers)

    print("Papers ranked by semantic similarity:\n")
    for i, paper in enumerate(ranked):
        print(f"{i+1}. {paper['title']}")
        print(f"   Score: {paper['semantic_score']:.4f}")
        print()


def example7_incremental_indexing():
    """Example 7: Incrementally adding papers to vector store."""
    print("\n=== Example 7: Incremental Indexing ===\n")

    resp = Resp()
    resp.init_vector_store()

    # Initial batch
    print("Building initial index...")
    papers1 = resp.arxiv_direct("neural networks", max_pages=1)
    resp.build_vector_index(papers1)

    # Add more papers later
    print("\nAdding more papers...")
    papers2 = resp.arxiv_direct("deep learning", max_pages=1)
    resp.add_to_vector_index(papers2)

    papers3 = resp.arxiv_direct("computer vision", max_pages=1)
    resp.add_to_vector_index(papers3)

    # Check stats
    stats = resp._vector_store.get_stats()
    print(f"\nVector store statistics:")
    print(f"  Total papers: {stats['num_papers']}")
    print(f"  Vectors: {stats['num_vectors']}")
    print(f"  Dimension: {stats['dimension']}")


def example8_batch_queries():
    """Example 8: Batch processing multiple queries."""
    print("\n=== Example 8: Batch Query Processing ===\n")

    from resp.semantic_search import SemanticReranker, SentenceTransformerEmbedder

    embedder = SentenceTransformerEmbedder()
    reranker = SemanticReranker(embedder=embedder)

    resp = Resp()

    # Multiple queries
    queries = [
        "attention mechanisms",
        "transfer learning",
        "reinforcement learning"
    ]

    # Get papers for each query
    print("Fetching papers for multiple queries...")
    papers_list = []
    for query in queries:
        papers = resp.arxiv_direct(query, max_pages=1)
        papers_list.append(papers.to_dict('records'))

    # Batch re-rank
    print("\nRe-ranking all queries...")
    results = reranker.batch_rerank(queries, papers_list, top_k=3)

    # Display results
    for query, ranked_papers in zip(queries, results):
        print(f"\nTop 3 for '{query}':")
        for i, paper in enumerate(ranked_papers):
            print(f"  {i+1}. {paper['title'][:60]}...")


def main():
    """Run all examples (uncomment the ones you want to try)."""

    print("\n" + "="*80)
    print("RESP Semantic Search Examples")
    print("="*80)

    # Uncomment the examples you want to run:

    # example1_semantic_reranking()
    # example2_vector_store()
    # example3_persist_vector_store()
    # example4_hybrid_search()
    # example5_custom_embedder()
    # example6_direct_api_usage()
    # example7_incremental_indexing()
    # example8_batch_queries()

    print("\nNote: Uncomment the examples you want to run in the main() function.")
    print("Make sure to install semantic search dependencies:")
    print("  pip install -e '.[semantic]'")


if __name__ == '__main__':
    main()
