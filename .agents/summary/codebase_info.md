# Codebase Information

<!-- metadata:type=overview, audience=ai-agents, updated=2026-05-29 -->

## Project Identity

- **Name**: Guardian Seven Best Shows Monitor
- **Language**: Python 3
- **Type**: CLI automation tool (single-run, cron-scheduled)
- **Purpose**: Monitors The Guardian's weekly "Seven Best Shows to Stream" series, sends Discord notifications, and manages qBittorrent download rules

## Technology Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3 |
| Web Scraping | requests, BeautifulSoup4 |
| Notifications | discord-webhook |
| Configuration | configparser (INI), python-dotenv (.env) |
| Data Persistence | JSON files |
| Process Management | subprocess (qBittorrent) |
| Date Handling | python-dateutil |
| Scheduling | System cron (external) |

## Directory Layout

```
guardian-seven-best-shows-monitor/
├── guardian_monitor.py      # CLI entry point
├── config.ini               # Application configuration
├── .env                     # Secrets (Discord webhook URL, bot token)
├── requirements.txt         # Python dependencies
├── cron-setup.md            # Cron scheduling guide
├── DISCORD_SETUP.md         # Discord webhook setup guide
├── app/                     # Core application modules
│   ├── main.py              # GuardianMonitor orchestrator
│   ├── config.py            # Config singleton (loads config.ini + .env)
│   ├── scraper.py           # GuardianScraper (web scraping)
│   ├── storage.py           # ShowDataStorage (JSON persistence)
│   ├── discord_bot.py       # GuardianDiscordBot (notifications)
│   ├── qbittorrent_rules.py # QBittorrentRulesManager (download rules)
│   ├── log_manager.py       # LogManager (log file rotation)
│   ├── storage_utils.py     # CLI for storage operations
│   ├── test_integration.py  # Integration tests
│   └── test_discord_sample.py # Discord notification test
├── data/                    # JSON data files (git-ignored)
│   ├── shows_history.json
│   ├── processed_articles.json
│   └── last_checked.json
└── logs/                    # Log files (git-ignored)
```

## Execution Model

- **Single-run**: Each invocation performs one check and exits
- **Scheduling**: Designed for cron execution on Fridays (Guardian publishes Fridays at 08:00 CET)
- **Idempotent**: Tracks processed articles to avoid duplicate notifications
- **Stateful**: Persists data between runs via JSON files in `data/`

## Configuration Sources

1. **config.ini** — Application settings (URLs, timeouts, logging, storage paths)
2. **.env** — Secrets (`DISCORD_WEBHOOK_URL`, `DISCORD_BOT_TOKEN`)
3. **Global singleton** — `config.py` exports a `config` instance used by all modules
