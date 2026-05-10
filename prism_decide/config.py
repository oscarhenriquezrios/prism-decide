"""Configuration loader for Prism-Decide."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "prism-decide" / "config.yaml"

DEFAULT_CONFIG = {
    "provider": {
        "default": "openai",
        "openai": {
            "model": "gpt-4o-mini",
            "api_key": "${OPENAI_API_KEY}",
        },
        "anthropic": {
            "model": "claude-sonnet-4-20250514",
            "api_key": "${ANTHROPIC_API_KEY}",
        },
    },
    "behavior": {
        "parallel_agents": True,
        "show_reasoning": True,
        "color_theme": "default",
    },
}


def load_config(path: str | None = None) -> dict:
    """Load config from YAML file, falling back to defaults."""
    config = DEFAULT_CONFIG.copy()

    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if config_path.exists():
        with open(config_path) as f:
            user_config = yaml.safe_load(f) or {}
            _deep_merge(config, user_config)

    # Resolve environment variables
    _resolve_env_vars(config)

    return config


def _resolve_env_vars(obj):
    """Recursively resolve ${VAR} patterns in config values."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = _resolve_env_vars(v)
        return obj
    elif isinstance(obj, str):
        import re
        def replace_var(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))
        return re.sub(r"\$\{(\w+)\}", replace_var, obj)
    return obj


def _deep_merge(base: dict, override: dict):
    """Deep merge override into base."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
