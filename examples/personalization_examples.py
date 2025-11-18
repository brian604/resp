"""
Examples demonstrating personalized paper discovery with RESP.

Requirements:
    pip install -e ".[summarization]"  # Includes OpenAI dependency

Set your OpenAI API key:
    export OPENAI_API_KEY='your-api-key'
"""

from resp import Resp
from resp.personalization import ResearchProfile, RelevanceScorer


def example1_use_template():
    """Example 1: Using a built-in profile template."""
    print("\n=== Example 1: Using Built-in Templates ===\n")

    resp = Resp()

    # Load a template (ml, nlp, or cv)
    resp.set_research_profile("ml")

    # Fetch recent papers
    papers = resp.arxiv_direct("machine learning", max_pages=2)
    print(f"Found {len(papers)} papers")

    # Rank by relevance to profile
    print("\nRanking papers by relevance...")
    ranked = resp.rank_by_relevance(papers, threshold=6.0)

    # Display top results
    print(f"\nTop 5 most relevant papers:\n")
    for i, paper in ranked.head(5).iterrows():
        score = paper.get('relevance_score', 0)
        reasoning = paper.get('relevance_reasoning', 'No reasoning')
        print(f"{i+1}. [{score:.1f}/10] {paper['title']}")
        print(f"   Reasoning: {reasoning}\n")


def example2_custom_profile():
    """Example 2: Creating a custom research profile."""
    print("\n=== Example 2: Custom Research Profile ===\n")

    # Create custom profile
    profile = ResearchProfile(
        name="My Custom Profile",
        email="researcher@example.com",
        arxiv_categories=["cs.LG", "cs.AI"],
        primary_interests=[
            "Efficient training methods for large models",
            "Model compression and quantization techniques",
            "Energy-efficient AI and green computing"
        ],
        secondary_interests=[
            "Distributed training systems",
            "Hardware-software co-design for ML"
        ],
        exclusions=[
            "Pure theoretical papers without code",
            "Medical applications only"
        ]
    )

    # Save profile for later use
    profile.to_yaml("my_profile.yaml")
    print(f"Profile saved to: my_profile.yaml\n")

    # Use the profile
    resp = Resp()
    resp.set_research_profile(profile)

    # Search and rank
    papers = resp.arxiv_direct("neural networks", max_pages=1)
    ranked = resp.rank_by_relevance(papers)

    print(f"Ranked {len(ranked)} papers")


def example3_load_from_file():
    """Example 3: Loading profile from YAML file."""
    print("\n=== Example 3: Loading Profile from File ===\n")

    resp = Resp()

    # Load from YAML file (created in example 2)
    resp.set_research_profile("my_profile.yaml")

    # Or load template and customize
    profile = ResearchProfile.from_template("nlp")
    profile.name = "My NLP Profile"
    profile.email = "my@email.com"
    profile.primary_interests.append("Multimodal learning")

    resp.set_research_profile(profile)

    # Use it
    papers = resp.arxiv_direct("transformers", max_pages=1)
    ranked = resp.rank_by_relevance(papers)

    print(f"Found {len(ranked)} relevant papers")


def example4_direct_scorer_use():
    """Example 4: Using RelevanceScorer directly."""
    print("\n=== Example 4: Direct Scorer Usage ===\n")

    # Create profile
    profile = ResearchProfile.from_template("cv")

    # Create scorer
    scorer = RelevanceScorer(profile, enable_cache=True)

    # Score individual paper
    paper = {
        "title": "Vision Transformers for Image Classification",
        "abstract": "We propose a novel vision transformer architecture..."
    }

    result = scorer.score_paper(paper)
    print(f"Paper: {paper['title']}")
    print(f"Score: {result['score']}/10")
    print(f"Reasoning: {result['reasoning']}")
    print(f"From cache: {result.get('from_cache', False)}")

    # Get stats
    stats = scorer.get_stats()
    print(f"\nScoring stats:")
    print(f"  Tokens used: {stats['total_tokens']}")
    print(f"  Estimated cost: ${stats['estimated_cost_usd']}")


def example5_batch_scoring():
    """Example 5: Efficient batch scoring."""
    print("\n=== Example 5: Batch Scoring ===\n")

    resp = Resp()
    resp.set_research_profile("ml")

    # Fetch papers
    papers = resp.arxiv_direct("deep learning", max_pages=3)
    print(f"Fetched {len(papers)} papers")

    # Rank with specific threshold
    print("\nScoring and ranking...")
    ranked = resp.rank_by_relevance(
        papers,
        threshold=7.0  # Only papers scoring 7+ out of 10
    )

    print(f"\n{len(ranked)} papers scored above 7.0:")
    for i, paper in ranked.iterrows():
        score = paper.get('relevance_score', 0)
        cached = " (cached)" if paper.get('score_from_cache') else ""
        print(f"  [{score:.1f}] {paper['title'][:60]}...{cached}")


def example6_profile_validation():
    """Example 6: Profile validation."""
    print("\n=== Example 6: Profile Validation ===\n")

    # Create invalid profile
    profile = ResearchProfile(
        name="",  # Invalid: empty name
        primary_interests=[],  # Invalid: no interests
        arxiv_categories=["invalid_category"]  # Invalid format
    )

    # Validate
    errors = profile.validate()

    if errors:
        print("Profile validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Profile is valid!")


def example7_cost_management():
    """Example 7: Managing API costs with caching."""
    print("\n=== Example 7: Cost Management ===\n")

    profile = ResearchProfile.from_template("nlp")

    # Enable caching to avoid re-scoring same papers
    scorer = RelevanceScorer(
        profile,
        enable_cache=True
    )

    # First run - will call API
    papers = [
        {"title": "Paper 1", "abstract": "About transformers..."},
        {"title": "Paper 2", "abstract": "About BERT..."},
    ]

    print("First scoring run:")
    results1 = scorer.score_papers(papers, show_progress=False)
    stats1 = scorer.get_stats()
    print(f"  Tokens: {stats1['total_tokens']}, Cost: ${stats1['estimated_cost_usd']}")

    # Second run - will use cache
    print("\nSecond scoring run (should use cache):")
    results2 = scorer.score_papers(papers, show_progress=False)
    stats2 = scorer.get_stats()
    print(f"  Tokens: {stats2['total_tokens']}, Cost: ${stats2['estimated_cost_usd']}")

    # Check cache usage
    cached_count = sum(1 for p in results2 if p.get('score_from_cache'))
    print(f"\n{cached_count}/{len(papers)} results from cache")

    # Clear cache if needed
    # scorer.clear_cache()


def example8_daily_digest_workflow():
    """Example 8: Daily digest workflow."""
    print("\n=== Example 8: Daily Digest Workflow ===\n")

    resp = Resp()

    # Set profile
    resp.set_research_profile("ml")

    # Fetch today's papers
    print("Fetching today's papers from arXiv...")
    papers = resp.fetch_daily_papers(days_back=1, max_papers=50)

    if papers.empty:
        print("No papers found")
        return

    print(f"Found {len(papers)} papers")

    # Rank by relevance
    print("\nRanking by relevance...")
    ranked = resp.rank_by_relevance(papers, threshold=6.5)

    # Save results
    if not ranked.empty:
        ranked.to_csv("daily_digest.csv", index=False)
        print(f"\nSaved {len(ranked)} papers to daily_digest.csv")

        # Show top papers
        print("\nTop 3 papers today:")
        for i, paper in ranked.head(3).iterrows():
            print(f"\n{i+1}. {paper['title']}")
            print(f"   Score: {paper['relevance_score']:.1f}/10")
            print(f"   {paper['relevance_reasoning']}")


def example9_compare_profiles():
    """Example 9: Compare different profiles on same papers."""
    print("\n=== Example 9: Profile Comparison ===\n")

    resp = Resp()

    # Fetch papers once
    papers = resp.arxiv_direct("artificial intelligence", max_pages=1)
    print(f"Testing {len(papers)} papers\n")

    # Test with different profiles
    profiles = ["ml", "nlp", "cv"]

    results = {}
    for profile_name in profiles:
        resp.set_research_profile(profile_name)
        ranked = resp.rank_by_relevance(papers, threshold=6.0)
        results[profile_name] = len(ranked)
        print(f"{profile_name.upper()}: {len(ranked)} papers above threshold")

    # Show most versatile papers (relevant to multiple profiles)
    print("\nPapers relevant to multiple profiles:")
    # (Would need to implement cross-profile analysis)


def main():
    """Run selected examples."""

    print("\n" + "="*80)
    print("RESP Personalization Examples")
    print("="*80)

    # Uncomment examples you want to run:

    # example1_use_template()
    # example2_custom_profile()
    # example3_load_from_file()
    # example4_direct_scorer_use()
    # example5_batch_scoring()
    # example6_profile_validation()
    # example7_cost_management()
    # example8_daily_digest_workflow()
    # example9_compare_profiles()

    print("\nNote: Uncomment examples you want to run in main() function")
    print("Make sure to set OPENAI_API_KEY environment variable")


if __name__ == '__main__':
    main()
