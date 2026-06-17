# Workflows

<!-- metadata:type=workflows, scope=processes -->

## Primary Workflow: Check for New Shows

```mermaid
flowchart TD
    START[Cron triggers guardian_monitor.py] --> INIT[Initialize components]
    INIT --> FETCH[Fetch series index pages]
    FETCH --> ARTICLES{Articles found?}
    ARTICLES -->|No| WARN[Log warning] --> END_EMPTY[Exit 0]
    ARTICLES -->|Yes| LOOP[For each article]
    LOOP --> CHECK{Already processed?}
    CHECK -->|Yes| SKIP[Skip] --> NEXT{More articles?}
    CHECK -->|No| PARSE[Parse show recommendations]
    PARSE --> SAVE[Save to shows_history.json]
    SAVE --> MARK[Mark article as processed]
    MARK --> DISCORD{Discord configured?}
    DISCORD -->|Yes| NOTIFY[Send Discord notification]
    DISCORD -->|No| QBT
    NOTIFY --> QBT{qBittorrent available?}
    QBT -->|Yes| RULES[Create download rules]
    QBT -->|No| NEXT
    RULES --> NEXT
    NEXT -->|Yes| LOOP
    NEXT -->|No| END[Exit 0]
```

## qBittorrent Rules Creation

```mermaid
flowchart TD
    START[create --apply --auto-qbt] --> LOAD[Load show history]
    LOAD --> EXISTING[Load existing rules]
    EXISTING --> DIFF[Identify missing rules]
    DIFF --> ANY{New rules needed?}
    ANY -->|No| DONE[Print "nothing to add"]
    ANY -->|Yes| RUNNING{qBittorrent running?}
    RUNNING -->|Yes| CLOSE[Close qBittorrent gracefully]
    CLOSE --> CLOSED{Closed OK?}
    CLOSED -->|No| FORCE[Force kill] --> BACKUP
    CLOSED -->|Yes| BACKUP[Backup existing config .gz]
    RUNNING -->|No| BACKUP
    BACKUP --> WRITE[Write merged rules JSON]
    WRITE --> RESTART[Start qBittorrent]
    RESTART --> VERIFY{Started OK?}
    VERIFY -->|Yes| SUCCESS[Print summary]
    VERIFY -->|No| ROLLBACK[Restore backup] --> FAIL[Exit error]
```

## Scraper Parsing Strategy

```mermaid
flowchart TD
    FETCH[Fetch article HTML] --> S1[Strategy 1: H2 headings]
    S1 --> FOUND1{Shows found?}
    FOUND1 -->|Yes| DONE[Return shows]
    FOUND1 -->|No| S2[Strategy 2: Numbered H2/H3]
    S2 --> FOUND2{Shows found?}
    FOUND2 -->|Yes| DONE
    FOUND2 -->|No| S3[Strategy 3: Bold numbered text]
    S3 --> FOUND3{Shows found?}
    FOUND3 -->|Yes| DONE
    FOUND3 -->|No| S4[Strategy 4: Body text parsing]
    S4 --> DONE
```

## Storage Cleanup Workflows

### Processed Articles Cleanup (automatic)
Triggered on every `add_processed_article()` call when count exceeds 100.
Removes oldest entries to maintain cap.

### Log File Cleanup
Manual or triggered by `config.setup_logging()`:
- Keeps maximum 10 timestamped log files
- Deletes oldest when limit exceeded

### qBittorrent Backup Cleanup
Manual via CLI. Keeps 10 most recent `.json.gz` backup files.

## Test Workflow

```mermaid
flowchart LR
    A[./guardian_monitor.py test] --> B[Test Scraper<br/>fetch series page]
    B --> C[Test Storage<br/>read/write JSON]
    C --> D[Test Discord<br/>send test message]
    D --> E[Print results]
```

## Scheduling

- **When**: Fridays (Guardian publishes at 08:00 CET)
- **Recommended cron**: `30 8 * * 5` and `0 10 * * 5` (two checks)
- **Idempotent**: Safe to run multiple times; processed articles tracked
