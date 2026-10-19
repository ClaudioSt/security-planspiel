# Phase 4: Print Pipeline & Attack Worksheets - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-19
**Phase:** 04-print-pipeline-attack-worksheets
**Areas discussed:** Worksheet content, Case-3 formula form, Equivalence scope, Build/output/stamp

---

## Worksheet content

| Option | Description | Selected |
|--------|-------------|----------|
| MHP order + numbered steps | MHP flow, numbered steps with fill-in boxes | ✓ |
| 1:1 MHP layout | Same paragraphs/tables, only add missing mechanics | |
| Redesign as calculation form | Mostly boxes/arrows, narrative cut | |

| Option | Description | Selected |
|--------|-------------|----------|
| Formula with fill-in boxes | "E-Wert = C ___ × 0,4 + …", weights from config | ✓ |
| Small weight table + formula | Separate weight table | |

| Option | Description | Selected |
|--------|-------------|----------|
| Extra recovery step on the sheet | Only when allow_recovery; M4 level → r table | ✓ |
| Separate Backup & Recovery sheet | Pointer to a recovery card | |

| Option | Description | Selected |
|--------|-------------|----------|
| Each team, own copy | 9 sheets, teams calculate | ✓ |
| Facilitator only | Facilitator fills in | |

| Option | Description | Selected |
|--------|-------------|----------|
| One A4, rows = max measures | Fixed one page, rows from config | |
| One page, keep 6 rows | MHP row count | |
| Two pages allowed | Split across two pages | |

**User's choice (page budget):** free text: "no max measures - one a4 is ideal - two pages if neccessary".

---

## Case-3 formula form

| Option | Description | Selected |
|--------|-------------|----------|
| Rearranged form + hard guard | "(31 − GR) × 20.000 €", build fails if invariant breaks | ✓ |
| General form always | "(8 − (GR − 23)) × 20.000 €" | |
| Auto-switch | Rearranged while invariant holds, general otherwise | |

| Option | Description | Selected |
|--------|-------------|----------|
| One KZ shape for all waves | "KZ = −6 + (GR − 23) × 2" | ✓ |
| Keep MHP shapes | Per-sheet forms from the docx | |

| Option | Description | Selected |
|--------|-------------|----------|
| Exact "× 17 ÷ 7" | Exact fraction, warning stays until Phase 6 | ✓ |
| Fail the build on non-decimal slopes | Pull BAL-02 forward | |
| Rounded decimal "× 2,43" | Friendlier, needs a tolerance | |

| Option | Description | Selected |
|--------|-------------|----------|
| Exact, with printed hint | "2 Nachkommastellen reichen", research proves it | ✓ |
| Round KZ on the sheet | Can differ from sim | |

---

## Equivalence scope

| Option | Description | Selected |
|--------|-------------|----------|
| Rounding as last step on the worksheet | Attack KZ + event KZ, rounded; test covers rounding | ✓ |
| Rounding on the tracking sheet (Phase 5) | Worksheet ends with exact attack KZ | |

| Option | Description | Selected |
|--------|-------------|----------|
| Synthetic grid + full replay | Fast exhaustive grid + slow replay of all plans | ✓ |
| Synthetic grid only | No slow replay | |
| Full plan replay only | Real plans only | |

| Option | Description | Selected |
|--------|-------------|----------|
| Replay on print model + PDF number check | Replay from render model; pypdf asserts numbers on the page | ✓ |
| Replay on print model only | No PDF text extraction | |

---

## Build, output & stamp

| Option | Description | Selected |
|--------|-------------|----------|
| uv run planspiel print | New CLI subcommand | ✓ |
| Separate build.py script | Root script | |

| Option | Description | Selected |
|--------|-------------|----------|
| Committed in final_documents/generated/ | Build dir gitignored, PDFs committed | ✓ |
| Build dir only (gitignored) | PDFs never committed | |

| Option | Description | Selected |
|--------|-------------|----------|
| Input hash + commit date | Hash over all inputs, commit date, "+lokal" if dirty | ✓ |
| Config hash + commit date | Only config hashed | |
| Config hash + build date | Wall clock breaks byte identity | |

| Option | Description | Selected |
|--------|-------------|----------|
| Arimo, committed | Arial-metric font, reproducible across machines | |
| System Arial | MHP font, byte identity only on same machine | ✓ |
| Segoe UI | MHP card brand font | |

| Option | Description | Selected |
|--------|-------------|----------|
| Update + pinned package list + preflight | One-time MiKTeX update, preflight, --disable-installer | ✓ |
| Only packages already installed | Plainer layout, no update | |

| Option | Description | Selected |
|--------|-------------|----------|
| Black/white-safe, sparse accent | Grayscale-safe, one accent colour | |
| Colour like the MHP decks | Full MHP theme colours | ✓ |
| Plain like the Word docx | No colour | |

---

## Claude's Discretion

- CIA table row count, step labels, module layout, hash details, number formatting, test markers, output file names (see CONTEXT.md).

## Deferred Ideas

- KZ clamp on the running total → Phase 5 tracking sheet.
- Hand-friendly wave-3 slope → Phase 6 (BAL-02).
- Archive old Angriff-*.docx → Phase 7 (LEG-01).
