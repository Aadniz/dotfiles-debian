import os
import shutil
import sys
from fnmatch import fnmatch
from pathlib import Path

from .config import ROOT


def mapping(config: dict) -> list[tuple[Path, Path]]:
    """(dotfiles folder, system folder) for every entry in the folder mapping."""
    return [(ROOT / repo, Path(system).expanduser()) for repo, system in config.get("folders", {}).items()]


def confirm(pairs: list[tuple[Path, Path]], ignore: list[str]) -> None:
    print("  IGNORE PATTERNS:")
    print("    " + "\n    ".join(ignore))
    print("  FOLDERS:")
    for src, dst in pairs:
        print(f"    {src} -> {dst}")
    print("\nAre you sure you want to do this? [Y/n]")
    if input("> ") not in ("Y", "y"):
        print("Canceled")
        sys.exit(130)


def copy(src: Path, dst: Path, ignore: list[str], symlinks: bool = False) -> None:
    if not src.exists():
        print(f"Warning: Source path {src} does not exist, skipping")
        return
    try:
        shutil.copytree(
            src, dst, symlinks=symlinks, dirs_exist_ok=True,
            # Patterns match against the full path, e.g. "*/target"
            ignore=lambda d, names: {n for n in names if any(fnmatch(os.path.join(d, n), p) for p in ignore)},
        )
    except shutil.Error as e:
        for _, _, msg in e.args[0]:
            print(f"WARNING: {msg}")
