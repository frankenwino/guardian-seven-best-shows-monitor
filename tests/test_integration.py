"""Integration tests that require network access. Run with: pytest -m integration"""

import pytest

from scraper import GuardianScraper


@pytest.mark.integration
class TestScraperIntegration:
    def test_get_series_articles_returns_results(self):
        scraper = GuardianScraper()
        articles = scraper.get_series_articles()
        assert len(articles) > 0
        assert "url" in articles[0]
        assert "title" in articles[0]
        assert "date" in articles[0]

    def test_parse_latest_article(self):
        scraper = GuardianScraper()
        articles = scraper.get_series_articles()
        assert articles, "No articles found"

        shows = scraper.parse_show_recommendations(articles[0]["url"])
        assert len(shows) > 0
        assert "title" in shows[0]
        assert "platform" in shows[0]
