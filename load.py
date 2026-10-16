#!/usr/bin/env python
from datetime import datetime
from pathlib import Path

from utils import apt, folders
from utils.config import README_FILE, ROOT, load_config
from utils.readme import Readme


def print_apt_instructions(readme: Readme) -> None:
    installed = apt.installed()
    missing = [row[0] for row in readme.table("APT_PACKAGES") if row[0] not in installed]
    if not missing:
        print("\nAll apt packages from README.md are installed")
        return

    repo_of = {name: repo for repo, names in readme.table("APT_REPOSITORIES") for name in names.split(", ")}
    available = apt.sources(missing)
    needed_repos, not_found = {}, []
    for name in missing:
        if available.get(name):
            continue
        if name in repo_of:
            needed_repos.setdefault(repo_of[name], []).append(name)
        else:
            not_found.append(name)

    print(f"\n{len(missing)} apt packages from README.md are not installed")
    if needed_repos:
        print("\nAdd these apt repositories first:")
        for repo, names in needed_repos.items():
            print(f"  {repo}  ({', '.join(names)})")
    if not_found:
        print("\nNot found in any known repository, install these manually:")
        print("  " + " ".join(not_found))
    if installable := [name for name in missing if name not in not_found]:
        print("\nThen install the rest with:")
        print("sudo apt install " + " ".join(installable))


print(f"Loading the files from the dotfiles folder {ROOT} into the computer\n")

config = load_config()
ignore = config.get("ignore_patterns", [])
pairs = folders.mapping(config)
folders.confirm(pairs, ignore)

backup = Path("~/.cache/dotfiles-backup").expanduser() / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
for repo, system in pairs:
    if system.exists():
        folders.copy(system, backup / repo.relative_to(ROOT), ignore, symlinks=True)
if backup.exists():
    print(f"Backed up the current folders to {backup}")

for src, dst in pairs:
    folders.copy(src, dst, ignore)

print_apt_instructions(Readme(README_FILE))
