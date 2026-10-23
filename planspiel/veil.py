"""Veil scan of the print set (VEIL-02, ROADMAP SC5, Phase 3 D-13/D-13b/D-20, Phase 5 D-12/D-14/D-24).

What each audience (see `planspiel.audience`) may and may not contain:

- pre-wave (`spieler-`): no attack name (story profile: the D-13b list minus the D-20 exceptions OT and
  Erpress*, plus the full revealed names), no attack-specific revealed string (revealed name, narrative,
  CIA rationale, bonus reason), no weight triple of a real wave and no weight symbol followed by a value
  (`wC = 0,4`). The bare symbols `wC wI wA` stay legal (legend, wave explainer). The measure deck uses the
  names-only profile, so the defence term "Phishing" on the M6 card passes (D-24).
- practice (`uebung-`): the same checks except the weight-symbol rule. Practice is shown before wave 1 on
  purpose (D-12, D-14): ROADMAP SC5 and VEIL-04 mean the weights and bonus links of the real waves 1-3, so a
  practice sheet may print its own practice weights and bonus measures, never a real wave's.
- revealed (`angriff-N_*`): checked against the other attacks only (F11): no other attack's full revealed
  name, attack-specific string or weight triple. Its own name and weights are allowed, and giveaway stems
  such as "exfil" are not used (worksheet 1 says "ggf. exfiltriert").
- facilitator (`spielleitung-`): not scanned for names.

Layer 1 (`layer="tex"`) runs on the de-TeXed source in the default suite and as the `print.veil` build gate.
Layer 2 (`layer="pdf"`) runs on pypdf text, which loses most word spaces and may hyphenate at line ends (F10):
only multi-character substring terms are matched there, on text squashed of whitespace and hyphens; token
terms (`sps`, `apt`) belong to layer 1. Layer 1 also runs the squashed pass, so a name split by TeX macros
(`Ran\\textbf{som}ware`) is still found.
"""
import dataclasses
import re
from typing import NamedTuple, Optional

from planspiel import audience, fmt, printmodel, rules
from planspiel.config import Config
from planspiel.texts import GiveawayTerms, Texts, giveaway_hits, normalize_for_matching
from planspiel.validate import Issue

LAYERS = ("tex", "pdf")
_WORD = r"[^\W\d_]"
_NUMBER = re.compile(r"\d+(?:,\d+)?")
_WEIGHT_SYMBOL = re.compile(r"(?<![A-Za-z])w[CIA]\s*[=:]?\s*\d")
_SHARED_WORDING = "case_"  # case texts are shared between attacks ("Ihr mindert die Auswirkungen teilweise.")

# Inverse of `render.tex_escape`, then control words and symbols, unescaped comments and grouping braces.
_UNESCAPE = {
    r"\textbackslash{}": "\\",
    r"\textquotedbl{}": '"',
    r"\textasciitilde{}": "~",
    r"\textasciicircum{}": "^",
    r"\&": "&",
    r"\%": "%",
    r"\$": "$",
    r"\#": "#",
    r"\_": "_",
    r"\{": "{",
    r"\}": "}",
}
_TEX_TOKEN = re.compile(
    r"\\(?:textbackslash|textquotedbl|textasciitilde|textasciicircum)\{\}"
    r"|\\[&%$#_{}]"
    r"|\\[A-Za-z]+\*?"
    r"|\\."
    r"|%[^\n]*"
    r"|[{}]",
    re.DOTALL,
)


def detex(source: str) -> str:
    """Printed-looking text of a .tex source: escapes undone, comments dropped, macros and braces as spaces."""

    def replace(match: re.Match) -> str:
        token = match.group(0)
        if token in _UNESCAPE:
            return _UNESCAPE[token]
        if token.startswith("%"):
            return ""
        return " "

    return _TEX_TOKEN.sub(replace, source)


class VeilContext(NamedTuple):
    cfg: Config
    texts: Texts
    terms: GiveawayTerms
    signatures: dict
    names: dict
    revealed: dict


def weight_signatures(cfg: Config) -> dict[tuple[str, str, str], int]:
    """Formatted (wC, wI, wA) of every real wave -> wave id; only through `rules.worksheet_constants` (F1)."""
    found: dict[tuple[str, str, str], int] = {}
    for wave in cfg.waves:
        constants = rules.worksheet_constants(cfg, wave)
        triple = tuple(fmt.format_number(value) for value in (constants.w_c, constants.w_i, constants.w_a))
        found[triple] = wave.wave_id
    return found


def context(cfg: Config, texts: Texts, terms: GiveawayTerms) -> VeilContext:
    names: dict[str, str] = {}
    revealed: dict[str, tuple[tuple[str, str], ...]] = {}
    for attack_id in cfg.attacks:
        base = f"attacks.{attack_id}.revealed"
        if texts.has(f"{base}.name"):
            names[attack_id] = str(texts.get(f"{base}.name"))
        revealed[attack_id] = tuple(
            (key[len(base) + 1:], text)
            for key, text in texts.strings(base)
            if not key[len(base) + 1:].startswith(_SHARED_WORDING)
        )
    return VeilContext(cfg, texts, terms, weight_signatures(cfg), names, revealed)


def weight_hits(text: str, signatures: dict) -> list[int]:
    """Wave ids whose weight triple is in the text: three consecutive number tokens, or the joined form."""
    numbers = _NUMBER.findall(text)
    squashed = re.sub(r"\s+", "", text)
    hits = {
        signatures[window]
        for window in (tuple(numbers[i:i + 3]) for i in range(len(numbers) - 2))
        if window in signatures
    }
    hits |= {wave for triple, wave in signatures.items() if "".join(triple) in squashed}
    return sorted(hits)


def weight_symbol_hits(text: str) -> list[str]:
    return [match.group(0) for match in _WEIGHT_SYMBOL.finditer(text)]


def _squash(normalised: str) -> str:
    return re.sub(r"[\s-]+", "", normalised)


def _name_regex(name: str, squashed: bool) -> re.Pattern:
    parts = [re.escape(part) for part in re.split(r"[\s-]+", normalize_for_matching(name)) if part]
    if squashed:
        return re.compile("".join(parts))
    pattern = r"[\s-]*".join(parts)
    if len(parts) > 1:
        pattern = rf"(?<!{_WORD}){pattern}"
    return re.compile(pattern)


def name_hits(
    text: str, ctx: VeilContext, profile: str, *, exclude_attack: Optional[str] = None, squashed: bool = False
) -> list[str]:
    """Attack names in the text. `names`: full names, long ids, compounds; `story`: plus the giveaway list;
    `other_attacks`: only the full names of the attacks other than `exclude_attack`."""
    if profile not in (audience.PROFILE_NAMES, audience.PROFILE_STORY, audience.PROFILE_OTHER_ATTACKS):
        raise ValueError(f"Unbekanntes Veil-Profil '{profile}'")
    normalised = normalize_for_matching(text)
    haystack = _squash(normalised) if squashed else normalised
    hits = {
        normalize_for_matching(name)
        for attack_id, name in ctx.names.items()
        if attack_id != exclude_attack and _name_regex(name, squashed).search(haystack)
    }
    if profile == audience.PROFILE_OTHER_ATTACKS:
        return sorted(hits)
    ids = [attack_id.lower() for attack_id in ctx.cfg.attacks if attack_id != exclude_attack]
    long_ids = [attack_id for attack_id in ids if len(attack_id) >= 5]
    if squashed:
        hits |= {attack_id for attack_id in long_ids if attack_id in haystack}
        for first, second in ctx.terms.compounds:
            if f"{first.lower()}{second.lower()}" in haystack:
                hits.add(f"{first.lower()}-{second.lower()}")
        if profile == audience.PROFILE_STORY:
            stems_only = dataclasses.replace(ctx.terms, tokens=(), compounds=())
            hits |= set(giveaway_hits(haystack, stems_only, long_ids, profile="story"))
        return sorted(hits)
    if profile == audience.PROFILE_STORY:
        hits |= set(giveaway_hits(text, ctx.terms, ids, profile="story"))
        return sorted(hits)
    hits |= {attack_id for attack_id in long_ids if attack_id in normalised}
    for first, second in ctx.terms.compounds:
        pattern = rf"(?<!{_WORD}){re.escape(first.lower())}[\s-]*{re.escape(second.lower())}"
        if re.search(pattern, normalised):
            hits.add(f"{first.lower()}-{second.lower()}")
    return sorted(hits)


def revealed_hits(
    text: str, ctx: VeilContext, *, exclude_attack: Optional[str] = None, squashed: bool = False
) -> list[str]:
    """`<attack>.<key>` of every attack-specific revealed string that appears in the text."""
    normalised = normalize_for_matching(text)
    haystack = _squash(normalised) if squashed else normalised
    hits = []
    for attack_id, strings in ctx.revealed.items():
        if attack_id == exclude_attack:
            continue
        for key, string in strings:
            needle = normalize_for_matching(string)
            needle = _squash(needle) if squashed else needle
            if needle and needle in haystack:
                hits.append(f"{attack_id}.{key}")
    return hits


def _quoted(hits) -> str:
    return ", ".join(f"'{hit}'" for hit in hits)


def scan_text(text: str, job: str, ctx: VeilContext, *, layer: str) -> list[Issue]:
    if layer not in LAYERS:
        raise ValueError(f"Unbekannte Ebene '{layer}', erlaubt sind {LAYERS}")
    try:
        group = audience.audience_of(job)
        profile = audience.scan_profile(job)
    except ValueError as error:
        return [Issue("error", "veil.audience", job, str(error))]
    if profile is None:
        return []
    exclude: Optional[str] = None
    own_wave: Optional[int] = None
    if group == audience.REVEALED:
        wave = next((wave for wave in ctx.cfg.waves if printmodel.worksheet_job(wave) == job), None)
        if wave is None:
            return [Issue("error", "veil.audience", job, f"Angriffsblatt '{job}' gehört zu keiner Welle der Config")]
        exclude, own_wave = wave.attack_id, wave.wave_id
    passes = (False, True) if layer == "tex" else (True,)
    subject = "Anderer Angriff im Angriffsblatt" if group == audience.REVEALED else "Vor der Welle verboten"
    issues: list[Issue] = []
    names = sorted({hit for squashed in passes for hit in name_hits(text, ctx, profile, exclude_attack=exclude, squashed=squashed)})
    if names:
        issues.append(Issue("error", "veil.name", job, f"{subject}: Angriffsname {_quoted(names)}"))
    # The revealed name is reported once, as veil.name; the other strings are attack-specific prose.
    strings = sorted(
        {
            hit
            for squashed in passes
            for hit in revealed_hits(text, ctx, exclude_attack=exclude, squashed=squashed)
            if not hit.endswith(".name")
        }
    )
    if strings:
        issues.append(Issue("error", "veil.revealed_text", job, f"{subject}: angriffsspezifischer Text {_quoted(strings)}"))
    waves = [wave for wave in weight_hits(text, ctx.signatures) if wave != own_wave]
    if waves:
        listed = ", ".join(str(wave) for wave in waves)
        issues.append(Issue("error", "veil.weights", job, f"{subject}: CIA-Gewichte von Welle {listed}"))
    if group == audience.PREWAVE:
        symbols = weight_symbol_hits(text)
        if symbols:
            issues.append(Issue("error", "veil.weight_symbol", job, f"{subject}: Gewichtssymbol mit Wert {_quoted(symbols)}"))
    return issues


def scan_documents(cfg: Config, texts: Texts, terms: GiveawayTerms, documents: dict[str, str]) -> list[Issue]:
    """Layer 1 over `{job: tex}`, including the job names of every non-revealed document (file names)."""
    ctx = context(cfg, texts, terms)
    issues: list[Issue] = []
    for job, source in documents.items():
        issues.extend(scan_text(detex(source), job, ctx, layer="tex"))
        try:
            revealed = audience.audience_of(job) == audience.REVEALED
        except ValueError:
            revealed = False
        if not revealed:
            hits = name_hits(job, ctx, audience.PROFILE_NAMES)
            if hits:
                issues.append(Issue("error", "veil.file_name", job, f"Dateiname nennt einen Angriff: {_quoted(hits)}"))
    return issues
