"""Facilitator-only cheat sheet (RISK-05, D-05, D-06, D-22): business consequences with management answers and the
band of each case. Bands and ids from `cfg.risk_matrix`, prose from `sheets.cheatsheet` and `sheets.register.bands`;
never an exact amount, never an attack name."""
from dataclasses import dataclass
from typing import Optional

from planspiel import risk
from planspiel.cards import printed_strings
from planspiel.config import Config
from planspiel.printmodel import PrintModelError
from planspiel.texts import RevealView, Texts

SHEET = "cheatsheet"
# Layout proof of the one-page table: more cases would no longer fit under the bands.
MAX_CHEAT_CASES = 8


@dataclass(frozen=True)
class CheatBand:
    word: str
    range: str


@dataclass(frozen=True)
class CheatCase:
    case: str
    answer: str
    band: str


@dataclass(frozen=True)
class CheatSheetPage:
    title: str
    intro: str
    bands_title: str
    bands: tuple[CheatBand, ...]
    header: tuple[str, str, str]
    cases: tuple[CheatCase, ...]

    def printed_fragments(self) -> tuple[str, ...]:
        """Every string of the page that ends up on the paper, without duplicates and without empty strings."""
        return tuple(dict.fromkeys(text for text in printed_strings(self) if text))


def build_cheat_sheet_page(cfg: Config, texts: Texts) -> Optional[CheatSheetPage]:
    """The cheat-sheet page; None when the config has no `risk_matrix` or no cases (e.g. the mini config)."""
    matrix = cfg.risk_matrix
    if matrix is None or not matrix.cases:
        return None
    if len(matrix.cases) > MAX_CHEAT_CASES:
        raise PrintModelError(
            f"Das Spielleitungs-Heft druckt höchstens {MAX_CHEAT_CASES} Geschäftsfälle (MAX_CHEAT_CASES), "
            f"die Config hat {len(matrix.cases)}"
        )
    view = RevealView(cfg, texts)
    words = view.sheet(SHEET)
    register = view.sheet("register")
    ranges = risk.band_ranges(matrix.bands, register)
    bands = {
        band.id: CheatBand(word=register["bands"][band.id], range=ranges[index])
        for index, band in enumerate(matrix.bands)
    }
    return CheatSheetPage(
        title=words["title"],
        intro=words["intro"],
        bands_title=words["bands_title"],
        bands=tuple(bands[band.id] for band in matrix.bands),
        header=(words["head_case"], words["head_answer"], words["head_band"]),
        cases=tuple(
            CheatCase(
                case=words["cases"][case.id]["case"],
                answer=words["cases"][case.id]["answer"],
                band=f"{bands[case.band].word} ({bands[case.band].range})",
            )
            for case in matrix.cases
        ),
    )
