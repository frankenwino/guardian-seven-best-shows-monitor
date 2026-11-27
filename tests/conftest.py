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
    """Sample weekly article dictionary."""
    return {
        "url": "https://www.theguardian.com/tv-and-radio/2026/may/29/seven-best-shows-to-stream",
        "title": "Seven best shows to stream this week",
        "date": "2026-05-29",
        "path": "/tv-and-radio/2026/may/29/seven-best-shows-to-stream",
        "body_html": "",
        "series_tag": "tv-and-radio/series/the-seven-best-shows-to-stream-this-week",
        "series_type": "weekly",
    }


@pytest.fixture
def sample_annual_tv_article():
    """Sample annual TV roundup article dictionary."""
    return {
        "url": "https://www.theguardian.com/tv-and-radio/2025/dec/31/best-tv-of-2025",
        "title": "The best TV of 2025",
        "date": "2025-12-31",
        "path": "tv-and-radio/2025/dec/31/best-tv-of-2025",
        "body_html": "",
        "series_tag": "tv-and-radio/series/2025-in-tv",
        "series_type": "annual_tv",
    }


@pytest.fixture
def sample_annual_film_article():
    """Sample annual film roundup article dictionary."""
    return {
        "url": "https://www.theguardian.com/film/2025/dec/19/best-films-of-2025",
        "title": "The 50 best films of 2025",
        "date": "2025-12-19",
        "path": "film/2025/dec/19/best-films-of-2025",
        "body_html": "",
        "series_tag": "film/series/best-films-of-2025",
        "series_type": "annual_film",
    }


@pytest.fixture
def sample_shows():
    """Sample list of show dictionaries."""
    return [
        {
            "title": "Test Show One",
            "platform": "Netflix",
            "description": "A great show about testing.",
            "pick_of_the_week": False,
        },
        {
            "title": "Test Show Two",
            "platform": "Disney+",
            "description": "Another excellent show.",
            "pick_of_the_week": False,
        },
    ]
