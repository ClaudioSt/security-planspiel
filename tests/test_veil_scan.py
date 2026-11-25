"""Layer-1 veil scan on the rendered .tex (VEIL-02, ROADMAP SC5, Phase 3 D-13/D-20, Phase 5 D-12/D-14/D-24)."""
import pytest

from planspiel import audience, render, rules, veil
from planspiel.config import load_config
from planspiel.fmt import format_number
from planspiel.texts import load_content
from tests.support import CONFIG_PATH, CONTENT_DIR, REPO_ROOT

TEMPLATES = REPO_ROOT / "print" / "templates"
PREWAVE = "spieler-test"
DECK = "spieler-massnahmenkarten"
PRACTICE = "uebung-test"


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def content():
    return load_content(CONTENT_DIR)


@pytest.fixture(scope="module")
def ctx(cfg, content):
    return veil.context(cfg, content.texts, content.terms)


def _codes(text, job, ctx, layer="tex"):
    if layer == "tex":
        text = veil.detex(text)  # scan_text takes printed-looking text, scan_documents de-TeXes first
    return sorted({issue.code for issue in veil.scan_text(text, job, ctx, layer=layer)})


def _triple(cfg, wave_id):
    wave = next(wave for wave in cfg.waves if wave.wave_id == wave_id)
    constants = rules.worksheet_constants(cfg, wave)
    return [format_number(value) for value in (constants.w_c, constants.w_i, constants.w_a)]


def _reason(content, attack_id, measure):
    return content.texts.get(f"attacks.{attack_id}.revealed.bonus_reasons.{measure}")


def _name(content, attack_id):
    return content.texts.get(f"attacks.{attack_id}.revealed.name")


# --- detex -----------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (r"A \& B", "A & B"),
        (r"\textquotedbl{}aktiv\textquotedbl{}", '"aktiv"'),
        (r"100 \% \# \_ \{x\} \$", "100 % # _ {x} $"),
        (r"a\textbackslash{}b \textasciitilde{} \textasciicircum{}", "a\\b ~ ^"),
    ],
)
def test_detex_inverts_the_tex_escapes(source, expected):
    assert expected in veil.detex(source)


def test_detex_inverts_every_special_of_tex_escape():
    specials = '\\&%$#_{}~^"'
    assert specials in veil.detex(render.tex_escape(specials))


def test_detex_drops_unescaped_comments_to_the_end_of_the_line():
    text = veil.detex("sichtbar % Ransomware im Kommentar\nzweite Zeile \\% bleibt")
    assert "Ransomware" not in text
    assert "zweite Zeile % bleibt" in text


def test_detex_replaces_control_words_by_spaces_and_keeps_words_apart():
    assert "Ransomware" not in veil.detex(r"\textbf{Ransom}ware")
    assert "Datenexfiltration" in veil.detex(r"x\step{Datenexfiltration}y").split()
    assert "Ransom" in veil.detex(r"\textbf{Ransom}ware").split()


# --- weights ---------------------------------------------------------------------------------------------


def test_weight_signatures_follow_the_config(cfg):
    signatures = veil.weight_signatures(cfg)
    expected = {tuple(_triple(cfg, wave.wave_id)): wave.wave_id for wave in cfg.waves}
    assert signatures == expected
    assert len(signatures) == len(cfg.waves)


def test_weight_hits_find_a_triple_with_text_in_between(cfg):
    signatures = veil.weight_signatures(cfg)
    first = _triple(cfg, 1)
    text = f"C × {first[0]} + I × {first[1]} + A × {first[2]}"
    assert veil.weight_hits(text, signatures) == [1]


def test_weight_hits_find_the_joined_form_in_squashed_text(cfg):
    signatures = veil.weight_signatures(cfg)
    assert veil.weight_hits("".join(_triple(cfg, 1)), signatures) == [1]


def test_weight_hits_ignore_a_single_value_and_a_partial_window(cfg):
    signatures = veil.weight_signatures(cfg)
    first = _triple(cfg, 1)
    assert veil.weight_hits(f"r = {first[2]}", signatures) == []
    assert veil.weight_hits(f"{first[0]} {first[1]} 0,3", signatures) == []


def test_weight_hits_report_every_wave_found(cfg):
    signatures = veil.weight_signatures(cfg)
    text = " ".join(" ".join(_triple(cfg, wave.wave_id)) for wave in cfg.waves)
    assert veil.weight_hits(text, signatures) == sorted(wave.wave_id for wave in cfg.waves)


@pytest.mark.parametrize("text", ["wC = 0,4", "wA:0,2", "wI 0,6", "Gewicht wC=1"])
def test_weight_symbol_with_a_value_is_found(text):
    assert veil.weight_symbol_hits(text)


@pytest.mark.parametrize("text", ["E-Wert = C · wC + I · wI + A · wA", "die Gewichte wC wI wA", "nichts"])
def test_weight_symbols_without_values_stay_legal(text):
    assert veil.weight_symbol_hits(text) == []


# --- pre-wave documents ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "Ransomware",
        "Datenexfiltration",
        "OT-Störung",
        "OT Störung",
        "OT-Stoerung",
        "Phishing",
        "Ihr seht Exfiltration kommen",
        r"\textbf{Ransom}ware",
        r"Datenex\textbf{filtration}",
    ],
)
def test_prewave_text_naming_an_attack_fails(text, ctx):
    assert "veil.name" in _codes(text, PREWAVE, ctx)


def test_prewave_text_with_a_real_weight_triple_fails(cfg, ctx):
    text = " ".join(_triple(cfg, 2))
    assert "veil.weights" in _codes(text, PREWAVE, ctx)


def test_prewave_text_with_a_weight_symbol_and_value_fails(ctx):
    assert "veil.weight_symbol" in _codes("wC = 0,3", PREWAVE, ctx)


def test_prewave_text_with_a_revealed_bonus_reason_fails(content, ctx):
    text = _reason(content, "ransomware", "M4")
    assert text == "Backup ermöglicht schnelle Wiederherstellung"
    assert "veil.revealed_text" in _codes(text, PREWAVE, ctx)


def test_prewave_text_with_a_revealed_narrative_fails(content, ctx):
    narrative = content.texts.get("attacks.ot.revealed.narrative")
    assert "veil.revealed_text" in _codes(narrative, PREWAVE, ctx)


def test_story_exceptions_pass(ctx):
    assert _codes("OT/IT-Segmentierung", PREWAVE, ctx) == []
    assert _codes("Erpresser", PREWAVE, ctx) == []
    assert _codes("Die OT im Werk", PREWAVE, ctx) == []


def test_legend_symbols_without_values_pass(ctx):
    assert _codes("E-Wert = C · wC + I · wI + A · wA", PREWAVE, ctx) == []


def test_a_squashed_name_across_macros_is_still_found(ctx):
    assert "veil.name" in _codes(r"Ran\textbf{som}ware", PREWAVE, ctx)


def test_shared_case_wording_is_not_attack_specific(content, ctx):
    case = content.texts.get("attacks.ransomware.revealed.case_3")
    assert case == content.texts.get("attacks.ot.revealed.case_3")
    assert _codes(case, PREWAVE, ctx) == []


# --- measure deck (names-only profile, D-24) -------------------------------------------------------------


def test_names_only_profile_lets_phishing_pass_on_the_measure_deck(ctx):
    assert _codes("Schulung gegen Phishing-Mails", DECK, ctx) == []
    assert _codes("Phishing", DECK, ctx) == []


def test_names_only_profile_still_fails_on_the_real_names(ctx):
    assert "veil.name" in _codes("Ransomware", DECK, ctx)
    assert "veil.name" in _codes("OT Störung", DECK, ctx)
    assert "veil.name" in _codes("Datenexfiltration", DECK, ctx)


def test_names_only_profile_does_not_use_token_terms(ctx):
    assert _codes("SPS APT OT", DECK, ctx) == []


# --- layers (F10) ----------------------------------------------------------------------------------------


@pytest.mark.parametrize("token", ["SPS", "APT"])
def test_token_terms_are_matched_at_layer_tex_only(token, ctx):
    assert "veil.name" in _codes(f"Die {token} im Werk", PREWAVE, ctx, layer="tex")
    assert _codes(f"Die {token} im Werk", PREWAVE, ctx, layer="pdf") == []


def test_a_token_term_is_a_whole_word_at_layer_tex(ctx):
    assert _codes("Kapital und Raps", PREWAVE, ctx, layer="tex") == []


def test_pdf_layer_matches_names_on_squashed_text(ctx):
    assert "veil.name" in _codes("Ran som ware", PREWAVE, ctx, layer="pdf")
    assert "veil.name" in _codes("Datenex-\nfiltration", PREWAVE, ctx, layer="pdf")
    assert "veil.name" in _codes("OT-\nStörung", PREWAVE, ctx, layer="pdf")


# --- revealed worksheets (F11) ---------------------------------------------------------------------------


def test_a_revealed_sheet_may_carry_its_own_name_story_and_weights(cfg, content, ctx):
    texts = content.texts
    parts = [
        _name(content, "ransomware"),
        texts.get("attacks.ransomware.revealed.narrative"),
        texts.get("attacks.ransomware.revealed.cia_rationale"),
        _reason(content, "ransomware", "M4"),
        " ".join(_triple(cfg, 1)),
    ]
    assert "MechTech" in parts[1]
    assert veil.scan_text("\n".join(parts), "angriff-1_ransomware", ctx, layer="tex") == []


@pytest.mark.parametrize(
    "text",
    ["OT-Störung", "OT Störung", "Datenexfiltration"],
)
def test_a_revealed_sheet_naming_another_attack_fails(text, ctx):
    issues = veil.scan_text(text, "angriff-1_ransomware", ctx, layer="tex")
    assert "veil.name" in {issue.code for issue in issues}


def test_the_message_names_the_other_attack(ctx):
    (issue, *_) = [i for i in veil.scan_text("OT-Störung", "angriff-1_ransomware", ctx, layer="tex") if i.code == "veil.name"]
    assert "ot" in issue.message.lower()


def test_a_revealed_sheet_with_the_weights_of_another_wave_fails(cfg, ctx):
    assert "veil.weights" in _codes(" ".join(_triple(cfg, 3)), "angriff-1_ransomware", ctx)


def test_a_revealed_sheet_with_another_attacks_bonus_reason_fails(content, ctx):
    text = _reason(content, "ot", "M5")
    assert "veil.revealed_text" in _codes(text, "angriff-1_ransomware", ctx)


def test_a_revealed_sheet_does_not_flag_giveaway_stems(ctx):
    # worksheet 1 says "ggf. exfiltriert": the id 'exfil' and the stem list belong to the other profiles
    assert _codes("ggf. exfiltriert und verschlüsselt, Phishing, Erpressung", "angriff-1_ransomware", ctx) == []


def test_an_unknown_revealed_job_is_reported(ctx):
    assert _codes("x", "angriff-9_unbekannt", ctx) == ["veil.audience"]


def test_a_job_without_prefix_is_reported(ctx):
    assert _codes("x", "smoke", ctx) == ["veil.audience"]


def test_facilitator_jobs_are_not_scanned(cfg, ctx):
    assert veil.scan_text("Ransomware " + " ".join(_triple(cfg, 1)), "spielleitung-uebersicht", ctx, layer="tex") == []


# --- practice (D-12, D-14) -------------------------------------------------------------------------------


def test_a_practice_job_with_a_real_weight_triple_fails(cfg, ctx):
    assert "veil.weights" in _codes(" ".join(_triple(cfg, 1)), PRACTICE, ctx)


def test_a_practice_job_with_its_own_weights_passes_also_with_symbols(ctx):
    assert _codes("0,3 0,3 0,4", PRACTICE, ctx) == []
    assert _codes("wC = 0,3 · wI = 0,3 · wA = 0,4", PRACTICE, ctx) == []


def test_a_practice_job_with_a_real_bonus_reason_fails(content, ctx):
    assert "veil.revealed_text" in _codes(_reason(content, "exfil", "M2"), PRACTICE, ctx)


def test_a_practice_job_naming_an_attack_fails(ctx):
    assert "veil.name" in _codes("Ransomware", PRACTICE, ctx)


# --- job names and the whole set -------------------------------------------------------------------------


def test_an_attack_in_a_non_revealed_job_name_is_a_file_name_finding(cfg, content):
    issues = veil.scan_documents(cfg, content.texts, content.terms, {"spieler-ransomware-info": "\\documentclass{article}"})
    assert "veil.file_name" in {issue.code for issue in issues}


def test_a_revealed_job_name_may_name_its_attack(cfg, content):
    documents = {
        job: source
        for job, source in render.render_all(cfg, content.texts, TEMPLATES).items()
        if job.startswith("angriff-")
    }
    assert len(documents) == len(cfg.waves)
    assert veil.scan_documents(cfg, content.texts, content.terms, documents) == []


def test_scan_documents_returns_nothing_for_todays_print_set(cfg, content):
    documents = render.render_all(cfg, content.texts, TEMPLATES)
    assert len([job for job in documents if job.startswith("angriff-")]) == len(cfg.waves)
    assert audience.MEASURE_DECK_JOB in documents
    assert veil.scan_documents(cfg, content.texts, content.terms, documents) == []


def test_scan_documents_reports_a_leak_with_job_and_code(cfg, content):
    documents = {"spieler-test": "\\begin{document}Ransomware\\end{document}"}
    (issue, *_) = veil.scan_documents(cfg, content.texts, content.terms, documents)
    assert (issue.level, issue.code, issue.path) == ("error", "veil.name", "spieler-test")
    assert "ransomware" in issue.message.lower()


def test_scan_documents_finds_an_unclassified_job(cfg, content):
    issues = veil.scan_documents(cfg, content.texts, content.terms, {"smoke": "x"})
    assert [issue.code for issue in issues] == ["veil.audience"]
