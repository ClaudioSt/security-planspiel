# Obsolete — legacy print generators and their output

This folder holds the three old generator scripts (`generate_pptx_cards.py`,
`generate_from_template.py`, `generate_attack_calculator.py`), their output folder `pptx_output/` and
the Excel attack calculator `angriff_berechnung.xlsx`.

They were replaced by the `planspiel print` pipeline (Phases 4 and 5), which renders all print material
from `simulation_config.json` and `content/texte.toml`. The calculator has raised a KeyError since
plan 02-01.

The scripts resolve paths relative to their own folder and the working directory and are not meant to
run from here. Kept for history only.
