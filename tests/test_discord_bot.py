"""Unit tests for GuardianDiscordBot."""

from unittest.mock import MagicMock, patch, call
import pytest

from app.discord_bot import GuardianDiscordBot


@pytest.fixture
def bot():
    """GuardianDiscordBot with a test webhook URL."""
    with patch("app.discord_bot.load_dotenv"):
        with patch.dict("os.environ", {"DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/test/token"}):
            return GuardianDiscordBot()


@pytest.fixture
def bot_no_webhook():
    """GuardianDiscordBot with no webhook URL configured."""
    with patch("app.discord_bot.load_dotenv"):
        with patch.dict("os.environ", {}, clear=True):
            import os
            os.environ.pop("DISCORD_WEBHOOK_URL", None)
            return GuardianDiscordBot()


@pytest.fixture
def sample_shows():
    return [
        {"title": "Show One", "platform": "Netflix", "description": "A great drama.", "pick_of_the_week": True},
        {"title": "Show Two", "platform": "Disney+", "description": "A fun comedy.", "pick_of_the_week": False},
    ]


def _mock_webhook_execute(status_code: int = 200) -> MagicMock:
    """Return a mock DiscordWebhook whose execute() returns the given status code."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_webhook = MagicMock()
    mock_webhook.execute.return_value = mock_response
    return mock_webhook


class TestSendAnnualRoundupAlert:
    def test_annual_tv_uses_correct_title(self, bot, sample_shows):
        embeds_seen = []

        def capture_add_embed(embed):
            embeds_seen.append(embed)

        mock_webhook = _mock_webhook_execute(200)
        mock_webhook.add_embed.side_effect = capture_add_embed

        with patch("app.discord_bot.DiscordWebhook", return_value=mock_webhook):
            result = bot.send_annual_roundup_alert(
                "Best TV 2025", "2025-12-31",
                "https://example.com/best-tv", sample_shows, "annual_tv"
            )

        assert result is True
        embed = embeds_seen[0]
        assert embed.title == "📺 Guardian Best TV of the Year"
        assert embed.color == 0x005689

    def test_annual_film_uses_correct_title_and_colour(self, bot, sample_shows):
        embeds_seen = []

        def capture_add_embed(embed):
            embeds_seen.append(embed)

        mock_webhook = _mock_webhook_execute(200)
        mock_webhook.add_embed.side_effect = capture_add_embed

        with patch("app.discord_bot.DiscordWebhook", return_value=mock_webhook):
            result = bot.send_annual_roundup_alert(
                "Best Films 2025", "2025-12-19",
                "https://example.com/best-films", sample_shows, "annual_film"
            )

        assert result is True
        embed = embeds_seen[0]
        assert embed.title == "🎬 Guardian Best Films of the Year"
        assert embed.color == 0x8B0000

    def test_returns_false_without_webhook_url(self, bot_no_webhook, sample_shows):
        result = bot_no_webhook.send_annual_roundup_alert(
            "Best TV 2025", "2025-12-31",
            "https://example.com", sample_shows, "annual_tv"
        )
        assert result is False

    def test_returns_false_on_non_200_response(self, bot, sample_shows):
        mock_webhook = _mock_webhook_execute(429)
        with patch("app.discord_bot.DiscordWebhook", return_value=mock_webhook):
            result = bot.send_annual_roundup_alert(
                "Best TV 2025", "2025-12-31",
                "https://example.com", sample_shows, "annual_tv"
            )
        assert result is False

    def test_includes_all_shows_up_to_20(self, bot):
        shows = [
            {"title": f"Show {i}", "platform": "Netflix",
             "description": "Desc.", "pick_of_the_week": False}
            for i in range(25)
        ]
        embeds_seen = []

        def capture_add_embed(embed):
            embeds_seen.append(embed)

        mock_webhook = _mock_webhook_execute(200)
        mock_webhook.add_embed.side_effect = capture_add_embed

        with patch("app.discord_bot.DiscordWebhook", return_value=mock_webhook):
            bot.send_annual_roundup_alert(
                "Best TV 2025", "2025-12-31",
                "https://example.com", shows, "annual_tv"
            )

        embed = embeds_seen[0]
        # 3 info fields (Published, Source, Read Full Article) + 20 show fields = 23
        show_fields = [f for f in embed.fields if f["name"].startswith(tuple(str(i) for i in range(1, 21)))]
        assert len(show_fields) == 20

    def test_no_pick_of_the_week_indicator(self, bot):
        shows = [
            {"title": "Top Show", "platform": "Netflix",
             "description": "Best of the year.", "pick_of_the_week": True}
        ]
        embeds_seen = []

        def capture_add_embed(embed):
            embeds_seen.append(embed)

        mock_webhook = _mock_webhook_execute(200)
        mock_webhook.add_embed.side_effect = capture_add_embed

        with patch("app.discord_bot.DiscordWebhook", return_value=mock_webhook):
            bot.send_annual_roundup_alert(
                "Best TV 2025", "2025-12-31",
                "https://example.com", shows, "annual_tv"
            )

        embed = embeds_seen[0]
        # No show field name should contain "Pick of the week" or "⭐"
        for field in embed.fields:
            assert "⭐" not in field["name"]
            assert "Pick of the week" not in field["name"]

    def test_footer_text_is_annual_roundup(self, bot, sample_shows):
        embeds_seen = []

        def capture_add_embed(embed):
            embeds_seen.append(embed)

        mock_webhook = _mock_webhook_execute(200)
        mock_webhook.add_embed.side_effect = capture_add_embed

        with patch("app.discord_bot.DiscordWebhook", return_value=mock_webhook):
            bot.send_annual_roundup_alert(
                "Best TV 2025", "2025-12-31",
                "https://example.com", sample_shows, "annual_tv"
            )

        embed = embeds_seen[0]
        assert embed.footer["text"] == "Guardian Annual Roundup Monitor"

    def test_description_includes_show_count(self, bot, sample_shows):
        embeds_seen = []

        def capture_add_embed(embed):
            embeds_seen.append(embed)

        mock_webhook = _mock_webhook_execute(200)
        mock_webhook.add_embed.side_effect = capture_add_embed

        with patch("app.discord_bot.DiscordWebhook", return_value=mock_webhook):
            bot.send_annual_roundup_alert(
                "Best TV 2025", "2025-12-31",
                "https://example.com", sample_shows, "annual_tv"
            )

        embed = embeds_seen[0]
        assert str(len(sample_shows)) in embed.description


class TestSendNewShowsAlert:
    """Regression tests to confirm the existing weekly alert is unaffected."""

    def test_weekly_alert_uses_original_title(self, bot, sample_shows):
        embeds_seen = []

        def capture_add_embed(embed):
            embeds_seen.append(embed)

        mock_webhook = _mock_webhook_execute(200)
        mock_webhook.add_embed.side_effect = capture_add_embed

        with patch("app.discord_bot.DiscordWebhook", return_value=mock_webhook):
            result = bot.send_new_shows_alert(
                "Seven best shows this week", "2026-05-29",
                "https://example.com/weekly", sample_shows
            )

        assert result is True
        embed = embeds_seen[0]
        assert embed.title == "🎬 New Guardian Show Recommendations!"
        assert embed.color == 0x052962

    def test_weekly_alert_shows_pick_of_the_week(self, bot):
        shows = [
            {"title": "Top Pick", "platform": "Netflix",
             "description": "Best show.", "pick_of_the_week": True}
        ]
        embeds_seen = []

        def capture_add_embed(embed):
            embeds_seen.append(embed)

        mock_webhook = _mock_webhook_execute(200)
        mock_webhook.add_embed.side_effect = capture_add_embed

        with patch("app.discord_bot.DiscordWebhook", return_value=mock_webhook):
            bot.send_new_shows_alert(
                "Seven best shows", "2026-05-29",
                "https://example.com", shows
            )

        embed = embeds_seen[0]
        show_fields = [f for f in embed.fields if "Top Pick" in f["name"]]
        assert any("⭐" in f["name"] for f in show_fields)
