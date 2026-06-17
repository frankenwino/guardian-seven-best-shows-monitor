# Components

<!-- metadata:type=components, scope=classes -->

## Class Diagram

```mermaid
classDiagram
    class GuardianMonitor {
        +scraper: GuardianScraper
        +storage: ShowDataStorage
        +discord_bot: GuardianDiscordBot?
        +qbt_manager: QBittorrentRulesManager?
        +check_for_new_shows() bool
        +run()
        +test_components()
        +get_status()
    }

    class GuardianScraper {
        +base_url: str
        +series_urls: List[str]
        +session: requests.Session
        +fetch_page(url) BeautifulSoup?
        +get_series_articles() List[Dict]
        +get_latest_article_url() str?
        +parse_show_recommendations(url) List[Dict]
        -_is_seven_best_shows_article(url) bool
        -_extract_title_from_link(link) str
        -_extract_date_from_url(url) str?
        -_parse_show_from_heading(elem) Dict?
        -_parse_show_from_guardian_heading(elem) Dict?
        -_parse_show_from_element(elem) Dict?
        -_parse_shows_from_body(soup) List[Dict]
        -_extract_platform(text) str
    }

    class ShowDataStorage {
        +data_dir: Path
        +last_checked_file: Path
        +shows_history_file: Path
        +processed_articles_file: Path
        +is_article_processed(url) bool
        +add_processed_article(url)
        +get_processed_articles() List[Dict]
        +save_shows_data(article, shows)
        +get_shows_history() List[Dict]
        +get_shows_by_platform(platform) List[Dict]
        +search_shows(query) List[Dict]
        +get_storage_stats() Dict
        +cleanup_duplicate_history_entries()
        +cleanup_old_data()
        +get_last_checked_article() Dict?
        +update_last_checked_article(article)
        -_safe_load_json(path, default, type?) Any
        -_safe_write_json(path, data)
        -_cleanup_processed_articles()
    }

    class GuardianDiscordBot {
        +webhook_url: str?
        +is_configured() bool
        +send_new_shows_alert(title, date, url, shows) bool
        +send_error_notification(error_msg) bool
        +send_test_message() bool
        -_format_date(date_str) str
    }

    class QBittorrentRulesManager {
        +rules_file: Path
        +backup_dir: Path
        +is_qbittorrent_running() bool
        +close_qbittorrent() bool
        +start_qbittorrent() bool
        +load_rules() Dict
        +save_rules(rules)
        +backup_rules() Path?
        +get_guardian_shows() List[Dict]
        +check_existing_rules() Set[str]
        +clean_title_for_search(title) str
        +create_rule_template(show) Dict
        +analyze_shows()
        +create_missing_rules(apply, auto_qbt)
        +cleanup_backups()
        +show_backup_status()
        -_cleanup_old_backups()
    }

    class Config {
        +project_root: Path
        +discord_webhook_url: str?
        +guardian_series_urls: List[str]
        +setup_logging()
        +is_discord_configured() bool
        +get_data_directory_path() Path
        +get_summary() str
        -_load_env_file(path?)
        -_load_config_file(path?)
        -_validate_config()
        -_cleanup_old_logs()
    }

    class LogManager {
        +log_dir: Path
        +show_log_status()
        +cleanup_logs()
    }

    GuardianMonitor --> GuardianScraper
    GuardianMonitor --> ShowDataStorage
    GuardianMonitor --> GuardianDiscordBot
    GuardianMonitor --> QBittorrentRulesManager
    GuardianMonitor --> Config
    QBittorrentRulesManager --> ShowDataStorage
```

## Component Responsibilities

### GuardianMonitor (`app/main.py`)
Top-level orchestrator. Initializes all components, runs the check-for-new-shows workflow, provides test/status/config commands. Handles argument parsing for the CLI.

### GuardianScraper (`app/scraper.py`)
HTTP client that fetches Guardian series index pages, identifies article URLs, and parses show recommendations from article HTML. Implements multiple fallback parsing strategies due to inconsistent Guardian article formatting.

### ShowDataStorage (`app/storage.py`)
JSON-file-based persistence layer. Manages three data files: article deduplication registry, show history archive, and last-checked pointer. Includes corruption recovery (safe load with fallback), backup-on-write, and automatic cleanup (caps processed articles at 100).

### GuardianDiscordBot (`app/discord_bot.py`)
Discord webhook client. Formats show recommendations as rich embeds with article metadata and sends to configured channel. Supports error notifications and test messages.

### QBittorrentRulesManager (`app/qbittorrent_rules.py`)
Manages qBittorrent RSS auto-download rules. Reads show history from storage, generates search rules for each title, and writes them to qBittorrent's config file. Handles process lifecycle (close/restart) and config file backup/rollback. Also operates as standalone CLI.

### Config (`app/config.py`)
Singleton configuration loader. Merges `config.ini` (application settings) with `.env` (secrets). Provides logging setup with timestamped file rotation.

### LogManager (`app/log_manager.py`)
Simple log file rotation utility. Keeps maximum 10 log files, provides status reporting and manual cleanup CLI.
