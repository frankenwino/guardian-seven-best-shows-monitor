# Documentation Index

<!-- metadata:type=index, audience=ai-agents, updated=2026-05-29 -->

## How to Use This Documentation (AI Assistants)

This index is your primary reference for the **Guardian Seven Best Shows Monitor** codebase. Use it to determine which file contains the information you need, then read that file for details.

**Quick decision guide:**
- "How does the system work?" → `architecture.md`
- "What does component X do?" → `components.md`
- "What CLI commands exist?" → `interfaces.md`
- "What data is stored/passed around?" → `data_models.md`
- "What happens when the app runs?" → `workflows.md`
- "What libraries are used?" → `dependencies.md`
- "What is this project?" → `codebase_info.md`

## Project Summary

A Python CLI tool that monitors The Guardian's weekly "Seven Best Shows to Stream" article series. On each run (typically cron-scheduled on Fridays), it scrapes the latest article, extracts show recommendations, persists them to JSON, sends Discord notifications, and optionally creates qBittorrent download rules.

## Documentation Files

| File | Purpose | Key Content |
|------|---------|-------------|
| [codebase_info.md](codebase_info.md) | Project overview | Tech stack, directory layout, execution model, config sources |
| [architecture.md](architecture.md) | System design | Component diagram, orchestrator pattern, interaction sequence, error handling |
| [components.md](components.md) | Component details | Class diagrams, responsibilities, method signatures for all 7 components |
| [interfaces.md](interfaces.md) | APIs and CLIs | All CLI commands, external integrations (Guardian, Discord, qBittorrent) |
| [data_models.md](data_models.md) | Data structures | Article/show dicts, JSON file schemas, qBittorrent rule format, retention policies |
| [workflows.md](workflows.md) | Processes | Primary run flow, qBittorrent rules flow, scraper parsing strategy, scheduling |
| [dependencies.md](dependencies.md) | External deps | Python packages, stdlib usage, system deps, dependency graph, installation |

## Key Entry Points

| File | Role |
|------|------|
| `guardian_monitor.py` | CLI entry point — maps commands to `main.py` |
| `app/main.py` | Application logic — `GuardianMonitor` class |
| `app/config.py` | Configuration singleton — imported by all modules |
| `app/qbittorrent_rules.py` | Standalone CLI for qBittorrent rule management |
| `app/storage_utils.py` | Standalone CLI for data management |

## Cross-References

- **Config affects everything**: Changes to `config.ini` or `.env` impact scraper URLs, timeouts, Discord, logging, and storage paths. See `codebase_info.md` → Configuration Sources.
- **Storage is central**: Both the main workflow and utility scripts operate on the same JSON files. See `data_models.md` for schemas.
- **qBittorrent is optional**: The system works without it. It's imported with try/except in `main.py`. See `components.md` → QBittorrentRulesManager.
- **Scraper is fragile**: Multiple parsing strategies exist because The Guardian's HTML format changes. See `workflows.md` → Scraper Parsing Strategy.
