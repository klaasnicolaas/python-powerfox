"""Asynchronous Python client for Powerfox."""

from pathlib import Path


def load_fixtures(filename: str) -> str:
    """Load a fixture."""
    path = Path(__file__).parent / "fixtures" / filename
    return path.read_text()
