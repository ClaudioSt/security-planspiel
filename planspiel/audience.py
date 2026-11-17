"""Audience of every printed document, classified by the job-name prefix (VEIL-02).

The prefix is the single classification of a document: `spieler-` is read by the players before a wave,
`uebung-` is the practice material (Welle 0), `angriff-` is revealed when the wave hits and `spielleitung-`
is for the facilitators only. A job without one of these prefixes is a build error, so a new document cannot
be registered without deciding who may read it and which veil profile scans it.
"""

PREWAVE = "prewave"
PRACTICE = "practice"
REVEALED = "revealed"
FACILITATOR = "facilitator"

PREFIXES: tuple[tuple[str, str], ...] = (
    ("spieler-", PREWAVE),
    ("uebung-", PRACTICE),
    ("angriff-", REVEALED),
    ("spielleitung-", FACILITATOR),
)

# The measure deck legitimately carries defence terms such as "Phishing" (D-24): names-only profile.
MEASURE_DECK_JOB = "spieler-massnahmenkarten"

PROFILE_NAMES = "names"
PROFILE_STORY = "story"
PROFILE_OTHER_ATTACKS = "other_attacks"


def audience_of(job: str) -> str:
    for prefix, audience in PREFIXES:
        if job.startswith(prefix):
            return audience
    allowed = ", ".join(prefix for prefix, _ in PREFIXES)
    raise ValueError(f"Dokument {job!r} hat kein Zielgruppen-Präfix (erlaubt: {allowed})")


def scan_profile(job: str) -> str | None:
    """Veil scan profile of a job; None for facilitator documents, which are not scanned for names."""
    audience = audience_of(job)
    if audience == FACILITATOR:
        return None
    if audience == REVEALED:
        return PROFILE_OTHER_ATTACKS
    if job == MEASURE_DECK_JOB:
        return PROFILE_NAMES
    return PROFILE_STORY
