"""
Examples demonstrating AI-powered paper summarization with RESP.

Make sure to install summarization dependencies:
    pip install -e ".[summarization]"

For local models:
    pip install -e ".[local]"
"""

import os
from resp import Resp
from resp.config import Config


def example1_basic_openai():
    """Example 1: Basic usage with OpenAI API."""
    print("\n=== Example 1: Basic OpenAI Summarization ===\n")

    # Set your API key (or use environment variable OPENAI_API_KEY)
    # os.environ['OPENAI_API_KEY'] = 'your-api-key'

    # Initialize with OpenAI summarizer
    resp = Resp(summarizer='openai')

    # Search and summarize papers from arXiv
    print("Searching arXiv for 'large language models'...")
    papers = resp.arxiv_direct(
        'large language models',
        max_pages=1,  # Fetch just 1 page for demo
        summarize=True
    )

    # Display results
    print(f"\nFound {len(papers)} papers:\n")
    for idx, paper in papers.iterrows():
        print(f"Title: {paper['title']}")
        print(f"Authors: {paper.get('authors', 'N/A')}")
        print(f"\nSummary: {paper.get('summary', 'N/A')}")
        print(f"\nKey Points: {paper.get('key_points', 'N/A')}")
        print(f"\nTL;DR: {paper.get('tldr', 'N/A')}")
        print("\n" + "="*80 + "\n")


def example2_openai_compatible_api():
    """Example 2: Using OpenAI-compatible APIs (e.g., DeepSeek)."""
    print("\n=== Example 2: OpenAI-Compatible API (DeepSeek) ===\n")

    # Configure for DeepSeek or other compatible service
    config = Config()
    config.set('summarizer.openai.base_url', 'https://api.deepseek.com/v1')
    config.set('summarizer.openai.model', 'deepseek-chat')
    config.set('summarizer.openai.temperature', 0.3)
    config.set('summarizer.openai.max_tokens', 500)

    # Set API key (or use environment variable)
    # config.set_api_key('openai', 'your-deepseek-api-key')
    # config.save_config()

    # Initialize with custom config
    resp = Resp(config=config, summarizer='openai')

    print("Searching arXiv for 'computer vision'...")
    papers = resp.arxiv_direct('computer vision', max_pages=1, summarize=True)

    print(f"\nFound {len(papers)} papers with summaries.\n")


def example3_local_transformers():
    """Example 3: Using local transformers models."""
    print("\n=== Example 3: Local Transformers Model ===\n")

    # Configure local model
    config = Config()
    config.set('summarizer.local.model_type', 'transformers')
    config.set('summarizer.local.model_name', 'facebook/bart-large-cnn')
    config.set('summarizer.local.device', 'cpu')  # Change to 'cuda' if available
    config.set('summarizer.local.max_length', 150)

    # Initialize with local summarizer
    print("Initializing local model (this may take a moment)...")
    resp = Resp(config=config, summarizer='local')

    print("Searching arXiv for 'neural networks'...")
    papers = resp.arxiv_direct('neural networks', max_pages=1, summarize=True)

    print(f"\nFound {len(papers)} papers with summaries.\n")
    for idx, paper in papers.iterrows():
        print(f"Title: {paper['title']}")
        print(f"Summary: {paper.get('summary', 'N/A')}")
        print("\n" + "-"*80 + "\n")


def example4_manual_summarization():
    """Example 4: Manual control over summarization."""
    print("\n=== Example 4: Manual Summarization ===\n")

    resp = Resp()

    # First, search for papers without summarization
    print("Searching arXiv for 'deep learning'...")
    papers = resp.arxiv_direct('deep learning', max_pages=1)

    print(f"Found {len(papers)} papers.\n")

    # Later, enable summarization
    print("Enabling OpenAI summarizer...")
    resp.set_summarizer('openai')

    # Summarize the papers
    print("Generating summaries...")
    summarized_papers = resp.summarize_papers(papers)

    print(f"\nSummarized {len(summarized_papers)} papers.\n")


def example5_direct_summarizer_use():
    """Example 5: Using summarizers directly."""
    print("\n=== Example 5: Direct Summarizer Usage ===\n")

    from resp.summarizers import OpenAISummarizer

    # Create summarizer directly
    summarizer = OpenAISummarizer(
        # api_key='your-api-key',  # Or use environment variable
        model='gpt-3.5-turbo',
        temperature=0.3,
        max_tokens=300
    )

    # Example paper
    title = "Attention Is All You Need"
    abstract = """The dominant sequence transduction models are based on complex
    recurrent or convolutional neural networks that include an encoder and a decoder.
    The best performing models also connect the encoder and decoder through an
    attention mechanism. We propose a new simple network architecture, the Transformer,
    based solely on attention mechanisms, dispensing with recurrence and convolutions
    entirely."""

    # Summarize
    print("Summarizing paper...")
    summary = summarizer.summarize_paper(title, abstract)

    print(f"\nTitle: {title}")
    print(f"\nSummary: {summary['summary']}")
    print(f"\nKey Points: {summary['key_points']}")
    print(f"\nTL;DR: {summary['tldr']}")


def example6_custom_model_config():
    """Example 6: Advanced configuration with custom models."""
    print("\n=== Example 6: Advanced Configuration ===\n")

    # Create custom configuration
    config = Config()

    # Configure OpenAI settings
    config.set('summarizer.openai.model', 'gpt-4')
    config.set('summarizer.openai.temperature', 0.2)
    config.set('summarizer.openai.max_tokens', 600)

    # Save configuration for future use
    config.save_config()

    print("Configuration saved to ~/.resp/config.json")
    print("\nTo use this configuration:")
    print("  resp = Resp(summarizer='openai')")


def example7_batch_summarization():
    """Example 7: Batch summarization of multiple papers."""
    print("\n=== Example 7: Batch Summarization ===\n")

    resp = Resp(summarizer='openai')

    # Search multiple sources
    print("Searching multiple sources...")
    papers1 = resp.arxiv_direct('transformers', max_pages=1)
    papers2 = resp.arxiv_direct('reinforcement learning', max_pages=1)

    # Combine results
    import pandas as pd
    all_papers = pd.concat([papers1, papers2]).reset_index(drop=True)

    print(f"Found {len(all_papers)} total papers.")

    # Batch summarize
    print("\nGenerating summaries for all papers...")
    summarized = resp.summarize_papers(all_papers)

    print(f"Summarized {len(summarized)} papers.\n")

    # Save to CSV
    output_file = 'summarized_papers.csv'
    summarized.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")


def main():
    """Run all examples (uncomment the ones you want to try)."""

    print("\n" + "="*80)
    print("RESP Summarization Examples")
    print("="*80)

    # Uncomment the examples you want to run:

    # example1_basic_openai()
    # example2_openai_compatible_api()
    # example3_local_transformers()
    # example4_manual_summarization()
    # example5_direct_summarizer_use()
    # example6_custom_model_config()
    # example7_batch_summarization()

    print("\nNote: Uncomment the examples you want to run in the main() function.")
    print("Make sure to set your API keys as environment variables or in the code.")


if __name__ == '__main__':
    main()
