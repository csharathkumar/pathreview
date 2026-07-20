# Journal

## Week 7 — Issue selection

**Issue link:** [#146 — PII scrubber fails to redact parenthesized US phone numbers](https://github.com/ascherj/pathreview/issues/146)

**Issue title:** PII scrubber fails to redact parenthesized US phone numbers

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The PII scrubber in `safety/pii_scrubber.py` uses a regex for US phone numbers that only matches dashed formats like `555-123-4567`, so it misses the equally common parenthesized format `(555) 123-4567`. As a result, `scrub()` leaves parenthesized numbers completely unredacted in output text, and `detect()` reports no PII at all when given text containing only a parenthesized number — a false negative in a safety-critical component whose whole job is to catch this kind of data. A successful fix updates the phone-number pattern so it recognizes both formats (and the mixed separators/spacing that come with parentheses), and gets the related failing tests passing: `test_us_phone_number_redaction`, `test_us_phone_formats`, `test_detect_phone_pii`, and `test_phone_at_start_of_text` in `tests/unit/test_pii_scrubber.py`.

**Scope reasoning ("Is this right for me?" checklist):**
This is a self-contained, well-scoped bug in a single file (`safety/pii_scrubber.py`) with existing failing tests that define done clearly, no new dependencies or schema changes, and a narrow blast radius (one regex pattern). It's tagged `tier-1` / `good first issue`, matching a first contribution to this codebase. Note: PR #162 (open, unmerged, unreviewed) also claims to fix this issue as part of a multi-bug PR — that's expected in an open-source project where multiple contributors can pick up the same issue, so I'm proceeding with my own independent fix rather than treating it as already resolved.

**Branch name:** `fix/146-parenthesized-phone-scrub`

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger
