"""
Personalization module for RESP library.
Enables personalized paper discovery through LLM-based relevance scoring.
"""

from resp.personalization.profile import ResearchProfile
from resp.personalization.scorer import RelevanceScorer

__all__ = ['ResearchProfile', 'RelevanceScorer']
