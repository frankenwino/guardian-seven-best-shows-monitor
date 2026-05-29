# Spec D: Add Type Checking (mypy)

## Goal
Configure mypy for static type checking and fix type errors to catch interface bugs between components.

## Requirements

### D1: mypy Configuration
- [ ] Add `[tool.mypy]` section to `pyproject.toml`
- [ ] Set `python_version = "3.10"` (minimum supported)
- [ ] Enable `warn_return_any = true`
- [ ] Enable `warn_unused_configs = true`
- [ ] Set `disallow_untyped_defs = false` (gradual adoption — don't require all functions typed)
- [ ] Add `mypy` to `requirements.txt`

### D2: Per-Module Overrides
- [ ] Allow `ignore_missing_imports` for third-party packages without stubs (`discord_webhook`, `bs4`)

### D3: Fix Critical Type Errors
- [ ] Run `mypy app/` and fix any errors in:
  - `config.py` (the global singleton)
  - `storage.py` (return types for JSON data)
  - `main.py` (component initialization)
- [ ] Do NOT require fixing all warnings — focus on errors only

### D4: Add Missing Return Type Annotations
- [ ] Add return type annotations to all public methods in `storage.py` (the most interface-heavy module)
- [ ] Add return type annotations to `GuardianMonitor` public methods

## Acceptance Criteria
- `mypy app/` exits with 0 errors (warnings acceptable)
- Configuration lives in `pyproject.toml` (no separate `mypy.ini`)
- Existing functionality unchanged — type checking is static analysis only
