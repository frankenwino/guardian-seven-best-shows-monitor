# Workflows

<!-- metadata:type=workflows, audience=ai-agents, updated=2026-05-29 -->

## Primary Workflow: Check for New Shows

```mermaid
flowchart TD
    START[Cron triggers guardian_monitor.py] --> INIT[Initialize GuardianMonitor]
    INIT --> SCRAPE[Scrape series index page]
    SCRAPE --> ARTICLES{Articles found?}
    ARTICLES -->|No| EXIT_NONE[Exit: no articles]
    ARTICLES -->|Yes| CHECK[Check if latest article is processed]
    CHECK --> PROCESSED{Already processed?}
    PROCESSED -->|Yes| EXIT_DUP[Exit: no new content]
    PROCESSED -->|No| PARSE[Parse show recommendations from article]
    PARSE --> SHOWS{Shows found?}
    SHOWS -->|No| EXIT_EMPTY[Exit: no shows in article]
    SHOWS -->|Yes| SAVE[Save to shows_history.json]
    SAVE --> MARK[Mark article as processed]
    MARK --> DISCORD{Discord configured?}
    DISCORD -->|Yes| NOTIFY[Send Discord notification]
    DISCORD -->|No| QBT_CHECK
    NOTIFY --> QBT_CHECK{qBittorrent available?}
    QBT_CHECK -->|Yes| RULES[Create qBittorrent rules]
    QBT_CHECK -->|No| DONE[Exit: success]
    RULES --> DONE
```

## qBittorrent Rules Workflow

```mermaid
flowchart TD
    START[New shows detected] --> LOAD[Load existing rules]
    LOAD --> COMPARE[Compare shows vs existing rules]
    COMPARE --> NEEDED{New rules needed?}
    NEEDED -->|No| EXIT[Done: all rules exist]
    NEEDED -->|Yes| RUNNING{qBittorrent running?}
    RUNNING -->|Yes| CLOSE[Close qBittorrent gracefully]
    RUNNING -->|No| BACKUP
    CLOSE --> WAIT[Wait up to 10s for shutdown]
    WAIT --> CLOSED{Closed?}
    CLOSED -->|No| FORCE[Force kill]
    CLOSED -->|Yes| BACKUP[Backup current rules]
    FORCE --> BACKUP
    BACKUP --> CREATE[Create new rule entries]
    CREATE --> WRITE[Write updated rules file]
    WRITE --> RESTART{Was running before?}
    RESTART -->|Yes| START_QBT[Start qBittorrent]
    RESTART -->|No| DONE[Done]
    START_QBT --> DONE
```

## Scraper Parsing Strategy

```mermaid
flowchart TD
    FETCH[Fetch article HTML] --> FIND_BODY[Find article body div]
    FIND_BODY --> H2[Try: h2 headings with show format]
    H2 --> H2_FOUND{Shows found?}
    H2_FOUND -->|Yes| DONE[Return shows]
    H2_FOUND -->|No| NUMBERED[Try: numbered h2/h3 headings]
    NUMBERED --> NUM_FOUND{Shows found?}
    NUM_FOUND -->|Yes| DONE
    NUM_FOUND -->|No| BOLD[Try: bold/strong numbered text]
    BOLD --> BOLD_FOUND{Shows found?}
    BOLD_FOUND -->|Yes| DONE
    BOLD_FOUND -->|No| BODY[Try: sequential body parsing]
    BODY --> DONE
```

The scraper uses a cascading strategy because The Guardian's article format varies over time.

## Data Cleanup Workflows

### Automatic (on each run)
- Processed articles capped at 100 entries
- Log files capped at 10 (when `log_to_file = true`)

### Manual (via CLI utilities)
- `storage_utils.py cleanup-articles` — cap processed articles
- `storage_utils.py cleanup --days N` — remove old history (requires confirmation)
- `qbittorrent_rules.py cleanup` — remove old backup files
- `log_manager.py cleanup` — remove old log files

## Scheduling

| Schedule | Cron Expression | Rationale |
|----------|----------------|-----------|
| Primary check | `30 8 * * 5` | 30 min after Guardian's 08:00 CET publish time |
| Backup check | `0 10 * * 5` | Catch late publications |
| Conservative | Add `0 11 * * 5` | Third check for reliability |
