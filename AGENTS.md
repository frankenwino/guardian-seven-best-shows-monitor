# AGENTS.md

<!-- metadata:type=agent-guide, updated=2026-08-16 -->

## Project Overview

Python CLI tool that monitors The Guardian's weekly "Seven Best Shows to Stream" article series. Runs as a single-shot cron job on Fridays. Scrapes articles, persists show data to JSON, sends Discord webhook notifications, and optionally creates qBittorrent RSS download rules.

## Directory Map

```
guardian_monitor.py          → CLI entry point (maps commands to app/main.py)
app/                         → Python package (imported as `app.*`)
├── main.py                  → GuardianMonitor orchestrator (core workflow)
├── config.py                → Config singleton (loads config.ini + .env)
├── scraper.py               → GuardianScraper (HTML parsing, multiple strategies)
├── storage.py               → ShowDataStorage (JSON file persistence)
├── discord_bot.py           → GuardianDiscordBot (webhook notifications)
├── qbittorrent_rules.py     → QBittorrentRulesManager (also standalone CLI)
├── log_manager.py           → LogManager (log rotation, standalone CLI)
├── storage_utils.py         → Storage CLI utility (stats, search, cleanup)
├── manual_integration_test.py → Integration test (uses main() pattern, not pytest)
└── test_discord_sample.py   → Discord notification test
demo_restart.py              → Manual demo of qBittorrent close/restart handling
test_qbt_restart.py          → Manual qBittorrent restart test (not pytest)
pyproject.toml               → pytest + mypy configuration
requirements.txt             → Runtime and dev dependencies
config.ini                   → App settings (URLs, timeouts, logging)
config.ini.example           → Template for config.ini
.env / .env.example          → Secrets (DISCORD_WEBHOOK_URL, DISCORD_BOT_TOKEN)
download_rules.json          → Sample/reference qBittorrent RSS rules file
cron-setup.md, cron-example.txt → Scheduling docs and sample crontab
DISCORD_SETUP.md             → Discord webhook setup guide
data/                        → JSON persistence (git-ignored)
logs/                        → Timestamped log files (git-ignored, only when log_to_file=true)
tests/                       → Pytest unit tests (test_scraper, test_storage, test_integration)
specs/                       → Feature specifications (pytest config, JSON validation,
                               demo script docs, type checking)
```

## Architecture

```mermaid
graph LR
    CLI[guardian_monitor.py] --> M[GuardianMonitor]
    M --> S[GuardianScraper]
    M --> ST[ShowDataStorage]
    M --> D[GuardianDiscordBot]
    M --> Q[QBittorrentRulesManager]
```

**Flow**: Scrape Guardian → Check if new → Save to JSON → Notify Discord → Create qBittorrent rules

**Key patterns**:
- Orchestrator in `app/main.py` coordinates all components
- Config singleton (`from .config import config`) used everywhere
- Graceful degradation: Discord and qBittorrent are optional
- Idempotent: `processed_articles.json` prevents duplicate processing
- Cascading scraper: tries 4 parsing strategies because Guardian article format varies
- Article dicts carry `series_tag` (e.g. `tv-and-radio/series/2025-in-tv`) and `series_type` (`weekly` | `annual_tv` | `annual_film`) — routing in `main.py` and Discord branching depend on these

## Configuration

| Source | Contains | Tracked in Git |
|--------|----------|----------------|
| `config.ini` | URLs, timeouts, log settings, data path, HTTP settings | Yes |
| `.env` | `DISCORD_WEBHOOK_URL`, `DISCORD_BOT_TOKEN` | No (`.env.example` tracked) |

Config is loaded once at module import time via the global `config` instance in `app/config.py`.

## Data Files (in `data/`)

| File | Purpose | Retention |
|------|---------|-----------|
| `shows_history.json` | Complete archive of all shows | Indefinite |
| `processed_articles.json` | Deduplication registry | Auto-capped at 100 |
| `last_checked.json` | Last processed article reference | Single entry |

## Notable Implementation Details

- **Scraper uses cascading parsing**: Tries h2 headings → numbered h2/h3 → bold numbered text → body parsing. This is because The Guardian's article format varies.
- **qBittorrent rules management** requires closing the qBittorrent process to write its config file. The code handles close → backup → write → restart with rollback on failure.
- **Package imports**: `app/` is a real package; modules use relative imports (`from .config import config`) and `guardian_monitor.py` does `from app.main import main`. The standalone scripts (`demo_restart.py`, `test_qbt_restart.py`, `tests/conftest.py`, `app/storage_utils.py`) still manipulate `sys.path` to import modules directly.
- **Scheduling**: Designed for Friday-only cron execution (Guardian publishes Fridays 08:00 CET). Recommended: `30 8 * * 5` and `0 10 * * 5`.
- **Multi-series**: `series_urls` in `config.ini` is a comma-separated list. Each URL is converted to a Guardian Content API tag. `series_type` is derived automatically: `weekly` (default), `annual_tv` (tag matches `\d{4}-in-tv` or `best-tv-of-\d{4}`), `annual_film` (tag starts with `film/`). Article dicts include `series_tag` and `series_type` keys — downstream code routes on these.
- **Annual roundups**: same cron job handles weekly and annual articles. Annual roundup articles published in December are picked up on the next Friday run. Add new year series URLs to `config.ini` when The Guardian publishes them (commented-out placeholders are already there for 2026).
- **Discord routing**: `_send_discord_notifications` in `main.py` calls `send_annual_roundup_alert` for `annual_tv`/`annual_film`, `send_new_shows_alert` for `weekly`.
- **qBittorrent rules**: skipped for `annual_film` articles (film titles have no TV episode structure). Runs as normal for `weekly` and `annual_tv`.
- **Logging**: Log files are timestamped (`app/config.py`), but file logging is off by default (`log_to_file = false`), so `logs/` is normally empty.
- **Storage safety**: JSON writes use corruption recovery (safe load with fallback to defaults) and backup-on-write.

## Testing

- **pytest** (`tests/`): Unit tests for scraper, storage, and integration tests requiring network. Config in `pyproject.toml` (`testpaths = ["tests"]`, `integration` marker)
- **Manual test scripts** (`app/manual_integration_test.py`, `app/test_discord_sample.py`, `demo_restart.py`, `test_qbt_restart.py`): Use `if __name__ == "__main__"` pattern
- **mypy**: Configured in `pyproject.toml` targeting Python 3.10

## Detailed Documentation

For deeper information, see `.agents/summary/`:
- `index.md` — Navigation guide and cross-references
- `codebase_info.md` — Project identity, tech stack, entry points
- `architecture.md` — Full system diagrams and design patterns
- `components.md` — Class diagrams and method signatures
- `interfaces.md` — All CLI commands and external integrations
- `data_models.md` — JSON schemas and data structures
- `workflows.md` — Flowcharts for all processes
- `dependencies.md` — Package list and dependency graph
- `review_notes.md` — Documentation gaps and debugging pointers

## Custom Instructions
<!-- This section is for human and agent-maintained operational knowledge.
     Add repo-specific conventions, gotchas, and workflow rules here.
     This section is preserved exactly as-is when re-running codebase-summary. -->
