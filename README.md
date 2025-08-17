# Guardian Seven Best Shows Monitor

Automated monitoring for The Guardian's weekly "Seven Best Shows to Stream" series with Discord notifications.

## Quick Setup

```bash
# 1. Clone and install
git clone <repository-url>
cd guardian-seven-best-shows-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt

# 2. Configure Discord webhook
cp .env.example .env
# Edit .env and add your Discord webhook URL

# 3. Test
./guardian_monitor.py test

# 4. Run
./guardian_monitor.py
```

## Commands

```bash
./guardian_monitor.py          # Check for new shows
./guardian_monitor.py test     # Test all components
./guardian_monitor.py status   # Show current status
./guardian_monitor.py config   # Show configuration
```

## qBittorrent Integration

Automatically create download rules for Guardian shows:

```bash
# Analyze shows vs existing qBittorrent rules
python app/qbittorrent_rules.py analyze

# Preview rules that would be created
python app/qbittorrent_rules.py create

# Create rules (manual qBittorrent management - close qBittorrent first!)
python app/qbittorrent_rules.py create --apply

# Create rules with automatic qBittorrent management
python app/qbittorrent_rules.py create --apply --auto-qbt

# Check qBittorrent process status
python app/qbittorrent_rules.py status

# Show backup files status
python app/qbittorrent_rules.py backups

# Clean up old backup files (keeps 10 most recent)
python app/qbittorrent_rules.py cleanup
```

**Note**: Rules are created enabled and ready to download. Disable them in qBittorrent UI if you want to review first.

## Scheduling (Recommended)

The Guardian publishes every Friday at 08:00 CET. Add to crontab:

```bash
# Two Friday checks (recommended)
30 8 * * 5 /path/to/project/venv/bin/python /path/to/project/guardian_monitor.py
0 10 * * 5 /path/to/project/venv/bin/python /path/to/project/guardian_monitor.py
```

## Configuration

### Discord Setup
1. Server Settings → Integrations → Webhooks → Create New
2. Copy webhook URL to `.env` file:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN
```

### App Settings (`config.ini`)
```ini
[guardian]
series_url = https://www.theguardian.com/tv-and-radio/series/the-seven-best-shows-to-stream-this-week

[application]
send_error_notifications = true

[storage]
data_directory = data

[logging]
log_level = INFO
log_to_file = false
log_file = logs/guardian_monitor.log
```

### Log Management
When `log_to_file = true`, each run creates a timestamped log file and automatically keeps only the 10 most recent:

```bash
# View log files status
python app/log_manager.py status

# Clean up old log files manually
python app/log_manager.py cleanup
```

**Log files**: `logs/guardian_monitor_YYYYMMDD_HHMMSS.log`

## Data Storage

- `data/shows_history.json` - Complete archive of all show recommendations
- `data/processed_articles.json` - Prevents duplicate processing
- `data/last_checked.json` - Last processed article info

**Archive grows indefinitely** - builds comprehensive multi-year database.

## Discord Notifications

Rich embeds with:
- Article title and publication date
- Direct link to Guardian article
- Show details: title, platform, description
- ⭐ "Pick of the week" indicator

## Troubleshooting

**"Discord webhook not configured"**
- Set `DISCORD_WEBHOOK_URL` in `.env` file

**"No articles found"**
- Check internet connection
- Run `./guardian_monitor.py test`

**Permission denied**
- `chmod +x guardian_monitor.py`

## Storage Management

```bash
# View statistics
python app/storage_utils.py stats

# Search shows
python app/storage_utils.py search "netflix"

# View history
python app/storage_utils.py history --limit 10

# Clean up old processed articles (keeps 100 most recent)
python app/storage_utils.py cleanup-articles --max 100
```

### Disk Space Optimizations

**Automatic optimizations:**
- **Processed articles cleanup**: Keeps only 100 most recent articles (prevents unbounded growth)
- **qBittorrent backup compression**: ~96% size reduction with gzip compression
- **Log file rotation**: Maximum 10 timestamped log files
- **Backup file rotation**: Maximum 10 backup files

**Manual cleanup commands:**
```bash
# Clean up old processed articles
python app/storage_utils.py cleanup-articles

# Clean up old backup files  
python app/qbittorrent_rules.py cleanup

# Clean up old log files
python app/log_manager.py cleanup
```

## Project Structure

```
guardian-seven-best-shows-monitor/
├── app/                    # Application code
├── data/                   # JSON storage (ignored in git)
├── logs/                   # Log files (ignored in git)
├── guardian_monitor.py     # Main CLI script
├── config.ini             # App configuration
├── .env                   # Discord webhook (ignored in git)
└── README.md              # This file
```
