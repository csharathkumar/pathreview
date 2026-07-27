## Solution plan

**Issue:** [#146 — PII scrubber fails to redact parenthesized US phone numbers](https://github.com/ascherj/pathreview/issues/146)

### Understand

The `phone_us` pattern in `safety/pii_scrubber.py` is:

```python
r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b"
```

It already has optional `\(?` / `\)?` groups around the area code, so it looks like parentheses are supported. The actual bug is narrower: the separator allowed immediately after the closing `)` is `[-.]?`, which does not include a literal space. The conventional parenthesized US format is written `(555) 123-4567` — space, not dash or dot, after the `)`. Because of that, the regex engine can match up through the closing paren but then fails to bridge the space before the next 3-digit group, so the whole match attempt fails and the number is skipped entirely.

Expected behavior: `scrub()` should replace `(555) 123-4567` with `[REDACTED]`, and `detect()` should return a `phone_us` entry for it, exactly as it already does for `555-123-4567`.

Actual behavior (confirmed via `scripts/repro_issue_146.py`): `scrub()` leaves `(555) 123-4567` untouched while still correctly redacting `555-123-4567` in the same string, and `detect()` returns `[]` when a parenthesized number is the only PII present in the text.

### Map

Files expected to be touched:

- `safety/pii_scrubber.py` — update the `phone_us` regex pattern (the only line that needs to change is the pattern string in `PII_PATTERNS`).
- `tests/unit/test_pii_scrubber.py` — the existing tests `test_us_phone_number_redaction`, `test_us_phone_formats`, and any new `detect()`-focused test I add for the parenthesized case. These currently fail and should pass once the regex is fixed. I may add one new test explicitly asserting `detect()` returns a `phone_us` match for `(555) 123-4567` alone, since that's the sharpest reproduction of the bug.
- `scripts/repro_issue_146.py` — already added this week as reproduction evidence; no further changes expected, but I'll re-run it after the fix to confirm the "before" output in its docstring flips to the redacted/detected form.
- `JOURNAL.md` — Week 9 entry documenting the fix.

No other modules import or depend on `PIIScrubber` yet (confirmed via repo-wide search), so the blast radius is contained to this one file and its tests.

### Plan

1. Write/confirm a failing test that isolates the exact gap: `detect()` on text containing only `(555) 123-4567` should return one `phone_us` match (currently returns `[]`).
2. Update the `phone_us` regex in `safety/pii_scrubber.py` so the separator after the optional closing `)` also accepts whitespace — e.g. change `[-.]?` after `\)?` to something like `[-.\s]?`, or restructure the pattern so the paren-and-space combination is matched as a distinct alternative from the dash/dot form.
3. Re-run the full `phone_us`-related test list (`test_us_phone_number_redaction`, `test_us_phone_formats`, `test_detect_phone_pii`, `test_phone_at_start_of_text`) plus the rest of `test_pii_scrubber.py` to make sure the widened pattern doesn't introduce false positives elsewhere (e.g. accidentally matching unrelated digit runs separated by spaces).
4. Re-run `scripts/repro_issue_146.py` and update its docstring's "observed output" section to show the fixed behavior, so the script stays useful as a regression check rather than stale evidence.
5. Run `make check && make test-unit` per `CONTRIBUTING.md` before opening the PR, and write the commit message following the Conventional Commits format with a `safety` scope.

### Inputs & outputs

**Input:** free-form text strings passed to `PIIScrubber.scrub(text)` and `PIIScrubber.detect(text)` that may contain US phone numbers in dashed (`555-123-4567`), dotted (`555.123.4567`), plain (`+1 555 123 4567`), or parenthesized (`(555) 123-4567`) form, possibly mixed with other PII types (email, SSN, address) in the same string.

**Output:** `scrub()` returns the text with every recognized phone number (including the parenthesized form) replaced by `[REDACTED]`. `detect()` returns a list of dicts (`type`, `value`, `start`, `end`) that includes an entry for the parenthesized form with correct offsets into the original string, matching the shape it already returns for the other formats.

### Risks & unknowns

- **Over-broad matching risk:** loosening the separator to allow whitespace could cause the regex to match sequences of digits that aren't actually phone numbers (e.g. two unrelated 3-digit and 4-digit numbers separated by a space in a sentence). Need to check this against `test_text_with_no_pii` and consider adding a case with adjacent non-phone digit groups to confirm no new false positives.
- **Interaction with the `phone_intl` pattern:** `PII_PATTERNS` is a dict iterated in order, and `phone_intl` (`\+[0-9]{1,3}[-.]?[0-9]{1,14}`) runs after `phone_us` in the current dict ordering. I haven't traced whether a widened `phone_us` pattern could partially consume text in a way that changes what `phone_intl` sees on the same string (e.g. the `+1 555 123 4567` case tested in `test_us_phone_formats`). Need to verify all four formats in that test still pass together, not just the parenthesized one in isolation.
- **Regex readability/maintainability:** the current pattern is already dense; I want to avoid making it a write-only regex that's hard for the next contributor to reason about. Might be worth a short comment above the pattern explaining what each optional group is for, even though `CONTRIBUTING.md` doesn't strictly require inline regex comments.
- **Unknown:** whether the maintainer would prefer a single unified regex change vs. splitting `phone_us` into two alternatives (dashed/dotted vs. parenthesized) joined with `|` for clarity. I'll default to the smallest possible change (widen the character class) unless testing shows that approach causes the false-positive risk above.

### Edge cases

- `(555) 123-4567` — the reported bug case; must be redacted/detected.
- `(555)123-4567` — parens with no space after `)`; already passes today per the existing pattern, must not regress.
- `(555) 123.4567` — mixed space-then-dot separator; should be handled if the fix generalizes the separator class rather than special-casing exactly one space.
- Parenthesized number at the very start of a string (per `test_phone_at_start_of_text`) — confirms the `\b` boundary logic still works when there's no leading whitespace before the `(`.
- Parenthesized number immediately followed by punctuation, e.g. `Call (555) 123-4567.` — trailing period shouldn't be swallowed into or block the match.
- A string with both a parenthesized number and an unrelated space-separated pair of numbers that isn't a phone number (e.g. "room 123 4567 sq ft") — should NOT be falsely redacted; this is the main regression risk from widening the separator.
- Text with no phone number at all (`test_text_with_no_pii`) — must remain completely unchanged.
