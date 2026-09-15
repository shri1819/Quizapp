"""
Settings Manager for QuizMaster.
Handles persistent JSON configuration for themes, sound, defaults, and UI preferences.
"""

import json
import os
from typing import Any, Dict

DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "Dark",
    "sound_effects": True,
    "default_timer": 30,
    "shuffle_questions": True,
    "shuffle_answers": True,
    "ui_scale": "Normal",
    "player_name": "Player"
}


class SettingsManager:
    """Manages application settings persistence and default fallbacks."""

    def __init__(self, file_path: str = None):
        if file_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "settings.json")
        self.file_path = file_path
        self.settings: Dict[str, Any] = dict(DEFAULT_SETTINGS)
        self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file or create defaults if missing."""
        if not os.path.exists(self.file_path):
            self.settings = dict(DEFAULT_SETTINGS)
            self.save_settings()
            return self.settings

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    # Merge with default settings to cover any newly added keys
                    for key, val in DEFAULT_SETTINGS.items():
                        if key not in loaded:
                            loaded[key] = val
                    self.settings = loaded
                else:
                    self.settings = dict(DEFAULT_SETTINGS)
        except Exception:
            self.settings = dict(DEFAULT_SETTINGS)
            self.save_settings()

        return self.settings

    def save_settings(self) -> bool:
        """Persist current settings to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting value."""
        return self.settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value: Any) -> bool:
        """Update a setting value and persist."""
        self.settings[key] = value
        return self.save_settings()

    def reset_to_defaults(self) -> bool:
        """Reset all settings to initial defaults."""
        self.settings = dict(DEFAULT_SETTINGS)
        return self.save_settings()
