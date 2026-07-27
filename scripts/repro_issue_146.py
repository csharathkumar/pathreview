"""Reproduction script for issue #146.

PII scrubber fails to redact parenthesized US phone numbers.
https://github.com/ascherj/pathreview/issues/146

Run with the project venv active:

    source .venv/bin/activate
    python scripts/repro_issue_146.py

Observed output (2026-07-23, on this branch, before the fix):

    scrub(): Call me at (555) 123-4567 or [REDACTED]
    detect() on parens-only text: []
    detect() on dashed-only text: [{'type': 'phone_us', 'value': '555-123-4567', ...}]

The dashed number is redacted/detected correctly. The parenthesized number is
left completely untouched by scrub() and produces zero detections in
detect() when it is the only phone number present in the text.

Root cause: the `phone_us` pattern in safety/pii_scrubber.py already has
optional `\\(?` / `\\)?` groups around the area code, but the separator
allowed immediately after the closing `)` is restricted to `[-.]?` -- a
literal space is not in that character class. Since the conventional
parenthesized format is written as "(555) 123-4567" (space after the
paren), the match fails right after the closing paren and the whole
number is skipped.
"""

from safety.pii_scrubber import PIIScrubber

if __name__ == "__main__":
    scrubber = PIIScrubber()

    mixed_text = "Call me at (555) 123-4567 or 555-123-4567"
    parens_only = "Call me at (555) 123-4567"
    dashed_only = "Call me at 555-123-4567"

    print("scrub():", scrubber.scrub(mixed_text))
    print("detect() on parens-only text:", scrubber.detect(parens_only))
    print("detect() on dashed-only text:", scrubber.detect(dashed_only))
