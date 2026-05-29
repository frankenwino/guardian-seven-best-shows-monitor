# Review Notes

<!-- metadata:type=review, audience=ai-agents, updated=2026-05-29 -->

## Consistency Check

✅ **Passed** — No inconsistencies found across documents:
- Component names are consistent across all files (GuardianMonitor, GuardianScraper, ShowDataStorage, GuardianDiscordBot, QBittorrentRulesManager, Config, LogManager)
- File paths are consistent (app/main.py, data/, logs/, etc.)
- Data flow descriptions align between architecture.md, workflows.md, and data_models.md
- CLI commands documented in interfaces.md match actual argparse definitions in source code
- Dependency versions match requirements.txt

## Completeness Check

### Well-Documented Areas ✅
- System architecture and component relationships
- CLI interfaces for all entry points
- Data persistence schemas and retention policies
- Primary workflow (check for new shows)
- qBittorrent rules management workflow
- External integrations (Guardian, Discord, qBittorrent)
- Configuration system

### Gaps Identified ⚠️

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| No formal test framework (pytest) configured | Medium | Tests exist (`test_integration.py`, `test_discord_sample.py`) but no pytest config, no `conftest.py`, no CI pipeline |
| `DISCORD_BOT_TOKEN` usage undocumented in code | Low | `.env.example` mentions it for "bulk-deleting channel messages" but no code in the repo uses it |
| Scraper parsing methods not unit-tested | Medium | The cascading parsing strategy is complex and fragile — would benefit from test fixtures |
| No type checking configuration (mypy/pyright) | Low | Type hints are used inconsistently — some methods have them, others don't |
| `demo_restart.py` and `test_qbt_restart.py` purpose unclear | Low | Root-level test/demo scripts not documented in any interface |
| No error recovery for corrupted JSON files | Medium | If `shows_history.json` becomes corrupted, the system will crash on next run |
| `config.ini` is tracked in git with actual values | Low | Unlike `.env`, the config file is committed — changes to defaults affect all clones |

## Recommendations

1. **Add pytest configuration** — Create `pytest.ini` or `pyproject.toml` with test discovery settings. The existing test files use `main()` functions rather than pytest conventions.
2. **Add JSON validation** — Consider try/except around all JSON loads with fallback to empty state rather than crashing.
3. **Document demo/test scripts** — Add a brief note in README or interfaces about `demo_restart.py` and `test_qbt_restart.py`.
4. **Consider type checking** — Adding a `py.typed` marker and mypy config would catch bugs in the data-passing interfaces.
