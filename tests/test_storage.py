"""Unit tests for ShowDataStorage."""

import json

import pytest


class TestIsArticleProcessed:
    def test_empty_state_returns_false(self, storage):
        assert storage.is_article_processed("http://example.com/article") is False

    def test_returns_true_after_adding(self, storage, sample_article):
        storage.add_processed_article(
            sample_article["url"],
            sample_article["title"],
            sample_article["date"],
            7,
        )
        assert storage.is_article_processed(sample_article["url"]) is True

    def test_different_url_returns_false(self, storage, sample_article):
        storage.add_processed_article(
            sample_article["url"],
            sample_article["title"],
            sample_article["date"],
            7,
        )
        assert storage.is_article_processed("http://example.com/other") is False


class TestAddProcessedArticle:
    def test_writes_correct_json(self, storage, sample_article):
        storage.add_processed_article(
            sample_article["url"],
            sample_article["title"],
            sample_article["date"],
            2,
        )

        data = json.loads(storage.processed_articles_file.read_text())
        assert sample_article["url"] in data["processed_urls"]
        assert data["articles_info"][sample_article["url"]]["shows_count"] == 2


class TestCleanupProcessedArticles:
    def test_caps_at_max_entries(self, storage):
        # Add 105 articles
        for i in range(105):
            storage.add_processed_article(
                f"http://example.com/article-{i}",
                f"Article {i}",
                "2026-01-01",
                7,
            )

        data = json.loads(storage.processed_articles_file.read_text())
        assert len(data["processed_urls"]) <= 100


class TestSaveShowsData:
    def test_saves_and_retrieves(self, storage, sample_article, sample_shows):
        storage.save_shows_data(
            sample_article["url"],
            sample_article["title"],
            sample_article["date"],
            sample_shows,
        )

        history = storage.get_shows_history()
        assert len(history) == 1
        assert history[0]["article_url"] == sample_article["url"]
        assert len(history[0]["shows"]) == 2


class TestGetStorageStats:
    def test_empty_storage(self, storage):
        stats = storage.get_storage_stats()
        assert stats["processed_articles_count"] == 0
        assert stats["shows_history_entries"] == 0


class TestJsonRecovery:
    """Tests for graceful handling of corrupted JSON files."""

    def test_corrupted_last_checked(self, storage):
        storage.last_checked_file.write_text("{broken json", encoding="utf-8")
        assert storage.get_last_checked_article() is None

    def test_corrupted_processed_articles(self, storage):
        storage.processed_articles_file.write_text("not json!", encoding="utf-8")
        assert storage.get_processed_articles() == set()

    def test_corrupted_shows_history(self, storage):
        storage.shows_history_file.write_text("[invalid", encoding="utf-8")
        assert storage.get_shows_history() == []

    def test_wrong_structure_last_checked(self, storage):
        # Should be dict, but is a list
        storage.last_checked_file.write_text("[]", encoding="utf-8")
        assert storage.get_last_checked_article() is None

    def test_wrong_structure_processed_articles(self, storage):
        # Should be dict, but is a list
        storage.processed_articles_file.write_text("[]", encoding="utf-8")
        assert storage.get_processed_articles() == set()

    def test_wrong_structure_shows_history(self, storage):
        # Should be list, but is a dict
        storage.shows_history_file.write_text("{}", encoding="utf-8")
        assert storage.get_shows_history() == []

    def test_backup_created_on_write(self, storage, sample_article):
        # Write initial data
        storage.update_last_checked_article(
            sample_article["url"], sample_article["title"], sample_article["date"]
        )
        # Write again — should create .bak
        storage.update_last_checked_article(
            sample_article["url"], sample_article["title"], sample_article["date"]
        )
        bak_file = storage.last_checked_file.with_suffix(".json.bak")
        assert bak_file.exists()
