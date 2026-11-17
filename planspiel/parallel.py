from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Callable, Dict, Sequence


def map_tiers(worker: Callable, config_path, tiers: Sequence[str], jobs: int = 1) -> Dict[str, object]:
    """Ruft worker(config_path, tier) je Tier auf, bei jobs > 1 in getrennten Prozessen (höchstens ein Prozess je Tier).
    Der Worker muss eine Funktion auf Modulebene (Windows: spawn) sein und lädt die Konfiguration selbst aus dem Pfad."""
    names = list(tiers)
    path = str(Path(config_path))
    if jobs <= 1 or len(names) <= 1:
        return {name: worker(path, name) for name in names}
    with ProcessPoolExecutor(max_workers=min(jobs, len(names))) as pool:
        futures = {name: pool.submit(worker, path, name) for name in names}
        return {name: futures[name].result() for name in names}
