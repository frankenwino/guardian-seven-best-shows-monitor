# Architecture

<!-- metadata:type=architecture, scope=system -->

## System Overview

```mermaid
graph TB
    subgraph "Entry Points"
        CLI[guardian_monitor.py]
        QBT_CLI[qbittorrent_rules.py]
        STOR_CLI[storage_utils.py]
        LOG_CLI[log_manager.py]
    end

    subgraph "Core Application"
        M[GuardianMonitor<br/>Orchestrator]
        S[GuardianScraper]
        ST[ShowDataStorage]
        D[GuardianDiscordBot]
        Q[QBittorrentRulesManager]
        C[Config Singleton]
    end

    subgraph "External Systems"
        GUARDIAN[The Guardian<br/>Website]
        DISCORD[Discord<br/>Webhook API]
        QBT[qBittorrent<br/>Process + Config]
    end

    subgraph "Persistence"
        DATA[data/*.json]
        LOGS[logs/*.log]
    end

    CLI --> M
    QBT_CLI --> Q
    STOR_CLI --> ST
    LOG_CLI --> LOGS

    M --> S
    M --> ST
    M --> D
    M --> Q
    C -.-> M
    C -.-> S
    C -.-> D

    S --> GUARDIAN
    D --> DISCORD
    Q --> QBT
    ST --> DATA
```

## Design Patterns

### Orchestrator Pattern
`GuardianMonitor` in `app/main.py` coordinates all components. Each component is independently testable and has no cross-dependencies.

### Config Singleton
`app/config.py` exports a global `config` instance loaded at import time. All modules import from it. Sources: `config.ini` (tracked) + `.env` (secrets).

### Graceful Degradation
Optional features (Discord, qBittorrent) are checked at runtime. Missing configuration disables the feature rather than crashing.

### Idempotent Execution
`processed_articles.json` tracks which articles have been processed. Repeated runs are safe — duplicate processing is prevented.

### Cascading Parse Strategies
The scraper attempts multiple HTML parsing strategies in order, because Guardian article formats vary:
1. H2 headings with show details
2. Numbered H2/H3 headings
3. Bold numbered text patterns
4. Full body text parsing

### Process Lifecycle Management
qBittorrent rules require direct file manipulation of qBittorrent's config. The manager implements:
- Close process (graceful → force)
- Backup existing config (gzip compressed)
- Write new rules
- Restart process
- Rollback on failure

## Module Dependencies

```mermaid
graph LR
    main --> config
    main --> scraper
    main --> storage
    main --> discord_bot
    main --> qbittorrent_rules
    scraper --> config
    discord_bot --> config
    qbittorrent_rules --> storage
```

## Data Flow

```mermaid
sequenceDiagram
    participant Cron
    participant Monitor
    participant Scraper
    participant Storage
    participant Discord
    participant QBT

    Cron->>Monitor: Execute
    Monitor->>Scraper: get_series_articles()
    Scraper->>Scraper: fetch_page() per series URL
    Scraper-->>Monitor: articles[]
    
    loop Each article
        Monitor->>Storage: is_article_processed(url)?
        alt New article
            Monitor->>Scraper: parse_show_recommendations(url)
            Scraper-->>Monitor: shows[]
            Monitor->>Storage: save_shows_data(shows)
            Monitor->>Storage: add_processed_article(url)
            Monitor->>Discord: send_new_shows_alert(shows)
            Monitor->>QBT: create_missing_rules(shows)
        end
    end
```
