#!/usr/bin/env python
from datetime import date

from utils import apt, folders, source
from utils.config import README_FILE, ROOT, load_config
from utils.readme import Readme


def update_apt_table(readme: Readme) -> None:
    """Rows are only ever added (when installed) or removed (when uninstalled), never rewritten."""
    installed = apt.installed()
    old = readme.table("APT_PACKAGES")
    rows = [row for row in old if row[0] in installed]
    listed = {row[0] for row in rows}
    new = sorted((when, name) for name, when in apt.explicit_installs().items() if name in installed and name not in listed)
    rows += [[name, "-", when[:10]] for when, name in new]
    # Stable sort: new rows slot in by date, existing rows keep their order
    rows.sort(key=lambda row: row[2])
    readme.set_table("APT_PACKAGES", ["Package", "Description", "Installed"], rows)

    removed = [row[0] for row in old if row[0] not in installed]
    print(f"APT packages added: {', '.join(name for _, name in new) or 'none'}")
    print(f"APT packages removed: {', '.join(removed) or 'none'}")


def update_repo_table(readme: Readme) -> None:
    repos = {}
    for name, sources in apt.sources([row[0] for row in readme.table("APT_PACKAGES")]).items():
        for repo in filter(apt.is_third_party, sources):
            repos.setdefault(repo, []).append(name)
    rows = [[repo, ", ".join(sorted(names))] for repo, names in sorted(repos.items())]
    readme.set_table("APT_REPOSITORIES", ["Repository", "Packages"], rows)


def update_source_table(readme: Readme, paths: list[str]) -> None:
    """Rows keep their position, only link and date get refreshed. New folders are appended."""
    apps = source.applications(paths)
    old_links = {name: link for name, link, _ in readme.table("SOURCE_PACKAGES")}
    listed = [name for name in old_links if name in apps]
    new = sorted(apps.keys() - old_links.keys(), key=lambda name: apps[name][1])
    rows = []
    for name in listed + new:
        link, mtime = apps[name]
        # Without a git remote, keep whatever link was written by hand
        rows.append([name, f"[Source link]({link})" if link else old_links.get(name, "-"), date.fromtimestamp(mtime).isoformat()])
    readme.set_table("SOURCE_PACKAGES", ["Name", "Link", "Last Updated"], rows)

    print(f"Source packages added: {', '.join(new) or 'none'}")
    print(f"Source packages removed: {', '.join(sorted(old_links.keys() - apps.keys())) or 'none'}")


print(f"Saving the files from the computer into the dotfiles folder {ROOT}\n")

config = load_config()
ignore = config.get("ignore_patterns", [])
pairs = [(system, repo) for repo, system in folders.mapping(config)]
folders.confirm(pairs, ignore)
for src, dst in pairs:
    folders.copy(src, dst, ignore)

readme = Readme(README_FILE)
update_apt_table(readme)
update_repo_table(readme)
update_source_table(readme, config.get("source_application_paths", []))
readme.save()
