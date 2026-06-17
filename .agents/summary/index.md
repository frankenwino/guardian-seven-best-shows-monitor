# Documentation Index

<!-- metadata:type=index, scope=navigation -->

## How to Use This Documentation

This directory contains structured documentation for the Guardian Seven Best Shows Monitor. **Start here** to find the right file for your question.

### Quick Reference

| Question | Consult |
|----------|---------|
| "What does this project do?" | `codebase_info.md` |
| "How are components connected?" | `architecture.md` |
| "What does class X do?" | `components.md` |
| "What CLI commands are available?" | `interfaces.md` |
| "What's the JSON format for X?" | `data_models.md` |
| "What happens when the cron runs?" | `workflows.md` |
| "What libraries are used?" | `dependencies.md` |

## File Summaries

### codebase_info.md
Project identity, technology stack, entry points, and high-level metrics. Read first for project context.

### architecture.md
System-level diagrams showing component relationships, data flow (sequence diagram), module dependency graph, and key design patterns (orchestrator, config singleton, graceful degradation, idempotent execution, cascading parse strategies).

### components.md
Full class diagram with method signatures for all 6 classes. Includes responsibility descriptions for each component explaining what it does and why.

### interfaces.md
All CLI commands (4 entry points with their subcommands and flags), external system integrations (Guardian website, Discord API, qBittorrent process/config), and Python API examples for programmatic usage.

### data_models.md
JSON schemas for all 4 data files (shows_history, processed_articles, last_checked, qBittorrent rules). Entity relationship diagram. Internal Python dict structures. File storage strategy notes.

### workflows.md
Flowcharts for: main execution cycle, qBittorrent rule creation (with rollback), scraper parsing strategy cascade, storage cleanup processes, test workflow, and scheduling recommendations.

### dependencies.md
Runtime and dev dependency tables with versions and purposes. Standard library usage summary. Full dependency graph (Mermaid). System requirements.

## Cross-References

- **Config loading** → `architecture.md` (Config Singleton pattern) + `components.md` (Config class)
- **Discord notifications** → `interfaces.md` (API) + `components.md` (GuardianDiscordBot) + `workflows.md` (notification step in main flow)
- **qBittorrent integration** → `interfaces.md` (CLI) + `workflows.md` (rule creation flowchart) + `data_models.md` (rules JSON schema)
- **Data persistence** → `data_models.md` (schemas) + `components.md` (ShowDataStorage) + `workflows.md` (cleanup)
