#!/usr/bin/env python
import os
import shutil
import fnmatch
from pathlib import Path

from utils import config as config_utils
from utils import readme
from utils import utils

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = SCRIPT_DIR + "/folder-mapping.jsonc"
README_FILE = SCRIPT_DIR + "/README.md"

print(f"Saving the files from the computer into the dotfiles folder {SCRIPT_DIR}\n")

config = config_utils.read_config(CONFIG_FILE)
folders = config.get('folders', {})
ignore_patterns = config.get('ignore_patterns', [])
source_application_paths = config.get('source_application_paths', [])


print("  IGNORE PATTERNS:")
print("    " + "\n    ".join(ignore_patterns))

print("  FOLDERS:")
for (dotfile_folder, system_folder) in folders.items():
    print(f"    {os.path.expanduser(system_folder)} -> {SCRIPT_DIR}/{dotfile_folder}")


print("\nAre you sure you want to do this? [Y/n]")
ans = input("> ")

if ans != "Y" and ans != "y":
    print("Canceled")
    exit(130)

for (dotfile_folder, system_folder) in folders.items():
    from_folder = Path(os.path.expanduser(system_folder))
    to_folder = Path(SCRIPT_DIR + "/" + dotfile_folder)

    if not from_folder.exists():
        print(f"Warning: Source path {from_folder} does not exist, skipping")
        continue

    try:
        shutil.copytree(
            from_folder,
            to_folder,
            dirs_exist_ok=True,
            ignore=lambda p, f: set(
                f for f in os.listdir(p)
                if utils.should_ignore(os.path.join(p, f), ignore_patterns)
            )
        )
    except shutil.Error as e:
        for (src, dst, error_msg) in e.args[0]:
            print(f"WARNING: {error_msg}")
        continue


# Updating README.md apt application list
apt_applications = utils.get_apt_applications()
readme.update_apt_packages(apt_applications, README_FILE)

# Updating README.md source application list
source_applications = utils.get_source_applications(source_application_paths)
readme.update_source_packages(source_applications, README_FILE)