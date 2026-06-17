# Interfaces

<!-- metadata:type=interfaces, scope=cli-and-external -->

## CLI Interfaces

### guardian_monitor.py (Main CLI)

| Command | Description | Exit Codes |
|---------|-------------|-----------|
| `./guardian_monitor.py` | Check for new shows (default=run) | 0=success, 1=error |
| `./guardian_monitor.py run` | Same as no argument | |
| `./guardian_monitor.py test` | Test all components (scraper, storage, Discord) | |
| `./guardian_monitor.py status` | Show last checked article, history stats | |
| `./guardian_monitor.py config` | Display current configuration | |
| `./guardian_monitor.py help` | Print usage information | |

### app/qbittorrent_rules.py (Standalone CLI)

| Command | Flags | Description |
|---------|-------|-------------|
| `python app/qbittorrent_rules.py analyze` | | Compare shows vs existing qBittorrent rules |
| `python app/qbittorrent_rules.py create` | | Preview rules that would be created |
| `python app/qbittorrent_rules.py create` | `--apply` | Write rules (requires qBittorrent closed) |
| `python app/qbittorrent_rules.py create` | `--apply --auto-qbt` | Close/write/restart qBittorrent automatically |
| `python app/qbittorrent_rules.py status` | | Check qBittorrent process status |
| `python app/qbittorrent_rules.py backups` | | Show backup files status |
| `python app/qbittorrent_rules.py cleanup` | | Remove old backup files (keeps 10) |

### app/storage_utils.py (Standalone CLI)

| Command | Flags | Description |
|---------|-------|-------------|
| `python app/storage_utils.py stats` | | Show storage statistics |
| `python app/storage_utils.py search <query>` | | Search shows by text |
| `python app/storage_utils.py history` | `--limit N` | View recent show history |
| `python app/storage_utils.py cleanup-articles` | `--max N` | Cap processed articles list |
| `python app/storage_utils.py filter <platform>` | | Filter shows by platform |

### app/log_manager.py (Standalone CLI)

| Command | Description |
|---------|-------------|
| `python app/log_manager.py status` | Show log file statistics |
| `python app/log_manager.py cleanup` | Remove old log files (keeps 10) |

## External Integrations

### The Guardian Website

| Endpoint | Method | Purpose |
|----------|--------|---------|
| Series index page(s) | GET | List available articles |
| Individual article page | GET | Parse show recommendations |

Configured in `config.ini` under `[guardian]`:
- `series_urls` — comma-separated list of series index URLs
- `base_url` — base URL for resolving relative links

### Discord Webhook API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| Webhook URL | POST | Send rich embed notifications |

Configured via `.env`:
- `DISCORD_WEBHOOK_URL` — webhook endpoint (required for notifications)
- `DISCORD_BOT_TOKEN` — bot token (optional, for bulk message deletion)

### qBittorrent

| Interface | Method | Purpose |
|-----------|--------|---------|
| Process control | `pgrep`/`pkill` | Check/stop/start process |
| Config file | Direct file I/O | Read/write RSS download rules |

Default rules file: `~/.config/qBittorrent/rss/download_rules.json`

## Internal APIs (Python)

### GuardianScraper
```python
scraper = GuardianScraper(series_urls=["..."])
articles: List[Dict] = scraper.get_series_articles()
shows: List[Dict] = scraper.parse_show_recommendations(article_url)
```

### ShowDataStorage
```python
storage = ShowDataStorage(data_dir="data")
storage.is_article_processed(url) -> bool
storage.add_processed_article(url)
storage.save_shows_data(article_dict, shows_list)
storage.search_shows(query) -> List[Dict]
storage.get_storage_stats() -> Dict
```

### GuardianDiscordBot
```python
bot = GuardianDiscordBot()
bot.send_new_shows_alert(title, date, url, shows) -> bool
bot.send_error_notification(error_msg) -> bool
```
