"""
OpenAI-based summarizer supporting OpenAI and OpenAI-compatible APIs.
"""

import os
from typing import Dict, Optional
from resp.summarizers.base import BaseSummarizer

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAISummarizer(BaseSummarizer):
    """
    Summarizer using OpenAI API or OpenAI-compatible APIs (e.g., DeepSeek, Groq, etc.).

    Supports custom base URLs for compatible services.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.3,
        max_tokens: int = 500,
        **kwargs
    ):
        """
        Initialize OpenAI summarizer.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: Custom API base URL for OpenAI-compatible services
                     (e.g., "https://api.deepseek.com/v1" for DeepSeek)
            model: Model name (e.g., "gpt-3.5-turbo", "gpt-4", "deepseek-chat")
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
        """
        super().__init__(**kwargs)

        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        # Initialize client with optional custom base URL
        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def summarize(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Generate a summary of the input text.

        Args:
            text: The text to summarize
            max_length: Maximum length (overrides default max_tokens if provided)

        Returns:
            The generated summary
        """
        max_tokens = max_length if max_length else self.max_tokens

        prompt = f"""Summarize the following research paper abstract concisely and clearly:

{text}

Provide a clear summary focusing on the main contribution and key findings."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes research papers concisely and accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

    def summarize_paper(self, title: str, abstract: str) -> Dict[str, str]:
        """
        Generate a structured summary of a research paper.

        Args:
            title: Paper title
            abstract: Paper abstract

        Returns:
            Dictionary containing summary, key_points, and tldr
        """
        prompt = f"""Analyze this research paper and provide a structured summary:

Title: {title}

Abstract: {abstract}

Please provide:
1. A concise summary (2-3 sentences)
2. Key points/contributions (bullet points)
3. A one-line TL;DR

Format your response as:
SUMMARY:
[your summary]

KEY POINTS:
- [point 1]
- [point 2]
- [point 3]

TLDR:
[one line summary]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing research papers and extracting key information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            content = response.choices[0].message.content.strip()

            # Parse the structured response
            result = {
                'summary': '',
                'key_points': '',
                'tldr': ''
            }

            sections = content.split('\n\n')
            current_section = None

            for section in sections:
                if section.startswith('SUMMARY:'):
                    result['summary'] = section.replace('SUMMARY:', '').strip()
                elif section.startswith('KEY POINTS:'):
                    result['key_points'] = section.replace('KEY POINTS:', '').strip()
                elif section.startswith('TLDR:'):
                    result['tldr'] = section.replace('TLDR:', '').strip()
                elif current_section:
                    result[current_section] += '\n' + section

            return result

        except Exception as e:
            return {
                'summary': f"Error generating summary: {str(e)}",
                'key_points': '',
                'tldr': ''
            }
