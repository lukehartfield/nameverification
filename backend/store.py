"""State holder for the latest generated target name."""

from typing import Optional


_latest_target_name: Optional[str] = None


def get_latest_target_name() -> Optional[str]:
    """Return the latest generated target name string."""
    return _latest_target_name


def set_latest_target_name(name: str) -> str:
    """Persist and return the latest generated target name string."""
    global _latest_target_name
    _latest_target_name = name
    return _latest_target_name


def clear_latest_target_name() -> None:
    """Reset stored state for tests or fresh app startup."""
    global _latest_target_name
    _latest_target_name = None
