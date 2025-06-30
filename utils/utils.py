import os
import re
import gzip
import fnmatch
import subprocess

from datetime import datetime
from os import PathLike
from typing import List, Dict, Set
from pathlib import Path


def should_ignore(path:  str | PathLike[str], ignore_patterns: str | list[str]) -> bool:
    if type(ignore_patterns) is str:
        return fnmatch.fnmatch(path, ignore_patterns)

    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


def get_source_applications(paths:  str | PathLike[str] | List[PathLike[str]] | List[str]) -> list:
    if type(paths) is str or type(paths) is PathLike[str]:
        paths = [paths]

    apps = {}
    for path in paths:
        expanded_dir = os.path.expanduser(path)
        if not os.path.exists(expanded_dir):
            continue

        for entry in os.listdir(expanded_dir):
            entry_path = os.path.join(expanded_dir, entry)
            if not os.path.isdir(entry_path):
                continue
            if entry in apps:
                continue

            stat = os.stat(entry_path)
            mod_time = datetime.fromtimestamp(stat.st_mtime)

            name = entry
            link = get_git_link(entry_path)

            apps[entry] = {
                "name": name,
                "link": link,
                "date": mod_time
            }

    return list(apps.values())


def extract_package_names(command_line: str):
    installs = []
    removes = []
    if "install" in command_line:
        command_line = command_line.split("install", 1)[1]
    elif "purge" in command_line:
        command_line = command_line.split("purge", 1)[1]
    elif "remove" in command_line:
        command_line = command_line.split("remove", 1)[1]

    return {
        "installs": installs,
        "removes": removes
    }


def _get_sorted_history_files(log_dir: Path) -> List[Path]:
    """Get all history log files sorted from oldest to newest."""
    files = []

    current_log = log_dir / 'history.log'

    # Collect all rotated logs
    for f in log_dir.glob('history.log.*'):
        if f.name == 'history.log':
            continue

        # Handle both .gz and uncompressed rotated logs
        if f.suffix == '.gz':
            base = f.name[:-3]
            num_part = base.split('.')[-1]
        else:
            num_part = f.name.split('.')[-1]

        # Extract number (works for both 'history.log.1' and 'history.log.10.gz')
        try:
            num = int(num_part) if num_part.isdigit() else 0
            files.append((num, f))
        except ValueError:
            continue

    # Sort by number in descending order (oldest first)
    files.sort(key=lambda x: x[0], reverse=False)

    return [current_log] + [f for (num, f) in files]


def get_apt_applications() -> List[Dict[str, str]]:
    """
    Get user-installed apt packages by processing all available history logs.
    Processes files in order from newest to oldest rotated log.
    """
    log_dir = Path('/var/log/apt')
    pkgs = {}

    # Get files in correct processing order (newest to oldest)
    log_files = _get_sorted_history_files(log_dir)

    for log_file in log_files:
        try:
            content = _read_log_file(log_file)
            _process_log_content(content, pkgs)
        except Exception as e:
            print(f"Warning: Could not process {log_file}: {e}")
            continue

    installed_pkgs = [pkg for (pkg_name, pkg) in pkgs.items() if pkg["installed"]]

    user_apps = []
    for pkg in installed_pkgs:
        desc = _get_package_description(pkg["name"])

        user_apps.append({
            'name': pkg["name"],
            'description': desc,
            'date': pkg["date"]
        })

    return sorted(user_apps, key=lambda x: x['date'])


def _read_log_file(log_file: Path) -> str:
    """Read log file, handling both plain and gzipped files."""
    if log_file.suffix == '.gz':
        with gzip.open(log_file, 'rt') as f:
            return f.read()
    else:
        with open(log_file, 'r') as f:
            return f.read()


def _process_log_content(content: str, pkgs: Dict) -> None:
    """Process log content and update package states."""
    for log_entry in content.split("\n\n"):
        if not log_entry.strip():
            continue

        entry = {}
        for line in log_entry.strip().splitlines():
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            entry[key] = value

        if "Commandline" not in entry:
            continue

        date = None
        if "Start-Date" in entry:
            date = datetime.strptime(entry["Start-Date"], "%Y-%m-%d  %H:%M:%S")

        cmd = entry["Commandline"]
        if "install" in cmd:
            for pkg in _extract_packages(cmd, install=True):
                if not pkg in pkgs:
                    pkgs[pkg] = {}
                pkgs[pkg]["installed"] = True
                pkgs[pkg]["date"] = date
                pkgs[pkg]["name"] = pkg
        elif "remove" in cmd or "purge" in cmd:
            for pkg in _extract_packages(cmd, install=False):
                if not pkg in pkgs:
                    pkgs[pkg] = {}
                pkgs[pkg]["installed"] = False
                pkgs[pkg]["date"] = date
                pkgs[pkg]["name"] = pkg


def _extract_packages(cmd: str, install: bool) -> Set[str]:
    """Extract packages from apt command line."""
    action = "install" if install else "remove|purge"
    matches = re.findall(
        fr'(?:{action})\s+([^\s\-][^\s]*)',
        cmd.split("--", 1)[0]  # Ignore everything after --
    )
    return {pkg for pkg in matches if not pkg.startswith('-')}


def _is_system_package(pkg: str) -> bool:
    """Check if package should be considered a system package."""
    system_patterns = [
        '^lib', '^python', '^perl', '^ruby', '^fonts-',
        '^linux-', '-dev$', '-dbg$', '-doc$', '-data$',
        'firmware', 'microcode', 'task-', 'language-'
    ]
    return any(re.search(pattern, pkg) for pattern in system_patterns)


def _get_package_description(pkg: str) -> str:
    """Get package description using apt-cache."""
    try:
        result = subprocess.run(
            ['apt-cache', 'show', pkg],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith('Description: '):
                return line[13:]
    except subprocess.CalledProcessError:
        pass
    return ""

def get_git_link(git_repo_path: str | PathLike[str]):
    git_remote = None
    git_config = os.path.join(git_repo_path, '.git', 'config')
    if os.path.exists(git_config):
        try:
            result = subprocess.run(
                ['git', '-C', git_repo_path, 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                check=True
            )
            git_remote = result.stdout.strip()
            # Convert SSH URL to HTTPS if needed
            if git_remote.startswith('git@'):
                git_remote = git_remote.replace(':', '/').replace('git@', 'https://')
            if git_remote.endswith('.git'):
                git_remote = git_remote.replace('.git', '')
        except subprocess.CalledProcessError:
            pass

    return git_remote