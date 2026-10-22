---
status: complete
phase: 04-print-pipeline-attack-worksheets
source: [04-VERIFICATION.md]
started: 2026-10-22T16:32:26Z
updated: 2026-10-22T21:22:32Z
---

## Current Test

number: 1
name: Colour/duplex A4 test print of angriff-1_ransomware.pdf with a sample wave filled in by hand
expected: |
  Both pages print on one A4 sheet (duplex) in colour. Handwriting boxes are big enough, the punch margin is clear,
  colours are legible, front/back align, and a sample wave can be calculated by hand from the printed steps alone
  (check also that "GR" is understandable, see IN-02).
awaiting: none

## Tests

### 1. Colour/duplex A4 test print of angriff-1_ransomware.pdf with a sample wave filled in by hand
expected: Handwriting space, punch margin, colour legibility and duplex alignment are fine; a sample wave can be completed by hand from the sheet alone.
result: pass — user: "pdf looks good"

### 2. Confirm WR-07 semantics: non-default --config/--content-dir/--print-dir builds are stamped "+lokal" with a Hinweis line instead of being rejected
expected: User accepts "+lokal" marking (or asks for rejection instead).
result: pass — user chose option A ("yes confirm A"): non-default inputs are stamped +lokal, not rejected

## Summary

total: 2
passed: 2
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
