"""Throwaway git repositories for the version stamp tests."""
import os
import subprocess
from pathlib import Path

GIT_TIMEOUT_S = 30


def git(root: Path, *args: str, env: dict | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=GIT_TIMEOUT_S,
        check=True,
        env=env,
    )
    return result.stdout


def make_repo(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "--quiet")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.invalid")
    git(root, "config", "core.autocrlf", "false")
    git(root, "config", "commit.gpgsign", "false")
    return root


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def commit_all(root: Path, message: str, when: str) -> None:
    env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    git(root, "add", "-A")
    git(root, "commit", "--quiet", "-m", message, env=env)
