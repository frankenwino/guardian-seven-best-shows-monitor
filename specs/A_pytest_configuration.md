# Spec A: Add pytest Configuration

## Goal
Set up pytest as the test framework with proper configuration, convert existing tests to pytest conventions, and add unit tests for the scraper's parsing logic.

## Requirements

### A1: pytest Configuration
- [ ] Create `pyproject.toml` with `[tool.pytest.ini_options]` section
- [ ] Configure test discovery: `testpaths = ["tests"]`
- [ ] Add `pytest` to `requirements.txt`
- [ ] Create `tests/` directory at project root
- [ ] Create `tests/conftest.py` with shared fixtures

### A2: Convert Existing Tests
- [ ] Move/adapt `app/test_integration.py` → `tests/test_integration.py`
- [ ] Convert `main()` entry points to proper `test_` functions
- [ ] Tests must not require user input (no `input()` calls)
- [ ] Tests must not send real Discord notifications or make network calls (use mocking where needed)

### A3: Scraper Unit Tests
- [ ] Create `tests/test_scraper.py` with unit tests for parsing logic
- [ ] Create `tests/fixtures/` directory with sample HTML files
- [ ] Test `_is_seven_best_shows_article()` with valid and invalid URLs
- [ ] Test `_extract_date_from_url()` with various URL patterns
- [ ] Test `parse_show_recommendations()` using a saved HTML fixture (no network)
- [ ] Test the cascading parsing strategy (h2 → numbered → bold → body)

### A4: Storage Unit Tests
- [ ] Create `tests/test_storage.py`
- [ ] Test `is_article_processed()` with empty and populated state
- [ ] Test `add_processed_article()` writes correct JSON
- [ ] Test `_cleanup_processed_articles()` caps at 100 entries
- [ ] Use `tmp_path` fixture for isolated file operations

## Acceptance Criteria
- `pytest` runs from project root and discovers all tests
- All tests pass without network access (except tests explicitly marked `@pytest.mark.integration`)
- Integration tests are marked and skippable: `pytest -m "not integration"`
- No test requires user interaction
