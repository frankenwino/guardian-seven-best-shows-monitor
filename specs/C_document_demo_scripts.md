# Spec C: Document Demo/Test Scripts

## Goal
Document the purpose and usage of root-level demo/test scripts that are currently undocumented.

## Requirements

### C1: README Addition
- [ ] Add a "Demo & Test Scripts" section to `README.md` (after "Storage Management", before "Project Structure")
- [ ] Document `demo_restart.py`: demonstrates qBittorrent close/restart workflow
- [ ] Document `test_qbt_restart.py`: verifies qBittorrent process control works
- [ ] Document `app/test_discord_sample.py`: sends sample Discord notifications for visual verification
- [ ] Include a warning that these scripts interact with real processes/services

### C2: Script Docstrings
- [ ] Verify each script has a clear module-level docstring (already present — no changes needed if adequate)

## Acceptance Criteria
- README.md contains a section explaining all 3 demo/test scripts
- Each entry includes: purpose, usage command, and any prerequisites (e.g., "qBittorrent must be installed")
