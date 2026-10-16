import re
import subprocess
from pathlib import Path


def git_link(repo: Path) -> str | None:
    if not (repo / ".git").exists():
        return None
    url = subprocess.run(["git", "-C", repo, "remote", "get-url", "origin"], capture_output=True, text=True).stdout.strip()
    # git@github.com:user/repo.git -> https://github.com/user/repo
    return re.sub(r"^git@([^:]+):", r"https://\1/", url).removesuffix(".git") or None


def applications(paths: list[str]) -> dict[str, tuple[str | None, float]]:
    """name -> (git link, mtime) of every folder inside the given paths. Earlier paths win on name clashes."""
    apps = {}
    for folder in (Path(p).expanduser() for p in paths):
        if not folder.is_dir():
            continue
        for entry in folder.iterdir():
            if entry.is_dir() and entry.name not in apps:
                apps[entry.name] = (git_link(entry), entry.stat().st_mtime)
    return apps
