"""Shared test constants."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "simulation_config.json"
CONTENT_DIR = REPO_ROOT / "content"
MINI_CONTENT_DIR = REPO_ROOT / "tests" / "fixtures" / "mini_content"
