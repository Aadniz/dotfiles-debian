import sys
from pathlib import Path

import pyjson5

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "folder-mapping.jsonc"
README_FILE = ROOT / "README.md"


def load_config() -> dict:
    try:
        return pyjson5.loads(CONFIG_FILE.read_text())
    except (OSError, pyjson5.Json5DecoderException) as e:
        sys.exit(f"Error reading {CONFIG_FILE}: {e}")
