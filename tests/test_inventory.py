"""Inventar der handgepflegten Dokumente und Assets-Ordner (SC5, D-19, D-22, D-30)."""
import hashlib
import re
import unicodedata

from planspiel.texts import load_texts
from tests.support import CONTENT_DIR, REPO_ROOT

FINAL_DOCUMENTS = REPO_ROOT / "final_documents"
INVENTORY = CONTENT_DIR / "INVENTORY.md"
ASSETS = CONTENT_DIR / "assets"
MHP_ARCHIVE = REPO_ROOT / "archive" / "mhp_print_material_2026-07"

DISPOSITIONS = ("carried→TOML", "carried→assets", "generated", "kept manual", "dropped")
REASON_REQUIRED = ("generated", "kept manual", "dropped")

KEPT_FILES = (
    "13052026_VWI meets MHP_Offenes Treffen.pptx",
    "DanielGhebreselassie 1.jpg",
    "MHP Company Profile DE - Jubilee Logo.pptx",
    "Planspiel_Einführung + Grundlagen.pptx",
    "Stanullo Claudio_2022_04.jpg",
)

ARCHIVED_FILES = (
    "Anfrage-Mail.docx",
    "Anfrage-Mail.pdf",
    "Angriff-1_Ransomware.docx",
    "Angriff-2_OT-Störung.docx",
    "Angriff-3_Datenexfiltration.docx",
    "Audit-Mail.pdf",
    "Budget.docx",
    "Events_Security-Game.pptx",
    "Massnahmenkarten_Security-Game.pptx",
    "Return on Security und Final Wert.docx",
    "Unternehmenssteckbrief MechTech.docx",
    "Zeitungsartikel.docx",
    "Zeitungsartikel.pdf",
    "Zeitungsartikel_bild_audit.png",
    "Zeitungsartikel_bild_fabrik.png",
)


def _nfc(text):
    return unicodedata.normalize("NFC", text)


def _rows():
    rows = []
    in_table = False
    for line in INVENTORY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            in_table = False
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] == "File":
            in_table = True
            continue
        if not in_table or set(cells[0]) <= {"-", ":", " "}:
            continue
        assert len(cells) == 4, line
        rows.append({"files": [_nfc(name) for name in re.findall(r"`([^`]+)`", cells[0])],
                     "item": cells[1], "disposition": cells[2], "target": cells[3]})
    return rows


def _final_document_names():
    return sorted(_nfc(path.name) for path in FINAL_DOCUMENTS.iterdir() if path.is_file())


def _archived_names():
    if not MHP_ARCHIVE.is_dir():
        return []
    return sorted(_nfc(path.name) for path in MHP_ARCHIVE.iterdir()
                  if path.is_file() and path.name != "README.md")


def _all_names():
    return sorted(set(_final_document_names()) | set(_archived_names()))


def test_kept_files_equal_the_final_documents_listing():
    assert _final_document_names() == sorted(_nfc(name) for name in KEPT_FILES)


def test_archived_files_equal_the_archive_listing():
    assert _archived_names() == sorted(_nfc(name) for name in ARCHIVED_FILES)


def test_archived_files_are_gone_from_final_documents():
    present = set(_final_document_names())
    assert [name for name in ARCHIVED_FILES if _nfc(name) in present] == []


def test_every_final_document_has_a_row_of_its_own():
    sole_entries = {row["files"][0] for row in _rows() if len(row["files"]) == 1}
    missing = [name for name in _all_names() if name not in sole_entries]
    assert missing == []


def test_every_row_uses_a_known_disposition_and_names_only_real_files():
    names = set(_all_names())
    for row in _rows():
        assert row["disposition"] in DISPOSITIONS, row
        assert row["files"], row
        assert set(row["files"]) <= names, row


def test_measure_cards_are_carried_to_measures_and_the_deck_errors_are_dropped():
    rows = [row for row in _rows() if row["files"] == ["Massnahmenkarten_Security-Game.pptx"]]
    assert any(
        row["disposition"] == "carried→TOML" and row["target"].startswith("`measures.") for row in rows
    )
    dropped = " ".join(row["item"] + row["target"] for row in rows if row["disposition"] == "dropped")
    assert "M6 L3" in dropped
    assert "M10 L1" in dropped


def test_carried_toml_targets_point_at_existing_keys():
    keys = [key for key, _ in load_texts(CONTENT_DIR / "texte.toml").leaves()]
    for row in _rows():
        if row["disposition"] != "carried→TOML":
            continue
        match = re.match(r"`([^`]+)`", row["target"])
        assert match, row
        assert any(key.startswith(match.group(1)) for key in keys), row


def test_carried_assets_targets_point_at_existing_paths():
    for row in _rows():
        if row["disposition"] != "carried→assets":
            continue
        match = re.match(r"`([^`]+)`", row["target"])
        assert match, row
        assert (REPO_ROOT / match.group(1)).exists(), row


def test_rows_without_a_target_carry_a_reason():
    for row in _rows():
        if row["disposition"] in REASON_REQUIRED:
            assert row["target"], row


def test_newspaper_images_match_the_recorded_md5():
    readme = (ASSETS / "README.md").read_text(encoding="utf-8")
    for name in ("audit", "fabrik"):
        row = next(line for line in readme.splitlines()
                   if line.startswith(f"| `images/zeitungsartikel_bild_{name}.png`"))
        recorded = re.search(r"md5 `([0-9a-f]{32})`", row).group(1)
        copy = (ASSETS / "images" / f"zeitungsartikel_bild_{name}.png").read_bytes()
        assert hashlib.md5(copy).hexdigest() == recorded, name


def test_guidelines_carry_the_branding_facts():
    guidelines = (ASSETS / "GUIDELINES.md").read_text(encoding="utf-8")
    for fact in ("000099", "00CC67", "DDEF03", "Segoe UI", "3.0", "1.5", "2.0"):
        assert fact in guidelines, fact
    assert (ASSETS / "README.md").is_file()
