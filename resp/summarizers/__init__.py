"""
Summarization module for RESP library.
Supports multiple model providers: OpenAI, OpenAI-compatible APIs, and local models.
"""

from resp.summarizers.base import BaseSummarizer
from resp.summarizers.openai_summarizer import OpenAISummarizer
from resp.summarizers.local_summarizer import LocalSummarizer

__all__ = ['BaseSummarizer', 'OpenAISummarizer', 'LocalSummarizer']
