#!/usr/bin/env python3
"""Add the cache status line to one profile's settings.json. Used by install.sh.

    configure.py SETTINGS check             print: none | ours | other:<command>
    configure.py SETTINGS add|wrap|replace  write the statusLine entry

add      only when there is no status line yet
wrap     keep the existing status line and append the cache segment to it
replace  discard the existing status line

Before writing, the old file is copied to settings.json.bak-YYYYMMDD-HHMMSS. Other keys are kept.
"""

from __future__ import annotations

import json
import shlex
import shutil
import sys
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("cache.py")
OURS = f"python3 {shlex.quote(str(SCRIPT))}"


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[2] not in ("check", "add", "wrap", "replace"):
        print(__doc__, file=sys.stderr)
        return 2
    path, action = Path(sys.argv[1]).expanduser(), sys.argv[2]
    try:
        settings = json.loads(path.read_text()) if path.exists() else {}
    except ValueError:
        print(f"error: {path} is not valid JSON; leaving it alone", file=sys.stderr)
        return 1
    current = settings.get("statusLine") or {}
    command = current.get("command", "") if isinstance(current, dict) else ""

    if action == "check":
        print("none" if not command else "ours" if command.startswith(OURS) else f"other:{command}")
        return 0

    if action == "add" and command:
        print("error: a status line already exists; use wrap or replace", file=sys.stderr)
        return 1
    new_command = f"{OURS} --wrap {shlex.quote(command)}" if action == "wrap" and command else OURS
    entry = dict(current) if isinstance(current, dict) and action == "wrap" else {}
    entry.update({"type": "command", "command": new_command, "refreshInterval": 1})
    settings["statusLine"] = entry

    if path.exists():
        shutil.copy2(path, path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n")
    print(new_command)
    return 0


if __name__ == "__main__":
    sys.exit(main())
