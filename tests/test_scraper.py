"""Unit tests for GuardianScraper."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from app.scraper import GuardianScraper

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def scraper():
    return GuardianScraper()


# ── Tag helpers ───────────────────────────────────────────────────────────────

class TestSeriesUrlToTag:
    def test_strips_base_url(self, scraper):
        url = "https://www.theguardian.com/film/series/best-films-of-2025"
        assert scraper._series_url_to_tag(url) == "film/series/best-films-of-2025"

    def test_strips_weekly_series_url(self, scraper):
        url = "https://www.theguardian.com/tv-and-radio/series/the-seven-best-shows-to-stream-this-week"
        assert scraper._series_url_to_tag(url) == "tv-and-radio/series/the-seven-best-shows-to-stream-this-week"

    def test_strips_annual_tv_url(self, scraper):
        url = "https://www.theguardian.com/tv-and-radio/series/2025-in-tv"
        assert scraper._series_url_to_tag(url) == "tv-and-radio/series/2025-in-tv"


class TestSeriesTypeFromTag:
    def test_weekly_classification(self, scraper):
        assert scraper._series_type_from_tag(
            "tv-and-radio/series/the-seven-best-shows-to-stream-this-week"
        ) == "weekly"

    def test_annual_tv_year_in_tv(self, scraper):
        assert scraper._series_type_from_tag("tv-and-radio/series/2025-in-tv") == "annual_tv"

    def test_annual_tv_best_tv_of_year(self, scraper):
        assert scraper._series_type_from_tag("tv-and-radio/series/best-tv-of-2016") == "annual_tv"

    def test_annual_film(self, scraper):
        assert scraper._series_type_from_tag("film/series/best-films-of-2025") == "annual_film"

    def test_annual_film_2026(self, scraper):
        assert scraper._series_type_from_tag("film/series/best-films-of-2026") == "annual_film"

    def test_other_tv_series_is_weekly(self, scraper):
        assert scraper._series_type_from_tag(
            "tv-and-radio/series/the-best-shows-to-stream-this-month"
        ) == "weekly"


# ── get_series_articles ───────────────────────────────────────────────────────

def _mock_api_response(articles: list) -> MagicMock:
    """Build a mock requests.Response for the Guardian API."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"response": {"results": articles}}
    return mock_resp


def _guardian_api_article(
    url: str = "https://www.theguardian.com/tv-and-radio/2026/may/29/seven-best-shows",
    title: str = "Seven best shows this week",
    body: str = "<p>Test body</p>",
    api_id: str = "tv-and-radio/2026/may/29/seven-best-shows",
) -> dict:
    return {
        "webUrl": url,
        "webTitle": title,
        "id": api_id,
        "fields": {"body": body},
    }


class TestGetSeriesArticles:
    def test_returns_articles_from_single_series(self):
        scraper = GuardianScraper(
            series_urls=[
                "https://www.theguardian.com/tv-and-radio/series/the-seven-best-shows-to-stream-this-week"
            ]
        )
        article = _guardian_api_article()
        with patch("requests.get", return_value=_mock_api_response([article])):
            with patch.dict("os.environ", {"GUARDIAN_API_KEY": "test-key"}):
                results = scraper.get_series_articles()

        assert len(results) == 1
        r = results[0]
        assert r["url"] == article["webUrl"]
        assert r["title"] == article["webTitle"]
        assert r["date"] == "2026-05-29"
        assert r["series_tag"] == "tv-and-radio/series/the-seven-best-shows-to-stream-this-week"
        assert r["series_type"] == "weekly"
        assert r["body_html"] == "<p>Test body</p>"

    def test_merges_articles_from_multiple_series(self):
        scraper = GuardianScraper(
            series_urls=[
                "https://www.theguardian.com/tv-and-radio/series/the-seven-best-shows-to-stream-this-week",
                "https://www.theguardian.com/tv-and-radio/series/2025-in-tv",
            ]
        )
        weekly_article = _guardian_api_article(
            url="https://www.theguardian.com/tv-and-radio/2026/may/29/seven-best-shows",
            title="Weekly shows",
        )
        annual_article = _guardian_api_article(
            url="https://www.theguardian.com/tv-and-radio/2025/dec/31/best-tv",
            title="Best TV 2025",
        )
        responses = [
            _mock_api_response([weekly_article]),
            _mock_api_response([annual_article]),
        ]
        with patch("requests.get", side_effect=responses):
            with patch.dict("os.environ", {"GUARDIAN_API_KEY": "test-key"}):
                results = scraper.get_series_articles()

        assert len(results) == 2
        types = {r["series_type"] for r in results}
        assert types == {"weekly", "annual_tv"}

    def test_annual_tv_articles_have_correct_series_type(self):
        scraper = GuardianScraper(
            series_urls=["https://www.theguardian.com/tv-and-radio/series/2025-in-tv"]
        )
        article = _guardian_api_article(
            url="https://www.theguardian.com/tv-and-radio/2025/dec/31/best-tv"
        )
        with patch("requests.get", return_value=_mock_api_response([article])):
            with patch.dict("os.environ", {"GUARDIAN_API_KEY": "test-key"}):
                results = scraper.get_series_articles()

        assert results[0]["series_type"] == "annual_tv"
        assert results[0]["series_tag"] == "tv-and-radio/series/2025-in-tv"

    def test_annual_film_articles_have_correct_series_type(self):
        scraper = GuardianScraper(
            series_urls=["https://www.theguardian.com/film/series/best-films-of-2025"]
        )
        article = _guardian_api_article(
            url="https://www.theguardian.com/film/2025/dec/19/best-films"
        )
        with patch("requests.get", return_value=_mock_api_response([article])):
            with patch.dict("os.environ", {"GUARDIAN_API_KEY": "test-key"}):
                results = scraper.get_series_articles()

        assert results[0]["series_type"] == "annual_film"
        assert results[0]["series_tag"] == "film/series/best-films-of-2025"

    def test_continues_if_one_series_fails(self):
        scraper = GuardianScraper(
            series_urls=[
                "https://www.theguardian.com/tv-and-radio/series/the-seven-best-shows-to-stream-this-week",
                "https://www.theguardian.com/tv-and-radio/series/2025-in-tv",
            ]
        )
        good_article = _guardian_api_article(
            url="https://www.theguardian.com/tv-and-radio/2025/dec/31/best-tv",
            title="Best TV 2025",
        )
        with patch(
            "requests.get",
            side_effect=[Exception("network error"), _mock_api_response([good_article])],
        ):
            with patch.dict("os.environ", {"GUARDIAN_API_KEY": "test-key"}):
                results = scraper.get_series_articles()

        assert len(results) == 1
        assert results[0]["title"] == "Best TV 2025"

    def test_missing_api_key_returns_empty(self):
        scraper = GuardianScraper()
        with patch.dict("os.environ", {}, clear=True):
            # Ensure GUARDIAN_API_KEY is absent
            import os
            os.environ.pop("GUARDIAN_API_KEY", None)
            results = scraper.get_series_articles()
        assert results == []

    def test_body_html_included_in_article(self):
        scraper = GuardianScraper(
            series_urls=[
                "https://www.theguardian.com/tv-and-radio/series/the-seven-best-shows-to-stream-this-week"
            ]
        )
        article = _guardian_api_article(body="<h2>Show Title</h2><p>Great show on Netflix.</p>")
        with patch("requests.get", return_value=_mock_api_response([article])):
            with patch.dict("os.environ", {"GUARDIAN_API_KEY": "test-key"}):
                results = scraper.get_series_articles()

        assert "<h2>Show Title</h2>" in results[0]["body_html"]

    def test_empty_api_response_returns_empty_list(self):
        scraper = GuardianScraper()
        with patch("requests.get", return_value=_mock_api_response([])):
            with patch.dict("os.environ", {"GUARDIAN_API_KEY": "test-key"}):
                results = scraper.get_series_articles()
        assert results == []


# ── Date extraction ───────────────────────────────────────────────────────────

class TestExtractDateFromUrl:
    def test_standard_url(self, scraper):
        assert scraper._extract_date_from_url(
            "/tv-and-radio/2026/may/29/seven-best-shows"
        ) == "2026-05-29"

    def test_january(self, scraper):
        assert scraper._extract_date_from_url(
            "/tv-and-radio/2025/jan/05/best-shows"
        ) == "2025-01-05"

    def test_no_date_returns_none(self, scraper):
        assert scraper._extract_date_from_url(
            "/tv-and-radio/series/the-seven-best-shows"
        ) is None


# ── Show parsing ──────────────────────────────────────────────────────────────

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

    def test_parse_from_body_html_avoids_http_request(self, scraper):
        html = (FIXTURES_DIR / "sample_article.html").read_text()
        with patch.object(scraper, "fetch_page") as mock_fetch:
            shows = scraper.parse_show_recommendations(
                "http://example.com/article", body_html=html
            )
        mock_fetch.assert_not_called()
        assert len(shows) == 3

    def test_returns_empty_on_fetch_failure(self, scraper):
        with patch.object(scraper, "fetch_page", return_value=None):
            shows = scraper.parse_show_recommendations("http://example.com/bad")
        assert shows == []


# ── Platform extraction ───────────────────────────────────────────────────────

class TestExtractPlatform:
    def test_netflix(self, scraper):
        assert scraper._extract_platform("Available on Netflix") == "Netflix"

    def test_disney_plus(self, scraper):
        assert scraper._extract_platform("Streaming on Disney+") == "Disney+"

    def test_bbc_iplayer(self, scraper):
        assert scraper._extract_platform("Watch on BBC iPlayer") == "BBC iPlayer"

    def test_no_platform(self, scraper):
        assert scraper._extract_platform("A great show") == "Platform not specified"
