# Codebase Information

<!-- metadata:type=overview, scope=project -->

## Project Identity

- **Name**: Guardian Seven Best Shows Monitor
- **Language**: Python (3.14, mypy configured for 3.10 compat)
- **Type**: CLI automation tool (cron-driven)
- **License**: Not specified
- **Repository**: frankenwino/guardian-seven-best-shows-monitor

## Purpose

Monitors The Guardian's weekly "Seven Best Shows to Stream" and "Seven Best Films to Watch on TV" article series. Scrapes recommendations, persists to JSON, sends Discord notifications, and optionally creates qBittorrent RSS download rules.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.14 |
| HTTP | requests + BeautifulSoup4 |
| Notifications | discord-webhook |
| Config | configparser + python-dotenv |
| Testing | pytest + mypy |
| Scheduling | System cron (external) |
| Process control | subprocess (qBittorrent) |

## Entry Points

| Entry Point | Purpose |
|-------------|---------|
| `guardian_monitor.py` | Main CLI (run/test/status/config) |
| `app/qbittorrent_rules.py` | Standalone qBittorrent CLI (analyze/create/status/backups/cleanup) |
| `app/storage_utils.py` | Storage CLI (stats/search/history/cleanup) |
| `app/log_manager.py` | Log management CLI (status/cleanup) |

## Project Metrics

| Metric | Value |
|--------|-------|
| Source files | 17 prioritized |
| Classes | 5 main + 6 test |
| Functions | 135 |
| Test files | 3 (pytest) + 2 (manual) |
