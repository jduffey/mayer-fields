# Full-Stack Architecture Refactoring Proposal

This document reviews the four Codex branches that propose large-scale refactoring for the mayer-fields price-fetching app, then consolidates a single recommended refactoring plan.

**Branches reviewed:**
- `origin/codex/review-full-stack-architecture-for-price-fetching-app`
- `origin/codex/review-full-stack-architecture-for-price-fetching-app-kna8op`
- `origin/codex/review-full-stack-architecture-for-price-fetching-app-mogm0g`
- `origin/codex/review-full-stack-architecture-for-price-fetching-app-sgsf92`

---

## 1. Branch Reviews

### Branch 1: `review-full-stack-architecture-for-price-fetching-app`

**What it does:**
- Splits long date ranges into fixed-size windows (e.g. 300 days) so the Coinbase candles API is not asked for more than `MAX_WINDOW_DAYS` at once.
- Extracts `_normalize_candles`, `_sort_and_dedupe_candles`, and `_build_date_windows` in `coinbase_utils`.
- Uses `_sort_and_dedupe_candles` to merge and deduplicate candles across windows (by `time`).
- Changes `get_yesterday()` in `utils.py` to use `datetime.utcnow()` instead of `datetime.now()` for consistency with UTC.
- Adds tests for `_build_date_windows` and `_sort_and_dedupe_candles`.

**Likes:**
- **API pagination:** Directly addresses the real limit that the Exchange API has on range size; avoids failures or truncated data for long histories.
- **Deduping:** Handles overlapping or duplicate candles when stitching windows.
- **Small, testable helpers:** Clear single-purpose functions with unit tests.
- **UTC for “yesterday”:** Aligns “yesterday” with UTC day boundaries, which matches how the app treats dates elsewhere.

**Dislikes / gaps:**
- No domain model; candles remain plain dicts. That’s fine for a small codebase but doesn’t set up the rest of the app for clearer types.
- No change to how invalid candle payloads are handled (no validation or explicit error path).

**Problems / suggestions:**
- `_build_date_windows` uses exclusive end semantics; ensure callers and tests are aligned (e.g. “2021-01-01” to “2021-01-10” with `max_days=3` gives last window ending on “2021-01-10”). Current tests look correct.
- Consider making `MAX_WINDOW_DAYS` configurable (e.g. in `config.py`) so it can be tuned without code changes.

---

### Branch 2: `review-full-stack-architecture-for-price-fetching-app-kna8op`

**What it does:**
- Introduces a **domain layer** in `domain.py`: `TimeRange`, `Candle`, and `Series` (dataclasses).
- `TimeRange.from_dates(start_date, end_date)` builds UTC-aware ranges and exposes `start_iso()` / `end_iso()` for API calls.
- `normalize_coinbase_candles()` **validates** each raw candle and **raises** `ValueError` on invalid structure or values; returns a sorted list of `Candle` instances.
- `Series` holds asset, quote, granularity, and candles, with `to_history()` to produce the existing dict shape for compatibility.
- **Retry behavior:** On `requests.RequestException`, the code now retries (with backoff) instead of returning immediately; only after exhausting retries does it return the error.
- `get_yesterday()` and tests use `datetime.now(timezone.utc)` for UTC.
- Adds tests for invalid candle payload, retries on `RequestException`, and normalized candle sort order.

**Likes:**
- **Domain model:** Clear, immutable types (`Candle`, `Series`, `TimeRange`) improve readability and make data flow explicit.
- **Strict validation:** Failing fast on malformed API responses avoids silent wrong data downstream.
- **Retry fix:** Correctly retries on transient network errors instead of failing on first exception.
- **TimeRange encapsulation:** ISO formatting and date parsing live in one place; `coinbase_utils` stays focused on HTTP and orchestration.

**Dislikes / gaps:**
- No date-window pagination; a single large `start_date`–`end_date` could still hit API limits or timeouts.
- `TimeRange` enforces `tzinfo == timezone.utc`; fine for this app but strict if you ever need other timezones.

**Problems / suggestions:**
- `normalize_coinbase_candles` returns a **list** of `Candle`; the caller then builds a `Series` and calls `to_history()`. Naming could be clarified (e.g. “parse” vs “normalize”) to distinguish “raw → domain” from “domain → API dict.”
- Ensure `TimeRange.from_dates` uses the same date format as the rest of the app (e.g. `YYYY-MM-DD`) and documents it.

---

### Branch 3: `review-full-stack-architecture-for-price-fetching-app-mogm0g`

**What it does:**
- Adds `domain.py` with `TimeRange`, `Candle`, and `Series`; `TimeRange` is built in `coinbase_utils` via `_build_utc_date_range(start_date, end_date)`.
- **Parsing:** `parse_coinbase_candles()` **skips** invalid or malformed candles (no raise), and returns a list of `Candle`.
- `Series` has `.sorted()` returning a **new** `Series` (immutable style) and `.to_dict()` for the history dict.
- **Backoff:** Introduces `_sleep_with_backoff(attempt)` and adds **jitter** (random 0–`BACKOFF_SECONDS`) to sleep to reduce thundering herd.
- `Candle.date` uses `datetime.fromtimestamp(..., tz=timezone.utc)` for timezone-aware date string.
- `get_yesterday()` and tests use UTC.
- Adds a test that expects invalid candles (e.g. missing volume) to be skipped and only valid candles returned.

**Likes:**
- **Jitter on backoff:** Good practice for retries under load.
- **Domain types:** Same benefits as branch 2 (clear types, `Candle`, `Series`).
- **Immutable-style `Series.sorted()`:** Returns a new `Series`, which is easy to reason about.
- **Timezone-aware `Candle.date`:** Avoids local-time bugs.

**Dislikes / gaps:**
- **Silent skip of invalid candles:** Malformed or truncated API responses can lead to missing data with no warning; harder to detect API or schema issues.
- No date-window pagination.
- `TimeRange` has no `from_dates` or ISO helpers; formatting lives in `coinbase_utils` (less encapsulation than branch 2).

**Problems / suggestions:**
- Consider at least logging when a candle is skipped (e.g. index and raw slice) so production issues are visible.
- Optionally add a strict mode or a validation path that raises on invalid candles for critical flows.

---

### Branch 4: `review-full-stack-architecture-for-price-fetching-app-sgsf92`

**What it does:**
- Adds a minimal `domain.py`: `parse_utc_date()`, `TimeRange` with `contains_epoch(epoch_seconds)`, `Candle`, and `Series`.
- **Central date format:** `DATE_FORMAT = '%Y-%m-%d'` in domain and used in `utils.py` for `get_yesterday`, `get_date_range`, and `get_day_after` (DRY).
- **Filtering:** `_normalize_coinbase_candles()` in `coinbase_utils` only keeps candles whose epoch falls inside `TimeRange.contains_epoch()` (start ≤ timestamp < end), and **raises** `ValueError` on invalid candle structure (e.g. too few fields).
- Retry backoff gets **jitter** (same idea as branch 3).
- `get_yesterday()` and tests use UTC.
- Adds test that candles outside the requested range are excluded (e.g. request 2021-01-01 to 2021-01-03, assert only 2021-01-01 and 2021-01-02 in result).

**Likes:**
- **Single `DATE_FORMAT`:** One place for the date string format; reduces magic strings and drift between utils and domain.
- **Defensive filtering:** `contains_epoch` avoids including candles outside the requested range (e.g. from API quirks or timezone edge cases).
- **Fail on bad format:** Raising on invalid candle structure matches branch 2 and avoids silent corruption.
- **Small, focused domain:** Minimal surface area; easy to maintain.

**Dislikes / gaps:**
- No `TimeRange.start_iso()` / `end_iso()`; request timestamps are still built in `coinbase_utils` with f-strings (e.g. `f'{start_date}T00:00:00Z'`). Less encapsulation than branch 2.
- No date-window pagination for long ranges.

**Problems / suggestions:**
- The “filters to range” test assumes API returns candles for 2021-01-01, 02, 03 and that we only keep 01 and 02 when end is exclusive. That’s correct for “[start, end)” semantics; just keep this documented so future changes don’t accidentally make end inclusive.
- Consider adding `start_iso()` / `end_iso()` to `TimeRange` and using them in `coinbase_utils` so date–string formatting stays in domain.

---

## 2. Consolidated Refactoring Plan

The following plan merges the strongest ideas from all four branches into one coherent sequence. It keeps the current behavior of the app (same entrypoint, same outputs) while improving structure, robustness, and maintainability.

### 2.1 Principles

- **UTC everywhere for “today” / “yesterday”:** Use `datetime.now(timezone.utc)` and UTC day boundaries for date logic (all branches agree; adopt it).
- **Single date format:** Use a shared `DATE_FORMAT` (e.g. `'%Y-%m-%d'`) in one place and reuse it in `utils` and anywhere that formats dates (from branch 4).
- **Domain layer for candles and time:** Introduce a small domain module with typed structures and clear boundaries (from branches 2, 3, 4). Prefer the style that validates and raises on invalid data (branches 2 and 4).
- **Robust Coinbase integration:** Add windowed fetches for long ranges, retry on transient errors, and backoff with jitter (from branches 1 and 3).
- **Explicit validation:** Do not silently drop malformed candles in the main path; validate and raise (or log and raise) so API/schema issues are visible (from branches 2 and 4).

### 2.2 Proposed Steps

**Phase A – Foundation (dates and time)**

1. **UTC and shared date format**
   - In `utils.py`, change `get_yesterday()` to use `datetime.now(timezone.utc)` (and keep the same return format).
   - Introduce a single `DATE_FORMAT` constant (e.g. in a small `domain` or `constants` module, or at the top of `utils` if you prefer). Use it in `get_yesterday`, `get_date_range`, and `get_day_after`.
   - Update `utils_test.py` (and any other tests that depend on “today”) to use `datetime.now(timezone.utc)` so tests are deterministic where possible.

**Phase B – Domain layer**

2. **Add `domain.py`**
   - **`parse_utc_date(date_str: str) -> datetime`**  
     Parse `YYYY-MM-DD` to UTC midnight; use `DATE_FORMAT`.
   - **`TimeRange`** (frozen dataclass)
     - `start`, `end`: timezone-aware UTC datetimes.
     - `from_dates(start_date: str, end_date: str) -> TimeRange` (class method).
     - `start_iso()`, `end_iso()` returning strings for the Exchange API (e.g. `YYYY-MM-DDTHH:MM:SSZ` or equivalent).
     - `contains_epoch(epoch_seconds: int) -> bool` (start ≤ timestamp < end) for optional filtering (branch 4).
   - **`Candle`** (frozen dataclass)  
     Fields: `time`, `open`, `high`, `low`, `close`, `volume`.  
     Property `date` (str) using `DATE_FORMAT` and timezone-aware conversion.  
     Method `to_dict()` for the current dict shape used by callers.
   - **`Series`** (frozen dataclass)  
     Fields: `asset`, `quote`, `granularity`, `candles: List[Candle]`.  
     Method `to_history()` (or `to_dict()`) that returns the existing history dict structure so `coinbase_utils` and callers do not need to change their expectations.

3. **Candle parsing in domain**
   - Add a single function, e.g. **`parse_coinbase_candles(payload) -> List[Candle]`**, that:
     - Iterates over the raw list from the API.
     - Validates each element (e.g. list-like, length ≥ 6, numeric types). **Raise `ValueError`** with a clear message (e.g. index and reason) on invalid structure or values; do not silently skip (align with branches 2 and 4).
     - Builds `Candle` instances, sorts by `time`, and returns the list.
   - Optionally: add a helper that builds a `Series(asset, quote, granularity, candles)` from this list so `coinbase_utils` stays thin.

**Phase C – Coinbase utils**

4. **Use domain in `coinbase_utils`**
   - In `get_price_history`:
     - Build `TimeRange` via `TimeRange.from_dates(start_date, end_date)` and use `start_iso()` / `end_iso()` for the HTTP request (branch 2 style).
     - After receiving the JSON list of candles, call `parse_coinbase_candles(...)` and build a `Series`; return `series.to_history()` (or equivalent) so the rest of the app still sees the same dict shape.
   - Optionally filter candles with `time_range.contains_epoch(candle.time)` before building `Series` if you want to enforce strict range semantics (branch 4); document that the API is assumed to return [start, end) or adjust filtering accordingly.

5. **Date-window pagination (branch 1)**
   - Add a constant, e.g. `MAX_WINDOW_DAYS = 300` (or configurable in `config.py`).
   - Add `_build_date_windows(start_date, end_date, max_days)` that returns a list of `(window_start, window_end)` string pairs, with each window at most `max_days` long and using the same date format. Use exclusive-end semantics if that matches the API.
   - In `get_price_history`, if the requested range is longer than `MAX_WINDOW_DAYS`, split into windows. For each window, call the candles API, parse with `parse_coinbase_candles`, and collect all `Candle` objects. Merge and deduplicate by `time` (e.g. dict keyed by `time` then sort), then build one `Series` and return `to_history()`.
   - Add unit tests for `_build_date_windows` and for merge/dedupe (e.g. overlapping windows or duplicate timestamps).

6. **Retries and backoff**
   - Keep existing retry logic for HTTP status codes (e.g. 429, 5xx).
   - **Fix RequestException handling:** On `requests.RequestException`, sleep with backoff and retry up to `MAX_RETRIES` times before returning an error (branch 2).
   - **Add jitter:** When sleeping between retries, add a small random jitter (e.g. 0–`BACKOFF_SECONDS`) to the backoff delay (branch 3) to avoid thundering herd. Use a helper like `_sleep_with_backoff(attempt)` so the retry loop stays readable.

**Phase D – Tests and cleanup**

7. **Tests**
   - Add or extend tests for: `parse_coinbase_candles` (valid payload, invalid structure, invalid values), `TimeRange.from_dates` and `contains_epoch`, `_build_date_windows`, merge/dedupe of candles across windows, and retry behavior on `RequestException` (and optionally on 5xx).
   - Ensure `get_yesterday` and any date-dependent tests use UTC so behavior is consistent and testable.

8. **Minor cleanups**
   - Fix the typo in `printer.check_compatibility_of_price_data_with_worksheet` message (“compatability” → “compatibility”) if not already done.
   - Consider adding a short comment in `main.py` or README that the app uses UTC for “yesterday” and for all date boundaries.

### 2.3 What we are not adopting (and why)

- **Silent skip of invalid candles (branch 3):** Prefer explicit validation and raise; optional logging can be added later if you want to log-and-skip in a separate “lenient” path.
- **Strict `TimeRange` tz check (branch 2):** Requiring `tzinfo == timezone.utc` is reasonable; we can adopt it in `TimeRange.__post_init__` if we want to reject naive or wrong-timezone ranges.
- **Building timestamps in `coinbase_utils` (branch 4 as-is):** Prefer moving ISO formatting into `TimeRange.start_iso()` / `end_iso()` for a single place that knows how we talk to the API.

### 2.4 Implementation order

1. Phase A (UTC + `DATE_FORMAT`).
2. Phase B (domain types + `parse_coinbase_candles`).
3. Phase C.4 (wire domain into `get_price_history` without pagination).
4. Phase C.6 (retry + jitter).
5. Phase C.5 (date windows + merge/dedupe).
6. Phase D (tests and small cleanups).

This order keeps each step reviewable and allows you to run the app after each phase with the same external behavior.

---

## 3. Summary Table

| Topic                 | Branch 1 | Branch 2 | Branch 3 | Branch 4 | Proposal                          |
|----------------------|----------|----------|----------|----------|-----------------------------------|
| Date windows         | ✅       | ❌       | ❌       | ❌       | Adopt (Branch 1)                  |
| Domain types         | ❌       | ✅       | ✅       | ✅       | Adopt (B2/B4 style)               |
| UTC yesterday        | ✅       | ✅       | ✅       | ✅       | Adopt                             |
| DATE_FORMAT constant | ❌       | ❌       | ❌       | ✅       | Adopt (Branch 4)                  |
| Validate candles     | ❌       | ✅ raise | Skip     | ✅ raise | Adopt raise (B2/B4)               |
| Retry on RequestException | ✅   | ✅       | ❌       | ❌       | Adopt (Branch 2)                  |
| Backoff jitter       | ❌       | ❌       | ✅       | ✅       | Adopt (Branch 3/4)                 |
| TimeRange ISO        | ❌       | ✅       | ❌       | ❌       | Adopt (Branch 2)                  |
| contains_epoch       | ❌       | ❌       | ❌       | ✅       | Adopt optional (Branch 4)         |

This proposal gives you a single refactoring plan that keeps the best parts of each branch while avoiding silent failures and keeping the codebase consistent and testable.
