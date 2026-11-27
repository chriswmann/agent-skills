#!/usr/bin/env bash
# Symlink every skill in this repository into one or more Claude profiles.
#
#   ./install.sh                 offer to search $HOME for profiles, then choose which to use
#   ./install.sh DIR [DIR ...]   install into each DIR's skills folder, no questions
#   ./install.sh --all           install into every profile found, no questions
#
# A profile is a Claude config directory: ~/.claude, or any directory at the top of $HOME that
# Claude Code uses through CLAUDE_CONFIG_DIR (for example ~/.claude-work). Skills go in
# <profile>/skills. A DIR argument may be a profile or its skills folder.
# Existing entries with the same name are left alone and reported.
# Written for bash 3.2, so it runs on the macOS system shell.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Print one profile directory per line, sorted, without duplicates.
find_profiles() {
  {
    if [ -n "${CLAUDE_CONFIG_DIR:-}" ] && [ -d "$CLAUDE_CONFIG_DIR" ]; then
      (cd "$CLAUDE_CONFIG_DIR" && pwd)
    fi
    for dir in "$HOME"/.[!.]* "$HOME"/*; do
      [ -d "$dir" ] && [ ! -L "$dir" ] || continue
      case "$(basename "$dir")" in
        .claude | .claude[-_.]* | claude[-_.]*) ;;
        *) [ -d "$dir/projects" ] || continue ;;  # other names must look like a profile
      esac
      if [ -e "$dir/settings.json" ] || [ -e "$dir/.credentials.json" ] ||
        [ -d "$dir/projects" ] || [ -d "$dir/skills" ] || [ -d "$dir/plugins" ] ||
        [ -e "$dir/CLAUDE.md" ]; then
        echo "$dir"
      fi
    done
  } | sort -u
}

install_into() {
  local target="$1"
  case "$(basename "$target")" in
    skills) ;;
    *) target="$target/skills" ;;
  esac
  mkdir -p "$target"
  echo "== $target"
  for skill in "$repo"/*/SKILL.md; do
    local dir name link
    dir="$(dirname "$skill")"
    name="$(basename "$dir")"
    link="$target/$name"
    if [ -L "$link" ] && [ "$(readlink "$link")" = "$dir" ]; then
      echo "   ok       $name"
    elif [ -e "$link" ] || [ -L "$link" ]; then
      echo "   skipped  $name (already exists)"
    else
      ln -s "$dir" "$link"
      echo "   linked   $name"
    fi
  done
}

# Ask which of the found profiles to use. Sets the global array `chosen`.
choose() {
  local i=1 answer n
  for p in "${profiles[@]}"; do
    printf '  %d) %s\n' "$i" "${p/#$HOME/\~}"
    i=$((i + 1))
  done
  while :; do
    printf 'Install into which? Numbers separated by spaces, "a" for all, "q" to quit: '
    read -r answer || exit 1
    chosen=()
    case "$answer" in
      a | A | all) chosen=("${profiles[@]}"); return ;;
      q | Q) exit 0 ;;
    esac
    for n in $answer; do
      case "$n" in
        *[!0-9]* | '') chosen=(); break ;;
      esac
      if [ "$n" -ge 1 ] && [ "$n" -le "${#profiles[@]}" ]; then
        chosen+=("${profiles[$((n - 1))]}")
      else
        chosen=(); break
      fi
    done
    [ "${#chosen[@]}" -gt 0 ] && return
    echo "Not understood. Try e.g. \"1 3\"."
  done
}

profiles=()
while IFS= read -r line; do profiles+=("$line"); done < <(find_profiles)
chosen=()

if [ "$#" -gt 0 ] && [ "$1" = "--all" ]; then
  [ "${#profiles[@]}" -gt 0 ] || { echo "No Claude profiles found in $HOME." >&2; exit 1; }
  chosen=("${profiles[@]}")
elif [ "$#" -gt 0 ]; then
  chosen=("$@")
elif [ ! -t 0 ]; then
  chosen=("$HOME/.claude")  # not interactive: the default profile only
else
  printf 'Search %s for Claude profiles? [Y/n] ' "$HOME"
  read -r answer || exit 1
  case "$answer" in
    n | N | no) chosen=("$HOME/.claude") ;;
    *)
      if [ "${#profiles[@]}" -eq 0 ]; then
        echo "No profiles found; using ~/.claude."
        chosen=("$HOME/.claude")
      else
        echo "Found ${#profiles[@]} profile(s):"
        choose
      fi
      ;;
  esac
fi

for p in "${chosen[@]}"; do install_into "$p"; done
