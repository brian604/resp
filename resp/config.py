"""
Configuration management for RESP library.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """
    Configuration manager for RESP library.
    Handles API keys, model settings, and other configurations.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to JSON configuration file
        """
        self.config_file = config_file or os.path.join(
            str(Path.home()), '.resp', 'config.json'
        )
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                return self._default_config()
        return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'api_keys': {
                'serp_api': os.getenv('SERP_API_KEY', ''),
                'openai': os.getenv('OPENAI_API_KEY', ''),
            },
            'summarizer': {
                'provider': 'openai',  # 'openai', 'local'
                'openai': {
                    'model': 'gpt-3.5-turbo',
                    'base_url': None,  # For OpenAI-compatible APIs
                    'temperature': 0.3,
                    'max_tokens': 500,
                },
                'local': {
                    'model_type': 'transformers',
                    'model_name': 'facebook/bart-large-cnn',
                    'device': 'cpu',
                    'max_length': 150,
                }
            }
        }

    def save_config(self):
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key path (e.g., 'api_keys.openai').

        Args:
            key: Dot-separated key path
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value by key path.

        Args:
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a service.

        Args:
            service: Service name (e.g., 'serp_api', 'openai')

        Returns:
            API key or None
        """
        # Try config file first
        key = self.get(f'api_keys.{service}')
        if key:
            return key

        # Try environment variable
        env_var = f"{service.upper()}_API_KEY"
        return os.getenv(env_var)

    def set_api_key(self, service: str, api_key: str):
        """
        Set API key for a service.

        Args:
            service: Service name
            api_key: API key value
        """
        self.set(f'api_keys.{service}', api_key)
        self.save_config()

    def get_summarizer_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summarizer configuration.

        Args:
            provider: Provider name ('openai' or 'local'), uses default if None

        Returns:
            Provider configuration
        """
        if provider is None:
            provider = self.get('summarizer.provider', 'openai')

        return self.get(f'summarizer.{provider}', {})
