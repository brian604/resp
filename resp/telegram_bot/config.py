"""
Configuration management for RESP Telegram bot.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class BotConfig:
    """
    Configuration for RESP Telegram bot.

    Attributes:
        bot_token: Telegram bot token from @BotFather
        data_dir: Directory for storing user data and profiles
        default_digest_time: Default time for scheduled digests (HH:MM)
        default_threshold: Default relevance threshold for papers
        max_papers_per_digest: Maximum papers to include in digest
        enable_web_preview: Enable link previews in messages
    """

    bot_token: str
    data_dir: str = "~/.resp/telegram"
    default_digest_time: str = "08:00"
    default_threshold: float = 6.5
    max_papers_per_digest: int = 10
    enable_web_preview: bool = False

    def __post_init__(self):
        """Validate and expand paths."""
        self.data_dir = os.path.expanduser(self.data_dir)
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

        # Validate time format
        try:
            hours, minutes = map(int, self.default_digest_time.split(':'))
            if not (0 <= hours < 24 and 0 <= minutes < 60):
                raise ValueError
        except (ValueError, AttributeError):
            raise ValueError(
                f"Invalid time format: {self.default_digest_time}. "
                "Expected HH:MM (24-hour format)"
            )

    @classmethod
    def from_env(cls) -> 'BotConfig':
        """
        Create configuration from environment variables.

        Environment variables:
            TELEGRAM_BOT_TOKEN: Bot token (required)
            RESP_BOT_DATA_DIR: Data directory
            RESP_BOT_DIGEST_TIME: Default digest time
            RESP_BOT_THRESHOLD: Default relevance threshold
            RESP_BOT_MAX_PAPERS: Max papers per digest

        Returns:
            BotConfig instance
        """
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN environment variable required. "
                "Get your token from @BotFather on Telegram."
            )

        return cls(
            bot_token=token,
            data_dir=os.getenv('RESP_BOT_DATA_DIR', '~/.resp/telegram'),
            default_digest_time=os.getenv('RESP_BOT_DIGEST_TIME', '08:00'),
            default_threshold=float(os.getenv('RESP_BOT_THRESHOLD', '6.5')),
            max_papers_per_digest=int(os.getenv('RESP_BOT_MAX_PAPERS', '10')),
            enable_web_preview=os.getenv('RESP_BOT_WEB_PREVIEW', 'false').lower() == 'true'
        )

    @classmethod
    def from_file(cls, file_path: str) -> 'BotConfig':
        """
        Load configuration from JSON file.

        Args:
            file_path: Path to JSON config file

        Returns:
            BotConfig instance
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls(**data)

    def to_file(self, file_path: str):
        """
        Save configuration to JSON file.

        Args:
            file_path: Path to save config
        """
        with open(file_path, 'w') as f:
            json.dump(asdict(self), f, indent=2)

    def get_user_dir(self, user_id: int) -> Path:
        """
        Get data directory for specific user.

        Args:
            user_id: Telegram user ID

        Returns:
            Path to user's data directory
        """
        user_dir = Path(self.data_dir) / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def get_user_profile_path(self, user_id: int) -> Path:
        """
        Get path to user's research profile.

        Args:
            user_id: Telegram user ID

        Returns:
            Path to profile YAML file
        """
        return self.get_user_dir(user_id) / 'profile.yaml'

    def get_user_settings_path(self, user_id: int) -> Path:
        """
        Get path to user's bot settings.

        Args:
            user_id: Telegram user ID

        Returns:
            Path to settings JSON file
        """
        return self.get_user_dir(user_id) / 'settings.json'
