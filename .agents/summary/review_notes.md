# Review Notes

<!-- metadata:type=review, scope=quality -->

## Consistency Check

✅ **No inconsistencies found** across documentation files.

- Component names match across architecture.md, components.md, and interfaces.md
- Data model field names align with descriptions in workflows.md
- CLI commands documented in interfaces.md match entry points in codebase_info.md
- Dependency versions match requirements.txt

## Completeness Check

### Well-Documented Areas
- ✅ All 5 main classes fully documented with method signatures
- ✅ All 4 CLI entry points with commands and flags
- ✅ All JSON data schemas with examples
- ✅ Main workflow and qBittorrent workflow with flowcharts
- ✅ External integrations documented

### Gaps Identified

| Area | Gap | Impact |
|------|-----|--------|
| Error handling | Not documented which errors trigger Discord error notifications vs silent logging | Low — code is readable |
| Config validation | `_validate_config()` rules not enumerated | Low — fail-fast on startup |
| Scraper strategies | Individual parse method logic not fully traced | Medium — important for debugging parse failures |
| HTTP retry behavior | `retry_attempts`/`retry_delay` from config.ini referenced but implementation not verified in scraper | Low |
| Test coverage | No pytest coverage reporting configured | Low — project is small |

### Recommendations

1. **If scraper parsing breaks**: Consult `app/scraper.py` methods `_parse_show_from_heading`, `_parse_show_from_guardian_heading`, `_parse_shows_from_body` — the cascading strategy means new formats need a new strategy function.
2. **If qBittorrent workflow fails**: Check `show_backup_status()` output and manual `backups` command. Rollback is automatic.
3. **Processed articles cap**: Currently 100. Change via `cleanup_processed_articles_manual(max_entries=N)` or the storage_utils CLI.
