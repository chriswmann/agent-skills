#!/usr/bin/env bash
# Symlink every skill in this repository into one or more Claude profiles.
#
#   ./install.sh                 offer to search $HOME for profiles, then choose which to use
#   ./install.sh DIR [DIR ...]   install into each DIR's skills folder, no questions
#   ./install.sh --all           install into every profile found, no questions
#   --statusline                 with DIR or --all: also add the cache countdown status line to
#                                each profile that has no status line yet (others are skipped)
#
# Run interactively, it also offers the cache countdown status line (statusline/cache.py) and,
# for a profile that already has a status line, asks whether to wrap it, replace it or skip.
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

# Add the cache status line to one profile. $2 is "ask" (interactive) or "auto".
statusline_into() {
  local profile="$1" mode="$2" settings state answer
  case "$(basename "$profile")" in skills) return ;; esac  # a skills folder, not a profile
  settings="$profile/settings.json"
  state="$(python3 "$repo/statusline/configure.py" "$settings" check)" || return 0
  case "$state" in
    none) python3 "$repo/statusline/configure.py" "$settings" add >/dev/null &&
      echo "   status line added to ${settings/#$HOME/\~}" ;;
    ours) echo "   status line already set in ${settings/#$HOME/\~}" ;;
    other:*)
      if [ "$mode" = auto ]; then
        echo "   status line skipped: ${settings/#$HOME/\~} already has one"
        return
      fi
      echo "   ${settings/#$HOME/\~} already runs: ${state#other:}"
      printf '   [w]rap it (keep it, add the countdown after), [r]eplace it, or [s]kip? [s] '
      read -r answer || return 0
      case "$answer" in
        w | W) python3 "$repo/statusline/configure.py" "$settings" wrap >/dev/null && echo "   wrapped" ;;
        r | R) python3 "$repo/statusline/configure.py" "$settings" replace >/dev/null && echo "   replaced" ;;
        *) echo "   skipped" ;;
      esac
      ;;
  esac
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

statusline=ask
args=()
for a in "$@"; do
  case "$a" in
    --statusline) statusline=auto ;;
    *) args+=("$a") ;;
  esac
done
if [ "${#args[@]}" -gt 0 ] || [ ! -t 0 ]; then
  [ "$statusline" = auto ] || statusline=no  # non-interactive: only with --statusline
fi
set -- ${args[@]+"${args[@]}"}

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

if [ "$statusline" = ask ]; then
  printf '\nAdd the cache countdown status line (statusline/cache.py) to these profiles? [y/N] '
  read -r answer || answer=n
  case "$answer" in y | Y | yes) ;; *) statusline=no ;; esac
fi
if [ "$statusline" != no ]; then
  command -v python3 >/dev/null || { echo "python3 not found; status line not added." >&2; exit 1; }
  for p in "${chosen[@]}"; do
    echo "== ${p/#$HOME/\~}"
    statusline_into "$p" "$statusline"
  done
fi
