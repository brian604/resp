"""
Research profile management for personalized paper discovery.
"""

import os
import json
import yaml
from typing import List, Dict, Optional, Any
from pathlib import Path


class ResearchProfile:
    """
    Represents a user's research interests for personalized paper ranking.

    A profile contains:
    - Basic info (name, email)
    - ArXiv categories of interest
    - Primary research interests (natural language)
    - Secondary interests (nice to have)
    - Exclusions (topics to avoid)
    - Scoring preferences
    """

    def __init__(
        self,
        name: str = "Default Profile",
        email: Optional[str] = None,
        arxiv_subjects: Optional[List[str]] = None,
        arxiv_categories: Optional[List[str]] = None,
        primary_interests: Optional[List[str]] = None,
        secondary_interests: Optional[List[str]] = None,
        exclusions: Optional[List[str]] = None,
        scoring_config: Optional[Dict[str, Any]] = None,
        digest_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a research profile.

        Args:
            name: Profile name
            email: User email for digest delivery
            arxiv_subjects: Broad subjects (e.g., ["cs", "math"])
            arxiv_categories: Specific categories (e.g., ["cs.AI", "cs.LG"])
            primary_interests: Primary research interests (natural language)
            secondary_interests: Secondary interests
            exclusions: Topics to avoid
            scoring_config: LLM scoring configuration
            digest_config: Digest generation preferences
        """
        self.name = name
        self.email = email
        self.arxiv_subjects = arxiv_subjects or []
        self.arxiv_categories = arxiv_categories or []
        self.primary_interests = primary_interests or []
        self.secondary_interests = secondary_interests or []
        self.exclusions = exclusions or []

        # Default scoring configuration
        self.scoring_config = scoring_config or {
            'model': 'gpt-3.5-turbo',
            'threshold': 6.0,
            'max_papers': 50,
            'batch_size': 10,
            'temperature': 0.3
        }

        # Default digest configuration
        self.digest_config = digest_config or {
            'format': 'html',
            'template': 'modern',
            'frequency': 'daily',
            'time': '08:00 UTC'
        }

    @classmethod
    def from_yaml(cls, file_path: str) -> 'ResearchProfile':
        """
        Load profile from YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            ResearchProfile instance
        """
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)

    @classmethod
    def from_json(cls, file_path: str) -> 'ResearchProfile':
        """
        Load profile from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            ResearchProfile instance
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchProfile':
        """
        Create profile from dictionary.

        Args:
            data: Dictionary with profile data

        Returns:
            ResearchProfile instance
        """
        profile_data = data.get('profile', {})
        arxiv_data = data.get('arxiv', {})
        interests_data = data.get('interests', {})

        return cls(
            name=profile_data.get('name', 'Default Profile'),
            email=profile_data.get('email'),
            arxiv_subjects=arxiv_data.get('subjects', []),
            arxiv_categories=arxiv_data.get('categories', []),
            primary_interests=interests_data.get('primary', []),
            secondary_interests=interests_data.get('secondary', []),
            exclusions=interests_data.get('exclusions', []),
            scoring_config=data.get('scoring'),
            digest_config=data.get('digest')
        )

    @classmethod
    def from_template(cls, template_name: str) -> 'ResearchProfile':
        """
        Load profile from built-in template.

        Args:
            template_name: Name of template (ml, nlp, cv, etc.)

        Returns:
            ResearchProfile instance
        """
        templates_dir = Path(__file__).parent / 'templates'
        template_file = templates_dir / f'{template_name}.yaml'

        if not template_file.exists():
            raise ValueError(f"Template '{template_name}' not found")

        return cls.from_yaml(str(template_file))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert profile to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'profile': {
                'name': self.name,
                'email': self.email
            },
            'arxiv': {
                'subjects': self.arxiv_subjects,
                'categories': self.arxiv_categories
            },
            'interests': {
                'primary': self.primary_interests,
                'secondary': self.secondary_interests,
                'exclusions': self.exclusions
            },
            'scoring': self.scoring_config,
            'digest': self.digest_config
        }

    def to_yaml(self, file_path: str):
        """
        Save profile to YAML file.

        Args:
            file_path: Path to save YAML file
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    def to_json(self, file_path: str):
        """
        Save profile to JSON file.

        Args:
            file_path: Path to save JSON file
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def get_interest_description(self) -> str:
        """
        Get formatted description of research interests for LLM prompts.

        Returns:
            Formatted interest description
        """
        parts = []

        if self.primary_interests:
            parts.append("PRIMARY INTERESTS:")
            for interest in self.primary_interests:
                parts.append(f"- {interest}")

        if self.secondary_interests:
            parts.append("\nSECONDARY INTERESTS:")
            for interest in self.secondary_interests:
                parts.append(f"- {interest}")

        if self.exclusions:
            parts.append("\nNOT INTERESTED IN:")
            for exclusion in self.exclusions:
                parts.append(f"- {exclusion}")

        return "\n".join(parts)

    def validate(self) -> List[str]:
        """
        Validate profile configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.name:
            errors.append("Profile name is required")

        if not self.primary_interests:
            errors.append("At least one primary interest is required")

        if not self.arxiv_categories and not self.arxiv_subjects:
            errors.append("At least one arXiv category or subject is required")

        # Validate arXiv categories format
        for cat in self.arxiv_categories:
            if '.' not in cat:
                errors.append(f"Invalid arXiv category format: {cat} (should be like 'cs.AI')")

        # Validate scoring config
        if 'threshold' in self.scoring_config:
            threshold = self.scoring_config['threshold']
            if not 0 <= threshold <= 10:
                errors.append(f"Scoring threshold must be between 0 and 10, got {threshold}")

        return errors

    def __repr__(self) -> str:
        """String representation of profile."""
        return (
            f"ResearchProfile(name='{self.name}', "
            f"categories={len(self.arxiv_categories)}, "
            f"interests={len(self.primary_interests)})"
        )

    def __str__(self) -> str:
        """Human-readable profile description."""
        lines = [
            f"Research Profile: {self.name}",
            f"Email: {self.email or 'Not set'}",
            f"\nArXiv Categories: {', '.join(self.arxiv_categories) if self.arxiv_categories else 'All'}",
            f"\nPrimary Interests ({len(self.primary_interests)}):"
        ]

        for interest in self.primary_interests:
            lines.append(f"  - {interest}")

        if self.secondary_interests:
            lines.append(f"\nSecondary Interests ({len(self.secondary_interests)}):")
            for interest in self.secondary_interests:
                lines.append(f"  - {interest}")

        if self.exclusions:
            lines.append(f"\nExclusions ({len(self.exclusions)}):")
            for exclusion in self.exclusions:
                lines.append(f"  - {exclusion}")

        return "\n".join(lines)
