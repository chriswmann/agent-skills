# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Read-only scan of a Claude Code setup, written as one JSON document.

Usage:
    uv run --script scan.py [--profile DIR] [--project DIR] [--days 30] [-o OUT.json]

--profile is the Claude config directory to audit: $CLAUDE_CONFIG_DIR if set, else ~/.claude.
Below, <profile> is that directory.

It reads, and never writes, these places:
  - skills in <profile>/skills and <project>/.claude/skills (one folder per skill, with SKILL.md)
  - memory files: <profile>/CLAUDE.md, <project>/CLAUDE.md, <project>/CLAUDE.local.md,
    <project>/AGENTS.md, <project>/.claude/CLAUDE.md, and any files they import with @path
  - settings: <profile>/settings.json, <project>/.claude/settings.json, settings.local.json
  - MCP servers: the profile's .claude.json (~/.claude.json for ~/.claude, otherwise
    <profile>/.claude.json), top-level and per-project, and <project>/.mcp.json
  - transcripts in <profile>/projects/*/*.jsonl modified in the last --days days

Token counts are estimates: characters / 4.

Usage counts come from transcripts: a Skill tool call names the skill, and a slash command typed
by the user appears as <command-name>/name</command-name>. An MCP tool call is named
mcp__<server>__<tool>. A skill with no use in the window is a candidate, not a verdict: use in
other machines, Cowork or the desktop app is not visible here.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

HOME = Path.home()
CLAUDE = HOME / ".claude"  # replaced by --profile in main()
COMMAND_RE = re.compile(r"<command-name>/?([\w:.-]+)</command-name>")
IMPORT_RE = re.compile(r"(?m)^\s*@([~\w./-]+)")


def tokens(text: str) -> int:
    return round(len(text) / 4)


def front_matter(text: str) -> dict[str, str]:
    """Parse the simple key: value front matter that skills use. Folded values are joined."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out: dict[str, str] = {}
    key = None
    for line in text[3:end].splitlines():
        if not line.strip():
            continue
        if line[0] not in " \t" and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            out[key] = value.strip().strip("\"'") if value.strip() not in (">", "|", ">-") else ""
        elif key:
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def scan_skills(root: Path, scope: str) -> list[dict]:
    found = []
    if not root.is_dir():
        return found
    for skill_md in sorted(root.glob("*/SKILL.md")):
        text = skill_md.read_text(errors="replace")
        fm = front_matter(text)
        manual = fm.get("disable-model-invocation", "").lower() == "true"
        description = fm.get("description", "")
        found.append(
            {
                "name": fm.get("name") or skill_md.parent.name,
                "scope": scope,
                "path": str(skill_md.parent),
                "symlink": skill_md.parent.is_symlink(),
                "user_invoked_only": manual,
                "description_tokens": 0 if manual else tokens(description),
                "body_tokens": tokens(text),
                "description": description,
            }
        )
    return found


def memory_file(path: Path, seen: set[Path]) -> list[dict]:
    path = path.expanduser()
    if not path.is_file() or path.resolve() in seen:
        return []
    seen.add(path.resolve())
    text = path.read_text(errors="replace")
    out = [{"path": str(path), "lines": text.count("\n") + 1, "tokens": tokens(text)}]
    for ref in IMPORT_RE.findall(text):
        target = Path(ref).expanduser()
        if not target.is_absolute():
            target = path.parent / target
        out += memory_file(target, seen)
    return out


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def scan_mcp(project: Path) -> list[dict]:
    servers = []
    state = HOME / ".claude.json" if CLAUDE == HOME / ".claude" else CLAUDE / ".claude.json"
    user = load_json(state)
    for name in user.get("mcpServers", {}):
        servers.append({"name": name, "scope": "user", "source": str(state)})
    for proj, cfg in user.get("projects", {}).items():
        if Path(proj).resolve() == project.resolve():
            for name in cfg.get("mcpServers", {}):
                servers.append({"name": name, "scope": "local", "source": str(state)})
    for name in load_json(project / ".mcp.json").get("mcpServers", {}):
        servers.append({"name": name, "scope": "project", "source": ".mcp.json"})
    return servers


def scan_settings(project: Path) -> list[dict]:
    out = []
    for path in (
        CLAUDE / "settings.json",
        project / ".claude" / "settings.json",
        project / ".claude" / "settings.local.json",
    ):
        data = load_json(path)
        if not data:
            continue
        perms = data.get("permissions", {})
        out.append(
            {
                "path": str(path),
                "allow": len(perms.get("allow", [])),
                "deny": len(perms.get("deny", [])),
                "hooks": sorted(data.get("hooks", {})),
                "enabled_plugins": sorted(k for k, v in data.get("enabledPlugins", {}).items() if v),
            }
        )
    return out


def scan_usage(days: int) -> dict:
    cutoff = time.time() - days * 86400
    skills: Counter[str] = Counter()
    last_used: dict[str, float] = {}
    mcp: Counter[str] = Counter()
    sessions = 0
    for path in (CLAUDE / "projects").glob("*/*.jsonl"):
        mtime = path.stat().st_mtime
        if mtime < cutoff:
            continue
        sessions += 1
        with path.open(errors="replace") as fh:
            for line in fh:
                if '"Skill"' not in line and "command-name" not in line and "mcp__" not in line:
                    continue
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                content = (event.get("message") or {}).get("content")
                names: list[str] = []
                if isinstance(content, str):
                    names += COMMAND_RE.findall(content)
                elif isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "text":
                            names += COMMAND_RE.findall(block.get("text", ""))
                        if block.get("type") != "tool_use":
                            continue
                        tool = block.get("name", "")
                        if tool == "Skill":
                            names.append(str((block.get("input") or {}).get("skill", "")))
                        elif tool.startswith("mcp__"):
                            mcp[tool.split("__")[1]] += 1
                for name in filter(None, names):
                    skills[name] += 1
                    last_used[name] = max(last_used.get(name, 0), mtime)
    return {
        "window_days": days,
        "sessions_scanned": sessions,
        "skills": {
            k: {"uses": v, "last_used": time.strftime("%Y-%m-%d", time.localtime(last_used[k]))}
            for k, v in skills.most_common()
        },
        "mcp_servers": dict(mcp.most_common()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    default_profile = os.environ.get("CLAUDE_CONFIG_DIR") or str(HOME / ".claude")
    parser.add_argument("--profile", type=Path, default=Path(default_profile))
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    global CLAUDE
    CLAUDE = args.profile.expanduser().resolve()
    project = args.project.resolve()

    seen: set[Path] = set()
    memory = []
    for path in (
        CLAUDE / "CLAUDE.md",
        project / "CLAUDE.md",
        project / ".claude" / "CLAUDE.md",
        project / "CLAUDE.local.md",
        project / "AGENTS.md",
    ):
        memory += memory_file(path, seen)

    skills = scan_skills(CLAUDE / "skills", "user") + scan_skills(project / ".claude" / "skills", "project")
    usage = scan_usage(args.days)
    for skill in skills:
        hit = usage["skills"].get(skill["name"])
        skill["uses"] = hit["uses"] if hit else 0
        skill["last_used"] = hit["last_used"] if hit else None

    report = {
        "profile": str(CLAUDE),
        "project": str(project),
        "memory_files": memory,
        "memory_tokens": sum(m["tokens"] for m in memory),
        "skills": skills,
        "skill_description_tokens": sum(s["description_tokens"] for s in skills),
        "mcp_servers": scan_mcp(project),
        "settings": scan_settings(project),
        "usage": usage,
    }
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + "\n")
        print(args.output)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
