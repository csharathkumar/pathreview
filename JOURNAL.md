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

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** [e7a8280](https://github.com/csharathkumar/pathreview/commit/e7a8280038849d82ebdecb5ebb84fa2bdec34274)

**Reproduction summary:**
Ran `scripts/repro_issue_146.py` against the live `PIIScrubber` class: `scrub("Call me at (555) 123-4567 or 555-123-4567")` redacted the dashed number but left `(555) 123-4567` untouched, and `detect("Call me at (555) 123-4567")` returned `[]` with no phone detected at all. Root cause confirmed in `safety/pii_scrubber.py`: the `phone_us` regex allows `-` or `.` right after the closing `)`, but not a space, and the conventional parenthesized format always has a space there.

**PLAN.md link:** [PLAN.md](https://github.com/csharathkumar/pathreview/blob/fix/146-parenthesized-phone-scrub/PLAN.md)

**Walkthrough video (recommended):** (not recorded)

**Blockers or open questions:**
Still deciding between the smallest possible regex change (widen the separator character class to include whitespace) versus splitting `phone_us` into explicit dashed/dotted vs. parenthesized alternatives for readability. Need to verify the widened pattern doesn't introduce false positives on unrelated space-separated digit groups before committing to the simplest fix — see Risks & Unknowns in `PLAN.md`.

## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Implemented the fix: replaced the `phone_us` regex's leading `\b` with `(?<!\w)` so a leading `(`/`+` is included in the redacted match, and widened the separator character class from `[-.]?` to `[-.\s]?` so whitespace is accepted. This resolved all 4 originally-failing tests plus a second latent bug I found in the same regex (`+1 555 123 4567` was also failing, for the same root cause). Added 3 new tests (`test_detect_parenthesized_phone_only`, `test_scrub_parenthesized_and_dashed_phone_together`, `test_phone_us_space_separated_tradeoff`) and type-annotated all existing test methods to satisfy the repo's mypy pre-commit hook. Along the way, fixed several pre-existing lint issues confined to the two files I'm editing, and confirmed (via `git stash` before/after comparison) that one remaining test failure (`test_mixed_pii_and_text`) is a pre-existing, unrelated bug in the `street_address` pattern, not something I introduced. Pushed the fix and opened a draft PR (#491).

**Next steps:**
Fill in the PR description (currently just the empty template), get peer/mentor review in Slack, address any feedback, then mark the PR ready for review before Sunday's deadline.

**Blockers:**
None currently. Earlier hiccups (zsh mangling a commit message containing `!`, and `make format` reformatting 51 unrelated files repo-wide) are resolved — commits are clean and scoped to just the 4 relevant files.

---

### Check-in 2 (end of week)

**PR link:** [#491 — fix(safety): redact parenthesized and space-separated US phone numbers](https://github.com/ascherj/pathreview/pull/491)

**Branch:** `fix/146-parenthesized-phone-scrub`

**What you built:**
Fixed the `phone_us` regex in `safety/pii_scrubber.py` so `scrub()`/`detect()` correctly catch parenthesized US phone numbers like `(555) 123-4567`, plus a second latent gap I found in the same pattern affecting space-separated numbers like `+1 555 123 4567`. The fix replaces the leading `\b` with `(?<!\w)` (so a leading `(`/`+` is included in the redacted match instead of left behind) and widens the separator character class to accept whitespace alongside `-`/`.`.

**Tests added or updated:**
`tests/unit/test_pii_scrubber.py` — added `test_detect_parenthesized_phone_only`, `test_scrub_parenthesized_and_dashed_phone_together`, and `test_phone_us_space_separated_tradeoff` (documents the accepted over-redaction trade-off from widening the separator class). Also added type annotations to all 29 existing test methods to satisfy the repo's mypy pre-commit hook.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes
(Scoped to the 4 files this PR touches: `ruff`, `black --check`, and `mypy` all clean; `pytest tests/unit/test_pii_scrubber.py` is 27 passed / 1 failed. The 1 failure, `test_mixed_pii_and_text`, is a pre-existing bug in the unrelated `street_address` pattern — confirmed via `git stash` comparison that it fails identically on `main`, before this PR's changes. Per this week's guidance on pre-existing failures, "passes" here means no new failures were introduced; documented in the PR's "Notes for Reviewers" along with ~159 pre-existing repo-wide `ruff` errors and other pre-existing `make test-unit` failures in unrelated modules.)

**Draft PR feedback received from:** Posted in the cohort Slack channel asking for review; no response yet as of submission. PR was moved from draft to ready-for-review regardless, per this week's guidance that peer review is encouraged but "none" is an acceptable answer here.
