"""
Base class for all summarizers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseSummarizer(ABC):
    """
    Abstract base class for paper summarizers.
    All summarizer implementations should inherit from this class.
    """

    def __init__(self, **kwargs):
        """
        Initialize the summarizer.

        Args:
            **kwargs: Configuration parameters specific to each summarizer
        """
        self.config = kwargs

    @abstractmethod
    def summarize(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Generate a summary of the input text.

        Args:
            text: The text to summarize
            max_length: Maximum length of the summary (in words or tokens)

        Returns:
            The generated summary
        """
        pass

    @abstractmethod
    def summarize_paper(self, title: str, abstract: str) -> Dict[str, str]:
        """
        Generate a structured summary of a research paper.

        Args:
            title: Paper title
            abstract: Paper abstract

        Returns:
            Dictionary containing:
                - summary: Concise summary of the paper
                - key_points: Main contributions/findings
                - tldr: Very short one-line summary
        """
        pass

    def summarize_batch(self, papers: List[Dict]) -> List[Dict]:
        """
        Summarize multiple papers in batch.

        Args:
            papers: List of paper dictionaries with 'title' and 'abstract' keys

        Returns:
            List of papers with added summary fields
        """
        results = []
        for paper in papers:
            try:
                if 'abstract' in paper and paper['abstract']:
                    summary_data = self.summarize_paper(
                        paper.get('title', ''),
                        paper['abstract']
                    )
                    paper.update(summary_data)
                results.append(paper)
            except Exception as e:
                paper['summary_error'] = str(e)
                results.append(paper)

        return results
