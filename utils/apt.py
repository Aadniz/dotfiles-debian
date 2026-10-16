import gzip
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

LOG_DIR = Path("/var/log/apt")


def _run(*cmd: str) -> str:
    # Untranslated output, since it gets parsed
    return subprocess.run(cmd, capture_output=True, text=True, env=os.environ | {"LC_ALL": "C"}).stdout


def installed() -> set[str]:
    out = _run("dpkg-query", "-W", "-f=${db:Status-Status} ${Package}\n")
    return {name for status, name in map(str.split, out.splitlines()) if status == "installed"}


def explicit_installs() -> dict[str, str]:
    """Earliest Start-Date (e.g. "2025-12-03  19:00:41") of every package installed on request, not as a dependency."""
    first = {}
    for log in LOG_DIR.glob("history.log*"):
        data = log.read_bytes()
        text = (gzip.decompress(data) if log.suffix == ".gz" else data).decode(errors="replace")
        for entry in text.split("\n\n"):
            fields = dict(line.split(": ", 1) for line in entry.splitlines() if ": " in line)
            # Entries without it come from the installer or unattended-upgrades
            if "Requested-By" not in fields:
                continue
            # "Install: foo:amd64 (1.0-1), libbar:amd64 (2.0-1, automatic)"
            for name, details in re.findall(r"([a-z0-9][a-z0-9+.-]*)(?::\S+)? \(([^)]*)\)", fields.get("Install", "")):
                if "automatic" not in details:
                    first[name] = min(first.get(name, fields["Start-Date"]), fields["Start-Date"])
    return first


def sources(names: list[str]) -> dict[str, set[str]]:
    """Repositories apt can install each package from, e.g. {"code": {"https://packages.microsoft.com/repos/code stable/main"}}."""
    if not names:
        return {}
    result = {}
    for line in _run("apt-cache", "policy", *names).splitlines():
        if not line.startswith(" "):
            pkg = result.setdefault(line.removesuffix(":"), set())
        # "        500 https://repository.spotify.com stable/non-free amd64 Packages"
        elif match := re.match(r"\s+\d+ (\w+://\S+ \S+)", line):
            pkg.add(match[1])
    return result


def is_third_party(source: str) -> bool:
    return not (urlparse(source.split()[0]).hostname or "").endswith("debian.org")
