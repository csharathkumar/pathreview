# Journal

## Week 7 — Issue selection

**Issue link:** [#146 — PII scrubber fails to redact parenthesized US phone numbers](https://github.com/ascherj/pathreview/issues/146)

**Issue title:** PII scrubber fails to redact parenthesized US phone numbers

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The PII scrubber in `safety/pii_scrubber.py` has a `phone_us` regex that already accounts for optional parentheses around the area code, but the separator it expects right after the closing `)` is limited to `-` or `.` — a plain space isn't allowed there. Since the conventional parenthesized format is written as `(555) 123-4567`, with a space after the `)`, the match breaks at exactly that point and the number passes through unredacted. `scrub()` leaves it in the output text, and `detect()` returns an empty list for text that contains only a parenthesized number, which is a real gap in a safety component whose entire job is catching this. A successful fix widens the separator character class (or otherwise permits whitespace there) so both `(555) 123-4567` and `(555)123-4567` are recognized alongside the dashed and dotted formats, and gets the related failing tests passing: `test_us_phone_number_redaction`, `test_us_phone_formats`, `test_detect_phone_pii`, and `test_phone_at_start_of_text` in `tests/unit/test_pii_scrubber.py`.

**"Is this right for me?" checklist reasoning:**

*Part 1 — Understanding the issue:* Paraphrased without re-reading: the phone regex in the scrubber doesn't allow a space after the closing parenthesis in `(555) 123-4567`, so that common format slips through both `scrub()` and `detect()` unredacted. Affected area: `safety/` (matches the issue's `safety` label). I opened `safety/pii_scrubber.py` and confirmed the `PII_PATTERNS["phone_us"]` regex and both methods that use it (`scrub`, `detect`) exist as described. Before/after: before the fix, `scrub("Call me at (555) 123-4567")` returns the phone number untouched and `detect(...)` returns `[]`; after the fix, both should treat it the same as the dashed format — `scrub` replaces it with `[REDACTED]`, `detect` returns a `phone_us` entry with the right `start`/`end` offsets.

*Part 2 — Tier fit:* Tagged `tier-1` / `good first issue` on the tracker, and this is my first contribution to this codebase, so Tier 1 is the right level — no cross-module or system-wide understanding needed, just this one regex.

*Part 3 — Codebase readiness:* Read the full `phone_us` pattern (not just the file) and traced how it flows through `scrub()` and `detect()`. Read `tests/unit/test_pii_scrubber.py` end-to-end — tests follow a simple `PIIScrubber()` fixture + `scrub`/`detect` call + assertion pattern, with `test_us_phone_formats` looping over a list of format strings, which is exactly where a parenthesized-with-space case belongs. I can already sketch the fix (adjust the separator character class in the regex) without needing to look anything else up.

*Part 4 — Scope and time:* Checked issue #146's comments and found no other explicit claim comments, though PR #162 (open, unmerged, no reviews yet) bundles a fix for #146 in with three other unrelated issues — normal for an open-source tracker where claims aren't exclusive. I'm proceeding with my own independent fix rather than treating it as resolved, and logged my claim in the cohort ledger per the Claims column. Estimated time: 1–2 hours for the regex change plus new/updated tests, well inside the 3–6 hour Tier 1 range and comfortably within the Week 8–9 window. No "blocked by" references or unresolved dependencies on the issue.

**Branch name:** `fix/146-parenthesized-phone-scrub`

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger
