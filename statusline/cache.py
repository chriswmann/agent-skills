#!/usr/bin/env python3
"""Claude Code status line: how long until this chat's prompt cache goes cold.

Claude Code runs this with the session as JSON on stdin and shows what it prints. Configure it
in a profile's settings.json:

    "statusLine": {"type": "command", "command": "python3 /path/to/cache.py", "refreshInterval": 1}

refreshInterval 1 re-runs it every second, so the countdown ticks.

    cache.py                 print the cache segment only
    cache.py --wrap CMD      run CMD (an existing status line) on the same input, then append the
                             cache segment to the end of its last line

Output, coloured by state:

    cache 3:42 · 1h · 182k to rebuild       green: more than a minute left
    cache 0:38 · send now to keep it        amber: a minute or less
    cache cold · next message writes 182k   red: expired (adds "consider /handoff" when large)

Where it gets the numbers:
  1. The prompt_cache object Claude Code passes (version 2.1.251 and later): warm, expires_at,
     ttl, recache_tokens_if_cold.
  2. Otherwise the transcript: the time of the last main-thread reply, plus the lifetime its
     usage shows it was written with (1h or 5m), and its cached token count.

Needs only the Python standard library. Set NO_COLOR to turn colours off.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime

GREEN, AMBER, RED, DIM, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"
WARN_SECONDS = 60
HANDOFF_TOKENS = 100_000
TTL_SECONDS = {"5m": 300, "1h": 3600}
TAIL_BYTES = 2_000_000


def tokens(n: int | None) -> str:
    if not n:
        return "?"
    return f"{n / 1_000_000:.1f}M" if n >= 1_000_000 else f"{round(n / 1000)}k"


def from_prompt_cache(pc: dict) -> dict | None:
    """State from Claude Code's own prompt_cache field, if it is present and usable."""
    if not pc:
        return None
    expires = pc.get("expires_at")
    return {
        "warm": bool(pc.get("warm")) and bool(expires),
        "expires_at": float(expires) if expires else None,
        "ttl": pc.get("ttl"),
        "rebuild": pc.get("recache_tokens_if_cold"),
    }


def main_replies(path: str):
    """Yield (timestamp, usage) for main-thread replies, newest first, from the transcript's tail."""
    with open(path, "rb") as fh:
        fh.seek(0, os.SEEK_END)
        fh.seek(max(0, fh.tell() - TAIL_BYTES))
        lines = fh.read().decode("utf-8", "ignore").splitlines()
    for line in reversed(lines):
        if '"assistant"' not in line:
            continue
        try:
            event = json.loads(line)
            replied = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")).timestamp()
        except (ValueError, KeyError, AttributeError):
            continue
        if event.get("type") == "assistant" and not event.get("isSidechain"):
            yield replied, (event.get("message") or {}).get("usage") or {}


def from_transcript(path: str | None) -> dict | None:
    """State worked out from the transcript.

    Any reply that reads or writes the cache restarts its lifetime from that reply. The lifetime
    itself (5m or 1h) shows only in replies that wrote to the cache, so it comes from the newest
    such reply; a reply that only read keeps whatever lifetime the cache was written with. If no
    write is in view, assume the shorter 5m and mark it, so the countdown errs on the early side.
    """
    if not path or not os.path.isfile(path):
        return None
    latest = None
    ttl = None
    for replied, usage in main_replies(path):
        created = usage.get("cache_creation") or {}
        used = usage.get("cache_read_input_tokens") or usage.get("cache_creation_input_tokens")
        if latest is None:
            if not used:
                return None  # the newest reply used no cache
            cached = (usage.get("cache_read_input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0)
            latest = (replied, cached)
        if created.get("ephemeral_1h_input_tokens"):
            ttl = "1h"
        elif created.get("ephemeral_5m_input_tokens"):
            ttl = "5m"
        if ttl:
            break
    if latest is None:
        return None
    replied, cached = latest
    expires = replied + TTL_SECONDS[ttl or "5m"]
    return {"warm": expires > time.time(), "expires_at": expires, "ttl": ttl or "5m?", "rebuild": cached}


def segment(state: dict | None, colour: bool) -> str:
    def paint(code: str, text: str) -> str:
        return f"{code}{text}{RESET}" if colour else text

    if state is None:
        return paint(DIM, "cache –")
    left = (state["expires_at"] or 0) - time.time()
    rebuild = tokens(state.get("rebuild"))
    if not state["warm"] or left <= 0:
        text = f"cache cold · next message writes {rebuild}"
        if (state.get("rebuild") or 0) >= HANDOFF_TOKENS:
            text += " · consider /handoff"
        return paint(RED, text)
    clock = f"{int(left) // 60}:{int(left) % 60:02d}"
    if left <= WARN_SECONDS:
        return paint(AMBER, f"cache {clock} · send now to keep it")
    ttl = f" · {state['ttl']}" if state.get("ttl") else ""
    return paint(GREEN, f"cache {clock}{ttl} · {rebuild} to rebuild")


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except ValueError:
        data = {}

    state = from_prompt_cache(data.get("prompt_cache") or {}) or from_transcript(data.get("transcript_path"))
    cache = segment(state, colour="NO_COLOR" not in os.environ)

    wrapped = ""
    if len(sys.argv) >= 3 and sys.argv[1] == "--wrap":
        try:
            wrapped = subprocess.run(
                sys.argv[2], shell=True, input=raw, capture_output=True, text=True, timeout=5
            ).stdout.rstrip("\n")
        except (OSError, subprocess.SubprocessError):
            wrapped = ""
    print(f"{wrapped} · {cache}" if wrapped else cache)
    return 0


if __name__ == "__main__":
    sys.exit(main())
