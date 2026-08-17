"""Unit tests for GuardianScraper parsing logic."""

from pathlib import Path
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from app.scraper import GuardianScraper

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def scraper():
    return GuardianScraper()


class TestIsSevenBestShowsArticle:
    def test_valid_url(self, scraper):
        url = "/tv-and-radio/2026/may/29/seven-best-shows-to-stream-this-week"
        assert scraper._is_seven_best_shows_article(url) is True

    def test_valid_url_alternate_format(self, scraper):
        url = "/tv-and-radio/2026/jan/10/best-shows-to-stream-this-week-netflix"
        assert scraper._is_seven_best_shows_article(url) is True

    def test_series_index_page_rejected(self, scraper):
        url = "/tv-and-radio/series/the-seven-best-shows-to-stream-this-week"
        assert scraper._is_seven_best_shows_article(url) is False

    def test_unrelated_url_rejected(self, scraper):
        url = "/tv-and-radio/2026/may/29/some-other-article"
        assert scraper._is_seven_best_shows_article(url) is False

    def test_empty_url_rejected(self, scraper):
        assert scraper._is_seven_best_shows_article("") is False

    def test_none_rejected(self, scraper):
        assert scraper._is_seven_best_shows_article(None) is False

    def test_films_url_rejected(self, scraper):
        url = "/tv-and-radio/2026/may/29/best-films-to-watch-on-tv-this-week"
        assert scraper._is_seven_best_shows_article(url) is False

    def test_films_url_alternate_rejected(self, scraper):
        url = "/tv-and-radio/2026/jan/10/seven-best-films-to-watch"
        assert scraper._is_seven_best_shows_article(url) is False

    def test_real_films_article_rejected(self, scraper):
        url = (
            "/tv-and-radio/2026/aug/14/the-beast-to-novak-djokovic-the-wolf-in-winter-"
            "the-seven-best-films-to-watch-on-tv-this-week"
        )
        assert scraper._is_seven_best_shows_article(url) is False

    def test_real_shows_article_accepted(self, scraper):
        url = (
            "/tv-and-radio/2026/aug/14/lanterns-to-a-beautiful-obsession-"
            "the-seven-best-shows-to-stream-this-week"
        )
        assert scraper._is_seven_best_shows_article(url) is True

    def test_film_section_url_rejected(self, scraper):
        url = "/film/2026/aug/14/the-seven-best-shows-to-stream-this-week"
        assert scraper._is_seven_best_shows_article(url) is False


class TestExcludedSeriesUrls:
    def test_films_series_url_not_fetched(self):
        scraper = GuardianScraper(
            series_urls=[
                "https://www.theguardian.com/tv-and-radio/series/the-seven-best-films-to-watch-on-tv-this-week"
            ]
        )
        with patch.object(scraper, "fetch_page") as mock_fetch:
            assert scraper.get_series_articles() == []
            mock_fetch.assert_not_called()


class TestExtractDateFromUrl:
    def test_standard_url(self, scraper):
        url = "/tv-and-radio/2026/may/29/seven-best-shows"
        assert scraper._extract_date_from_url(url) == "2026-05-29"

    def test_january(self, scraper):
        url = "/tv-and-radio/2025/jan/05/best-shows"
        assert scraper._extract_date_from_url(url) == "2025-01-05"

    def test_no_date_returns_none(self, scraper):
        url = "/tv-and-radio/series/the-seven-best-shows"
        assert scraper._extract_date_from_url(url) is None


class TestParseShowRecommendations:
    def test_parse_from_h2_headings(self, scraper):
        html = (FIXTURES_DIR / "sample_article.html").read_text()
        soup = BeautifulSoup(html, "html.parser")

        with patch.object(scraper, "fetch_page", return_value=soup):
            shows = scraper.parse_show_recommendations("http://example.com/article")

        assert len(shows) == 3
        assert shows[0]["title"] == "Hostage"
        assert shows[0]["pick_of_the_week"] is True
        assert shows[0]["platform"] == "Netflix"
        assert shows[1]["title"] == "Long Story Short"
        assert shows[1]["pick_of_the_week"] is False

    def test_returns_empty_on_fetch_failure(self, scraper):
        with patch.object(scraper, "fetch_page", return_value=None):
            shows = scraper.parse_show_recommendations("http://example.com/bad")

        assert shows == []


class TestExtractPlatform:
    def test_netflix(self, scraper):
        assert scraper._extract_platform("Available on Netflix") == "Netflix"

    def test_disney_plus(self, scraper):
        assert scraper._extract_platform("Streaming on Disney+") == "Disney+"

    def test_bbc_iplayer(self, scraper):
        assert scraper._extract_platform("Watch on BBC iPlayer") == "BBC iPlayer"

    def test_no_platform(self, scraper):
        assert scraper._extract_platform("A great show") == "Platform not specified"
