# Architecture

<!-- metadata:type=architecture, audience=ai-agents, updated=2026-05-29 -->

## System Architecture

```mermaid
graph TB
    CRON[Cron Scheduler] -->|Triggers| CLI[guardian_monitor.py<br/>CLI Entry Point]
    CLI -->|Delegates to| MAIN[GuardianMonitor<br/>app/main.py]
    
    MAIN --> SCRAPER[GuardianScraper<br/>app/scraper.py]
    MAIN --> STORAGE[ShowDataStorage<br/>app/storage.py]
    MAIN --> DISCORD[GuardianDiscordBot<br/>app/discord_bot.py]
    MAIN --> QBT[QBittorrentRulesManager<br/>app/qbittorrent_rules.py]
    
    SCRAPER -->|HTTP GET| GUARDIAN[The Guardian Website]
    DISCORD -->|Webhook POST| DISCORD_API[Discord API]
    QBT -->|File I/O| QBT_CONFIG[qBittorrent Config Files]
    QBT -->|subprocess| QBT_PROC[qBittorrent Process]
    STORAGE -->|JSON R/W| DATA[(data/ directory)]
    
    CONFIG[Config Singleton<br/>app/config.py] -.->|Provides settings| MAIN
    CONFIG -.-> SCRAPER
    CONFIG -.-> DISCORD
    
    ENV[.env] -.->|Secrets| CONFIG
    INI[config.ini] -.->|Settings| CONFIG
```

## Design Patterns

### Orchestrator Pattern
`GuardianMonitor` (app/main.py) acts as the central orchestrator, coordinating all components in a defined sequence: scrape → store → notify → manage rules.

### Singleton Configuration
`Config` class in app/config.py instantiates a module-level `config` object imported by all modules. Loads from both `config.ini` (settings) and `.env` (secrets).

### Graceful Degradation
- Discord notifications are optional — the system works without them
- qBittorrent integration is optional — imported with try/except
- Error notifications are sent to Discord if configured, but failures don't halt execution

### Idempotent Execution
Each run checks `processed_articles.json` to determine if the latest article has already been handled, preventing duplicate notifications and data entries.

## Component Interaction Flow

```mermaid
sequenceDiagram
    participant Cron
    participant CLI as guardian_monitor.py
    participant Monitor as GuardianMonitor
    participant Scraper as GuardianScraper
    participant Storage as ShowDataStorage
    participant Discord as GuardianDiscordBot
    participant QBT as QBittorrentRulesManager

    Cron->>CLI: Execute
    CLI->>Monitor: run()
    Monitor->>Scraper: get_series_articles()
    Scraper-->>Monitor: articles[]
    Monitor->>Storage: is_article_processed(url)
    Storage-->>Monitor: false (new article)
    Monitor->>Scraper: parse_show_recommendations(url)
    Scraper-->>Monitor: shows[]
    Monitor->>Storage: save_shows_data()
    Monitor->>Storage: add_processed_article()
    Monitor->>Discord: send_new_shows_alert()
    Monitor->>QBT: check_existing_rules() / create rules
```

## Error Handling Strategy

- Each component catches its own exceptions and logs them
- The orchestrator catches component failures and continues with remaining steps
- Discord error notifications are sent for critical failures (if configured)
- qBittorrent process management includes rollback (restart if closed)
