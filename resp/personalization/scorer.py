"""
LLM-based relevance scoring for personalized paper ranking.
"""

import os
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import pandas as pd

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from resp.personalization.profile import ResearchProfile


class RelevanceScorer:
    """
    Score papers against research interests using LLM.

    Uses OpenAI or compatible APIs to score papers on a 1-10 scale
    based on relevance to a research profile.
    """

    def __init__(
        self,
        profile: ResearchProfile,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        enable_cache: bool = True,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize relevance scorer.

        Args:
            profile: Research profile to score against
            api_key: OpenAI API key (or compatible)
            base_url: Custom API base URL for compatible services
            enable_cache: Enable response caching
            cache_dir: Directory for cache files
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )

        self.profile = profile
        self.enable_cache = enable_cache

        # Setup cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / '.resp' / 'cache' / 'scores'

        if enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize OpenAI client
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)

        # Scoring configuration
        self.model = profile.scoring_config.get('model', 'gpt-3.5-turbo')
        self.temperature = profile.scoring_config.get('temperature', 0.3)
        self.batch_size = profile.scoring_config.get('batch_size', 10)

        # Track API usage
        self.total_tokens = 0
        self.total_cost = 0.0

    def _get_cache_key(self, paper: Dict) -> str:
        """
        Generate cache key for a paper.

        Args:
            paper: Paper dictionary

        Returns:
            Cache key (hash)
        """
        # Create unique key from paper content and profile
        content = f"{paper.get('title', '')}||{paper.get('abstract', '')}"
        profile_key = json.dumps(self.profile.to_dict(), sort_keys=True)
        combined = f"{content}||{profile_key}||{self.model}"

        return hashlib.md5(combined.encode()).hexdigest()

    def _get_cached_score(self, cache_key: str) -> Optional[Dict]:
        """
        Get cached score if available.

        Args:
            cache_key: Cache key

        Returns:
            Cached result or None
        """
        if not self.enable_cache:
            return None

        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None

        return None

    def _save_to_cache(self, cache_key: str, result: Dict):
        """
        Save score to cache.

        Args:
            cache_key: Cache key
            result: Result to cache
        """
        if not self.enable_cache:
            return

        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except Exception as e:
            print(f"Warning: Could not save to cache: {e}")

    def _create_scoring_prompt(self, paper: Dict) -> str:
        """
        Create prompt for scoring a paper.

        Args:
            paper: Paper dictionary with title and abstract

        Returns:
            Formatted prompt
        """
        title = paper.get('title', 'Unknown')
        abstract = paper.get('abstract', 'No abstract available')

        interest_desc = self.profile.get_interest_description()

        prompt = f"""You are an expert research assistant helping to curate personalized academic paper recommendations.

RESEARCHER'S INTERESTS:
{interest_desc}

PAPER TO EVALUATE:
Title: {title}

Abstract: {abstract}

TASK:
Rate this paper's relevance to the researcher's interests on a scale of 1-10, where:
- 1-3: Not relevant (contradicts interests or falls into exclusions)
- 4-6: Somewhat relevant (tangentially related or secondary interest)
- 7-8: Highly relevant (matches primary interests)
- 9-10: Extremely relevant (perfect match, breakthrough in primary interest area)

Respond with ONLY a JSON object in this exact format:
{{
  "score": <number 1-10>,
  "reasoning": "<brief explanation in 1-2 sentences>"
}}

Do not include any other text outside the JSON object."""

        return prompt

    def score_paper(
        self,
        paper: Dict,
        use_cache: bool = True
    ) -> Dict:
        """
        Score a single paper.

        Args:
            paper: Paper dictionary with title and abstract
            use_cache: Whether to use cache

        Returns:
            Dictionary with score, reasoning, and metadata
        """
        # Check cache
        if use_cache and self.enable_cache:
            cache_key = self._get_cache_key(paper)
            cached = self._get_cached_score(cache_key)
            if cached:
                cached['from_cache'] = True
                return cached

        # Create prompt
        prompt = self._create_scoring_prompt(paper)

        try:
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that evaluates paper relevance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=200,
                response_format={"type": "json_object"}  # Ensure JSON response
            )

            # Parse response
            content = response.choices[0].message.content.strip()
            result = json.loads(content)

            # Add metadata
            result['model'] = self.model
            result['from_cache'] = False

            # Track usage
            if hasattr(response, 'usage'):
                self.total_tokens += response.usage.total_tokens
                result['tokens_used'] = response.usage.total_tokens

            # Save to cache
            if use_cache and self.enable_cache:
                self._save_to_cache(cache_key, result)

            return result

        except json.JSONDecodeError as e:
            return {
                'score': 5.0,
                'reasoning': f"Error parsing LLM response: {str(e)}",
                'error': True
            }
        except Exception as e:
            return {
                'score': 5.0,
                'reasoning': f"Error scoring paper: {str(e)}",
                'error': True
            }

    def score_papers(
        self,
        papers: List[Dict],
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Score multiple papers with batch processing.

        Args:
            papers: List of paper dictionaries
            show_progress: Show progress bar

        Returns:
            List of papers with added scoring fields
        """
        from tqdm import tqdm

        scored_papers = []

        iterator = tqdm(papers, desc="Scoring papers") if show_progress else papers

        for paper in iterator:
            result = self.score_paper(paper)

            # Add scoring fields to paper
            paper_with_score = paper.copy()
            paper_with_score['relevance_score'] = result.get('score', 5.0)
            paper_with_score['relevance_reasoning'] = result.get('reasoning', '')
            paper_with_score['score_from_cache'] = result.get('from_cache', False)

            if 'error' in result:
                paper_with_score['scoring_error'] = True

            scored_papers.append(paper_with_score)

        return scored_papers

    def score_and_rank(
        self,
        papers: List[Dict],
        threshold: Optional[float] = None,
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Score papers and return ranked results.

        Args:
            papers: List of paper dictionaries
            threshold: Minimum score threshold (uses profile default if None)
            top_k: Maximum number of results to return

        Returns:
            Ranked list of papers above threshold
        """
        # Score all papers
        scored = self.score_papers(papers)

        # Apply threshold
        if threshold is None:
            threshold = self.profile.scoring_config.get('threshold', 0.0)

        filtered = [p for p in scored if p.get('relevance_score', 0) >= threshold]

        # Sort by score (descending)
        ranked = sorted(filtered, key=lambda x: x.get('relevance_score', 0), reverse=True)

        # Apply top_k limit
        if top_k:
            ranked = ranked[:top_k]

        return ranked

    def score_dataframe(
        self,
        papers_df: pd.DataFrame,
        threshold: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Score papers in a DataFrame.

        Args:
            papers_df: DataFrame with title and abstract columns
            threshold: Minimum score threshold

        Returns:
            DataFrame with added score columns, sorted by relevance
        """
        # Convert to list of dicts
        papers = papers_df.to_dict('records')

        # Score and rank
        ranked = self.score_and_rank(papers, threshold=threshold)

        # Convert back to DataFrame
        return pd.DataFrame(ranked)

    def get_stats(self) -> Dict:
        """
        Get scoring statistics.

        Returns:
            Dictionary with stats (tokens used, estimated cost, etc.)
        """
        # Rough cost estimates (as of 2024)
        cost_per_1k = {
            'gpt-3.5-turbo': 0.0015,  # $0.0015 per 1K tokens
            'gpt-4': 0.03,  # $0.03 per 1K tokens
            'gpt-4-turbo': 0.01,  # $0.01 per 1K tokens
        }

        rate = cost_per_1k.get(self.model, 0.0015)
        estimated_cost = (self.total_tokens / 1000) * rate

        return {
            'total_tokens': self.total_tokens,
            'estimated_cost_usd': round(estimated_cost, 4),
            'model': self.model,
            'cache_enabled': self.enable_cache,
            'cache_dir': str(self.cache_dir) if self.enable_cache else None
        }

    def clear_cache(self):
        """Clear all cached scores."""
        if self.enable_cache and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
            print(f"Cache cleared: {self.cache_dir}")
