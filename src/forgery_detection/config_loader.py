"""Configuration loader for forgery detection system."""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigLoader:
    """Loads and provides access to configuration from config.yml."""

    _instance: Optional["ConfigLoader"] = None
    _config: Optional[Dict[str, Any]] = None
    _config_path: Optional[str] = None

    def __new__(cls, config_path: Optional[str] = None):
        """Singleton pattern to load config only once."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config_path = config_path
            cls._instance._load_config()
        return cls._instance

    def _get_project_root(self) -> Path:
        """Get the project root directory."""
        current_file = Path(__file__)
        return current_file.parent.parent.parent

    def _load_config(self) -> None:
        """Load configuration from config.yml."""
        config_path: Optional[Path] = None

        if self._config_path:
            # Try custom config path as-is first
            config_path = Path(self._config_path)

            if not config_path.exists():
                # Try relative to project root
                project_root = self._get_project_root()
                config_path_from_root = project_root / self._config_path

                if config_path_from_root.exists():
                    config_path = config_path_from_root
                else:
                    raise FileNotFoundError(
                        f"Config file not found at '{self._config_path}' or '{config_path_from_root}'. "
                        f"Please ensure the config file exists."
                    )
        else:
            # Use default config.yml in project root
            project_root = self._get_project_root()
            config_path = project_root / "config.yml"

            if not config_path.exists():
                raise FileNotFoundError(
                    f"Default config.yml not found at {config_path}. "
                    f"Please ensure config.yml exists in project root."
                )

        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path.

        Args:
            key_path: Dot-separated path (e.g., "metadata_detector.no_exif_score")
            default: Default value if key not found

        Returns:
            Configuration value or default

        Examples:
            >>> config = ConfigLoader()
            >>> config.get("classifier.modes.strict.threshold")
            0.7
            >>> config.get("metadata_detector.no_exif_score")
            0.4
        """
        keys = key_path.split(".")
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_dict(self, key_path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get configuration dictionary by path."""
        result = self.get(key_path, default)
        return result if isinstance(result, dict) else (default or {})

    def get_list(self, key_path: str, default: Optional[list] = None) -> list:
        """Get configuration list by path."""
        result = self.get(key_path, default)
        return result if isinstance(result, list) else (default or [])

    def get_float(self, key_path: str, default: float = 0.0) -> float:
        """Get configuration float value by path."""
        result = self.get(key_path, default)
        return float(result) if result is not None else default

    def get_int(self, key_path: str, default: int = 0) -> int:
        """Get configuration integer value by path."""
        result = self.get(key_path, default)
        return int(result) if result is not None else default

    def get_bool(self, key_path: str, default: bool = False) -> bool:
        """Get configuration boolean value by path."""
        result = self.get(key_path, default)
        return bool(result) if result is not None else default


# Global config instance
_config: Optional[ConfigLoader] = None


def get_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Get global configuration instance.

    Args:
        config_path: Optional path to custom config file. Only used on first call.

    Returns:
        ConfigLoader singleton instance
    """
    global _config
    if _config is None:
        _config = ConfigLoader(config_path)
    return _config
