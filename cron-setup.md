# Cron Setup

The Guardian publishes every **Friday at 08:00 CET**.

## Recommended Schedule

```bash
# Two Friday checks (reliable)
30 8 * * 5 /path/to/project/venv/bin/python /path/to/project/guardian_monitor.py
0 10 * * 5 /path/to/project/venv/bin/python /path/to/project/guardian_monitor.py
```

## Setup

1. **Edit crontab:**
   ```bash
   crontab -e
   ```

2. **Add the two lines above** (replace `/path/to/project/` with your actual path)

3. **Save and verify:**
   ```bash
   crontab -l
   ```

## Alternative Schedules

**Single check:**
```bash
30 8 * * 5 /path/to/project/venv/bin/python /path/to/project/guardian_monitor.py
```

**Conservative (3 checks):**
```bash
15 8 * * 5 /path/to/project/venv/bin/python /path/to/project/guardian_monitor.py
0 9 * * 5 /path/to/project/venv/bin/python /path/to/project/guardian_monitor.py
0 11 * * 5 /path/to/project/venv/bin/python /path/to/project/guardian_monitor.py
```

## Testing

Test the exact cron command:
```bash
/path/to/project/venv/bin/python /path/to/project/guardian_monitor.py
```

## Why Friday-Only

- **Efficient**: 52 checks/year vs 365
- **Pattern-based**: Matches Guardian's actual schedule
- **Resource-friendly**: No wasted daily checks

## Annual Roundups

The same Friday cron job also handles annual "best of year" roundups
(configured in `series_urls` in `config.ini`). The Guardian publishes
these in December. Because the monitor deduplicates by article URL,
it will pick them up on the first Friday run after they're published
and send a separate Discord embed with the annual roundup style.

No additional cron job is needed. To add the next year's series once
The Guardian publishes it, uncomment the relevant line in `config.ini`.
