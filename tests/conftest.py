"""Shared pytest fixtures for Guardian Seven Best Shows Monitor tests."""

import sys
from pathlib import Path

import pytest

# Add project root to path so tests can import the app package
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def storage(tmp_path):
    """Create a ShowDataStorage instance using a temporary directory."""
    from app.storage import ShowDataStorage

    return ShowDataStorage(data_dir=str(tmp_path))


@pytest.fixture
def sample_article():
    """Sample article dictionary."""
    return {
        "url": "https://www.theguardian.com/tv-and-radio/2026/may/29/seven-best-shows-to-stream",
        "title": "Seven best shows to stream this week",
        "date": "2026-05-29",
        "path": "/tv-and-radio/2026/may/29/seven-best-shows-to-stream",
    }


@pytest.fixture
def sample_shows():
    """Sample list of show dictionaries."""
    return [
        {
            "title": "Test Show One",
            "platform": "Netflix",
            "description": "A great show about testing.",
        },
        {
            "title": "Test Show Two",
            "platform": "Disney+",
            "description": "Another excellent show.",
        },
    ]
