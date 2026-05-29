# Components

<!-- metadata:type=components, audience=ai-agents, updated=2026-05-29 -->

## Component Map

```mermaid
classDiagram
    class GuardianMonitor {
        +scraper: GuardianScraper
        +storage: ShowDataStorage
        +discord_bot: GuardianDiscordBot
        +qbt_manager: QBittorrentRulesManager
        +run() bool
        +check_for_new_shows() bool
        +get_status() dict
        +test_components() bool
    }

    class GuardianScraper {
        +session: requests.Session
        +fetch_page(url) BeautifulSoup
        +get_series_articles() List[Dict]
        +parse_show_recommendations(url) List[Dict]
        +get_latest_article_url() Optional[str]
    }

    class ShowDataStorage {
        +data_dir: Path
        +is_article_processed(url) bool
        +save_shows_data(url, title, date, shows) bool
        +add_processed_article(url, title, date, count) bool
        +get_shows_history(limit) List[Dict]
        +search_shows(query) List[Dict]
        +get_storage_stats() Dict
    }

    class GuardianDiscordBot {
        +webhook_url: str
        +send_new_shows_alert(title, date, url, shows) bool
        +send_error_notification(error, context) bool
        +send_test_message() bool
    }

    class QBittorrentRulesManager {
        +rules_file: Path
        +backup_dir: Path
        +load_rules() Dict
        +save_rules(rules) None
        +check_existing_rules(title, rules) List
        +create_rule_template(title, platform) Dict
        +backup_rules() str
        +is_qbittorrent_running() bool
        +close_qbittorrent() bool
        +start_qbittorrent() bool
    }

    class Config {
        +discord_webhook_url: str
        +guardian_series_url: str
        +data_directory: str
        +request_timeout: int
        +setup_logging() None
        +is_discord_configured() bool
        +get_data_directory_path() Path
    }

    class LogManager {
        +log_dir: Path
        +show_log_status() None
        +cleanup_logs(max_logs) None
    }

    GuardianMonitor --> GuardianScraper
    GuardianMonitor --> ShowDataStorage
    GuardianMonitor --> GuardianDiscordBot
    GuardianMonitor --> QBittorrentRulesManager
    GuardianMonitor ..> Config
```

## Component Details

### GuardianMonitor (`app/main.py`)
The orchestrator. Initializes all components, runs the check-for-new-shows workflow, and provides status/test commands. Entry point for all application logic.

### GuardianScraper (`app/scraper.py`)
Scrapes The Guardian website. Uses multiple parsing strategies (h2 headings, numbered headings, bold text, body parsing) to extract show recommendations from articles. Handles URL pattern matching to identify "seven best shows" articles.

### ShowDataStorage (`app/storage.py`)
JSON-based persistence layer. Manages three files:
- `last_checked.json` — last processed article reference
- `processed_articles.json` — deduplication registry (auto-capped at 100 entries)
- `shows_history.json` — complete archive of all show recommendations

### GuardianDiscordBot (`app/discord_bot.py`)
Sends rich embed notifications via Discord webhooks. Formats show data with platform info, descriptions, and "pick of the week" indicators. Also handles error notifications.

### QBittorrentRulesManager (`app/qbittorrent_rules.py`)
Manages qBittorrent RSS auto-download rules. Can close/restart qBittorrent process, backup existing rules (gzip compressed), and create new rules from show titles. Operates on qBittorrent's `download_rules.json` config file directly.

### Config (`app/config.py`)
Singleton configuration loader. Reads `config.ini` for application settings and `.env` for secrets. Validates all values and provides a global `config` instance.

### LogManager (`app/log_manager.py`)
Manages timestamped log file rotation. Keeps maximum 10 log files.

### storage_utils.py (`app/storage_utils.py`)
CLI utility for storage operations: stats, history, search, platform filtering, cleanup, and reset. Not imported by the main application — standalone tool.
