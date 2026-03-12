#!/usr/bin/env bash
set -euo pipefail

# ANSI colors
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[32m'
YELLOW='\033[33m'
CYAN='\033[36m'
BLUE='\033[34m'
MAGENTA='\033[35m'
RED='\033[31m'
WHITE='\033[37m'

GMUX_DIR=".gmux"
CONFIG_FILE="$GMUX_DIR/config.json"
TASKS_DIR="$GMUX_DIR/tasks"
STATUS_DIR="$GMUX_DIR/status"
LOG_FILE="$GMUX_DIR/log.jsonl"

# ── helpers ──────────────────────────────────────────────────────────────────

jq_safe() {
  if command -v jq &>/dev/null; then
    jq -r "$@" 2>/dev/null || echo ""
  else
    # fallback: crude grep-based extraction for key:"value" patterns
    local key="${2:-.}"
    grep -o "\"${key#.}\":[^,}]*" "$1" 2>/dev/null | head -1 | sed 's/.*: *"\(.*\)"/\1/' || echo ""
  fi
}

elapsed_seconds() {
  local start_ts="$1"
  local now
  now=$(date +%s)
  # parse ISO 8601 — try GNU date, fall back to BSD date
  local start
  start=$(date -d "$start_ts" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "${start_ts%%.*}" +%s 2>/dev/null || echo "$now")
  echo $(( now - start ))
}

format_elapsed() {
  local secs="$1"
  local h=$(( secs / 3600 ))
  local m=$(( (secs % 3600) / 60 ))
  local s=$(( secs % 60 ))
  printf "%02d:%02d:%02d" "$h" "$m" "$s"
}

seconds_ago() {
  local ts="$1"
  local secs
  secs=$(elapsed_seconds "$ts")
  echo "${secs}s ago"
}

pad_right() {
  local str="$1"
  local width="$2"
  printf "%-${width}s" "$str"
}

hr() {
  local char="${1:-─}"
  local width="${2:-80}"
  printf '%*s' "$width" '' | tr ' ' "$char"
}

# ── sections ─────────────────────────────────────────────────────────────────

print_header() {
  local session_name="gmux"
  local started_at=""
  local elapsed_str="--:--:--"

  if [[ -f "$CONFIG_FILE" ]]; then
    session_name=$(jq_safe '.session_name' "$CONFIG_FILE") || session_name="gmux"
    started_at=$(jq_safe '.started_at' "$CONFIG_FILE") || started_at=""
    [[ -n "$started_at" ]] && elapsed_str=$(format_elapsed "$(elapsed_seconds "$started_at")")
  fi

  echo ""
  printf "${BOLD}${CYAN}  ██████╗ ███╗   ███╗██╗   ██╗██╗  ██╗${RESET}\n"
  printf "${BOLD}${CYAN} ██╔════╝ ████╗ ████║██║   ██║╚██╗██╔╝${RESET}\n"
  printf "${BOLD}${CYAN} ██║  ███╗██╔████╔██║██║   ██║ ╚███╔╝ ${RESET}\n"
  printf "${BOLD}${CYAN} ██║   ██║██║╚██╔╝██║██║   ██║ ██╔██╗ ${RESET}\n"
  printf "${BOLD}${CYAN} ╚██████╔╝██║ ╚═╝ ██║╚██████╔╝██╔╝ ██╗${RESET}\n"
  printf "${BOLD}${CYAN}  ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝${RESET}\n"
  echo ""
  printf "  ${BOLD}Session:${RESET} ${WHITE}${session_name}${RESET}"
  if [[ -n "$started_at" ]]; then
    printf "   ${DIM}started ${started_at}${RESET}"
  fi
  printf "   ${BOLD}Elapsed:${RESET} ${YELLOW}${elapsed_str}${RESET}\n"
  printf "  ${DIM}Updated: $(date '+%Y-%m-%d %H:%M:%S')${RESET}\n"
  echo ""
}

print_tasks() {
  printf "${BOLD}${BLUE}$(hr '─' 80)${RESET}\n"
  printf "${BOLD}  TASKS${RESET}\n"
  printf "${BOLD}${BLUE}$(hr '─' 80)${RESET}\n"

  if [[ ! -d "$TASKS_DIR" ]] || [[ -z "$(ls "$TASKS_DIR"/task-*.json 2>/dev/null)" ]]; then
    printf "  ${DIM}waiting for tasks...${RESET}\n"
    echo ""
    return
  fi

  printf "  ${BOLD}%-6s %-14s %-20s %s${RESET}\n" "ID" "STATUS" "OWNER" "SUBJECT"
  printf "  ${DIM}%-6s %-14s %-20s %s${RESET}\n" "──────" "──────────────" "────────────────────" "───────────────────────────────────────"

  for task_file in "$TASKS_DIR"/task-*.json; do
    [[ -f "$task_file" ]] || continue

    local id status owner subject color
    id=$(jq_safe '.id' "$task_file")
    status=$(jq_safe '.status' "$task_file")
    owner=$(jq_safe '.owner' "$task_file")
    subject=$(jq_safe '.subject' "$task_file")

    [[ -z "$id" ]] && id="?"
    [[ -z "$status" ]] && status="unknown"
    [[ -z "$owner" ]] && owner="—"
    [[ -z "$subject" ]] && subject="(no subject)"

    # Truncate subject if too long
    [[ ${#subject} -gt 40 ]] && subject="${subject:0:37}..."

    case "$status" in
      completed)   color="$GREEN" ;;
      in_progress) color="$YELLOW" ;;
      *)           color="$DIM" ;;
    esac

    printf "  ${color}%-6s %-14s %-20s %s${RESET}\n" "$id" "$status" "$owner" "$subject"
  done
  echo ""
}

print_agents() {
  printf "${BOLD}${MAGENTA}$(hr '─' 80)${RESET}\n"
  printf "${BOLD}  AGENTS${RESET}\n"
  printf "${BOLD}${MAGENTA}$(hr '─' 80)${RESET}\n"

  if [[ ! -d "$STATUS_DIR" ]] || [[ -z "$(ls "$STATUS_DIR"/*.json 2>/dev/null)" ]]; then
    printf "  ${DIM}waiting for agents...${RESET}\n"
    echo ""
    return
  fi

  printf "  ${BOLD}%-22s %-12s %-16s %s${RESET}\n" "AGENT" "STATE" "CURRENT TASK" "LAST SEEN"
  printf "  ${DIM}%-22s %-12s %-16s %s${RESET}\n" "──────────────────────" "────────────" "────────────────" "──────────"

  for status_file in "$STATUS_DIR"/*.json; do
    [[ -f "$status_file" ]] || continue

    local agent state current_task last_heartbeat last_seen color
    agent=$(jq_safe '.agent' "$status_file")
    state=$(jq_safe '.state' "$status_file")
    current_task=$(jq_safe '.current_task' "$status_file")
    last_heartbeat=$(jq_safe '.last_heartbeat' "$status_file")

    [[ -z "$agent" ]] && agent=$(basename "$status_file" .json)
    [[ -z "$state" ]] && state="unknown"
    [[ -z "$current_task" ]] || [[ "$current_task" == "null" ]] && current_task="—"
    if [[ -n "$last_heartbeat" ]] && [[ "$last_heartbeat" != "null" ]]; then
      last_seen=$(seconds_ago "$last_heartbeat")
    else
      last_seen="—"
    fi

    case "$state" in
      working)   color="$GREEN" ;;
      reviewing) color="$YELLOW" ;;
      idle)      color="$DIM" ;;
      *)         color="$WHITE" ;;
    esac

    printf "  ${color}%-22s %-12s %-16s %s${RESET}\n" "$agent" "$state" "$current_task" "$last_seen"
  done
  echo ""
}

print_git() {
  printf "${BOLD}${GREEN}$(hr '─' 80)${RESET}\n"
  printf "${BOLD}  GIT — last 5 commits${RESET}\n"
  printf "${BOLD}${GREEN}$(hr '─' 80)${RESET}\n"

  if ! git rev-parse --git-dir &>/dev/null 2>&1; then
    printf "  ${DIM}not a git repository${RESET}\n"
    echo ""
    return
  fi

  git log --oneline -5 --color=always 2>/dev/null | while IFS= read -r line; do
    printf "  %s\n" "$line"
  done
  echo ""
}

print_activity() {
  printf "${BOLD}${YELLOW}$(hr '─' 80)${RESET}\n"
  printf "${BOLD}  ACTIVITY — last 10 entries${RESET}\n"
  printf "${BOLD}${YELLOW}$(hr '─' 80)${RESET}\n"

  if [[ ! -f "$LOG_FILE" ]]; then
    printf "  ${DIM}waiting for activity...${RESET}\n"
    echo ""
    return
  fi

  tail -10 "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
    local ts agent action message
    if command -v jq &>/dev/null; then
      ts=$(echo "$line" | jq -r '.ts // ""' 2>/dev/null)
      agent=$(echo "$line" | jq -r '.agent // ""' 2>/dev/null)
      action=$(echo "$line" | jq -r '.action // ""' 2>/dev/null)
      message=$(echo "$line" | jq -r '.message // ""' 2>/dev/null)
    else
      ts=$(echo "$line" | grep -o '"ts":"[^"]*"' | sed 's/"ts":"//;s/"//')
      agent=$(echo "$line" | grep -o '"agent":"[^"]*"' | sed 's/"agent":"//;s/"//')
      action=$(echo "$line" | grep -o '"action":"[^"]*"' | sed 's/"action":"//;s/"//')
      message=$(echo "$line" | grep -o '"message":"[^"]*"' | sed 's/"message":"//;s/"//')
    fi

    # Shorten ISO timestamp to HH:MM:SS
    local short_ts
    short_ts=$(echo "$ts" | sed 's/T/ /;s/\.[0-9]*//' | awk '{print $2}' | cut -c1-8)
    [[ -z "$short_ts" ]] && short_ts="$ts"

    printf "  ${DIM}%s${RESET}  ${CYAN}%-18s${RESET}  ${DIM}%-12s${RESET}  %s\n" \
      "$short_ts" "$agent" "$action" "$message"
  done
  echo ""
}

# ── main ─────────────────────────────────────────────────────────────────────

clear
print_header
print_tasks
print_agents
print_git
print_activity
printf "${DIM}$(hr '─' 80)${RESET}\n"
