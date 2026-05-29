# Spec B: Add JSON Validation/Recovery

## Goal
Prevent crashes when JSON data files are corrupted or malformed. The system should recover gracefully and continue operating.

## Requirements

### B1: Graceful JSON Loading
- [ ] All `json.load()` calls in `storage.py` must be wrapped with recovery logic
- [ ] On `json.JSONDecodeError`, log a warning and return the empty/default state for that file
- [ ] On `IOError`/`PermissionError`, log an error and return the empty/default state

### B2: Backup Before Overwrite
- [ ] Before writing to any data file, if the file exists and is non-empty, create a `.bak` copy
- [ ] Keep only 1 `.bak` per data file (overwrite previous backup)

### B3: Default States
- [ ] `last_checked.json` → returns `None`
- [ ] `processed_articles.json` → returns `{"processed_urls": [], "articles_info": {}}`
- [ ] `shows_history.json` → returns `[]`

### B4: Corruption Detection
- [ ] After loading JSON, validate the expected top-level structure (dict vs list, required keys)
- [ ] If structure is wrong (e.g., `shows_history.json` contains a dict instead of a list), treat as corrupted and return default state

## Acceptance Criteria
- A test creates each data file with invalid JSON content (e.g., `"{broken"`) and verifies the system returns the default state without raising
- A test creates each data file with valid JSON but wrong structure and verifies graceful fallback
- The `.bak` file is created before any write operation
- All existing tests continue to pass
