# Guardian Seven Best Shows Monitor

Automated monitoring for The Guardian's weekly "Seven Best Shows to Stream" series with Discord notifications.

## Quick Setup

```bash
# 1. Clone and install
git clone https://github.com/frankenwino/guardian-seven-best-shows-monitor.git
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
```

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
