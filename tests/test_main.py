"""Unit tests for GuardianMonitor orchestration logic."""

from unittest.mock import MagicMock, patch, call
import pytest


def _make_monitor():
    """Create a GuardianMonitor with all external dependencies mocked."""
    with patch("app.main.config") as mock_config, \
         patch("app.main.GuardianScraper") as mock_scraper_cls, \
         patch("app.main.ShowDataStorage") as mock_storage_cls, \
         patch("app.main.GuardianDiscordBot") as mock_discord_cls, \
         patch("app.main.QBittorrentRulesManager") as mock_qbt_cls, \
         patch("app.main.QBITTORRENT_AVAILABLE", True):

        mock_config.setup_logging.return_value = None
        mock_config.get_summary.return_value = {}
        mock_config.guardian_series_urls = ["https://www.theguardian.com/tv-and-radio/series/the-seven-best-shows-to-stream-this-week"]
        mock_config.request_timeout = 10
        mock_config.user_agent = "test-agent"
        mock_config.retry_attempts = 3
        mock_config.retry_delay = 5
        mock_config.get_data_directory_path.return_value = "/tmp/test-data"
        mock_config.is_discord_configured.return_value = True
        mock_config.send_error_notifications = False

        from app.main import GuardianMonitor
        monitor = GuardianMonitor()

        # Replace component instances with fresh mocks for inspection
        monitor.scraper = MagicMock()
        monitor.storage = MagicMock()
        monitor.discord_bot = MagicMock()
        monitor.qbt_manager = MagicMock()

        return monitor


@pytest.fixture
def monitor():
    return _make_monitor()


@pytest.fixture
def weekly_article():
    return {
        "url": "https://www.theguardian.com/tv-and-radio/2026/may/29/seven-best-shows",
        "title": "Seven best shows this week",
        "date": "2026-05-29",
        "path": "tv-and-radio/2026/may/29/seven-best-shows",
        "body_html": "",
        "series_tag": "tv-and-radio/series/the-seven-best-shows-to-stream-this-week",
        "series_type": "weekly",
    }


@pytest.fixture
def annual_tv_article():
    return {
        "url": "https://www.theguardian.com/tv-and-radio/2025/dec/31/best-tv-2025",
        "title": "Best TV of 2025",
        "date": "2025-12-31",
        "path": "tv-and-radio/2025/dec/31/best-tv-2025",
        "body_html": "",
        "series_tag": "tv-and-radio/series/2025-in-tv",
        "series_type": "annual_tv",
    }


@pytest.fixture
def annual_film_article():
    return {
        "url": "https://www.theguardian.com/film/2025/dec/19/best-films-2025",
        "title": "Best Films of 2025",
        "date": "2025-12-19",
        "path": "film/2025/dec/19/best-films-2025",
        "body_html": "",
        "series_tag": "film/series/best-films-of-2025",
        "series_type": "annual_film",
    }


@pytest.fixture
def sample_shows():
    return [
        {"title": "Show One", "platform": "Netflix", "description": "Great.", "pick_of_the_week": False},
        {"title": "Show Two", "platform": "Disney+", "description": "Fun.", "pick_of_the_week": False},
    ]


# ── _send_discord_notifications ───────────────────────────────────────────────

class TestSendDiscordNotifications:
    def test_weekly_calls_send_new_shows_alert(self, monitor, weekly_article, sample_shows):
        monitor.discord_bot.send_new_shows_alert.return_value = True

        result = monitor._send_discord_notifications(weekly_article, sample_shows)

        assert result is True
        monitor.discord_bot.send_new_shows_alert.assert_called_once_with(
            weekly_article["title"],
            weekly_article["date"],
            weekly_article["url"],
            sample_shows,
        )
        monitor.discord_bot.send_annual_roundup_alert.assert_not_called()

    def test_annual_tv_calls_send_annual_roundup_alert(self, monitor, annual_tv_article, sample_shows):
        monitor.discord_bot.send_annual_roundup_alert.return_value = True

        result = monitor._send_discord_notifications(annual_tv_article, sample_shows)

        assert result is True
        monitor.discord_bot.send_annual_roundup_alert.assert_called_once_with(
            annual_tv_article["title"],
            annual_tv_article["date"],
            annual_tv_article["url"],
            sample_shows,
            "annual_tv",
        )
        monitor.discord_bot.send_new_shows_alert.assert_not_called()

    def test_annual_film_calls_send_annual_roundup_alert(self, monitor, annual_film_article, sample_shows):
        monitor.discord_bot.send_annual_roundup_alert.return_value = True

        result = monitor._send_discord_notifications(annual_film_article, sample_shows)

        assert result is True
        monitor.discord_bot.send_annual_roundup_alert.assert_called_once_with(
            annual_film_article["title"],
            annual_film_article["date"],
            annual_film_article["url"],
            sample_shows,
            "annual_film",
        )
        monitor.discord_bot.send_new_shows_alert.assert_not_called()

    def test_missing_series_type_defaults_to_weekly(self, monitor, sample_shows):
        article_no_type = {
            "url": "https://example.com/article",
            "title": "Some article",
            "date": "2026-01-01",
        }
        monitor.discord_bot.send_new_shows_alert.return_value = True

        monitor._send_discord_notifications(article_no_type, sample_shows)

        monitor.discord_bot.send_new_shows_alert.assert_called_once()
        monitor.discord_bot.send_annual_roundup_alert.assert_not_called()


# ── _manage_qbittorrent_rules ─────────────────────────────────────────────────

class TestManageQbittorrentRules:
    def test_film_series_skips_qbittorrent(self, monitor, sample_shows):
        monitor._manage_qbittorrent_rules(sample_shows, series_type="annual_film")

        monitor.qbt_manager.load_rules.assert_not_called()

    def test_weekly_series_creates_rules(self, monitor, sample_shows):
        monitor.qbt_manager.load_rules.return_value = {}
        monitor.qbt_manager.check_existing_rules.return_value = []
        monitor.qbt_manager.is_qbittorrent_running.return_value = False
        monitor.qbt_manager.backup_rules.return_value = "/tmp/backup.json.gz"
        monitor.qbt_manager.create_rule_template.return_value = {"enabled": True}

        monitor._manage_qbittorrent_rules(sample_shows, series_type="weekly")

        monitor.qbt_manager.load_rules.assert_called_once()
        assert monitor.qbt_manager.create_rule_template.call_count == len(sample_shows)

    def test_annual_tv_creates_rules(self, monitor, sample_shows):
        monitor.qbt_manager.load_rules.return_value = {}
        monitor.qbt_manager.check_existing_rules.return_value = []
        monitor.qbt_manager.is_qbittorrent_running.return_value = False
        monitor.qbt_manager.backup_rules.return_value = "/tmp/backup.json.gz"
        monitor.qbt_manager.create_rule_template.return_value = {"enabled": True}

        monitor._manage_qbittorrent_rules(sample_shows, series_type="annual_tv")

        monitor.qbt_manager.load_rules.assert_called_once()
        assert monitor.qbt_manager.create_rule_template.call_count == len(sample_shows)

    def test_default_series_type_is_weekly(self, monitor, sample_shows):
        monitor.qbt_manager.load_rules.return_value = {}
        monitor.qbt_manager.check_existing_rules.return_value = []
        monitor.qbt_manager.is_qbittorrent_running.return_value = False
        monitor.qbt_manager.backup_rules.return_value = "/tmp/backup.json.gz"
        monitor.qbt_manager.create_rule_template.return_value = {"enabled": True}

        # No series_type arg — should default to weekly and proceed normally
        monitor._manage_qbittorrent_rules(sample_shows)

        monitor.qbt_manager.load_rules.assert_called_once()
