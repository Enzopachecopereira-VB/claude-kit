#!/usr/bin/env bash
# Fail-closed wrapper for public GitHub writes.
# - Requires an EXPLICIT account handle (never infers the active account).
# - Runs a leak/PII sanitization gate on the body before posting.
# - Restores the previously-active gh account on exit (even on failure).
#
# Usage:
#   gh-post.sh check   <handle>                                  # verify handle is authed; show active
#   gh-post.sh scan    <body-file>                               # run the sanitization gate only
#   gh-post.sh --check-only [<body-file>|-]                       # run the sanitization gate only; stdin by default
#   gh-post.sh --list-classes                                     # list mechanical sanitizer classes
#   gh-post.sh comment <handle> <owner/repo> <issue#> <body-file>
#   gh-post.sh pr      <handle> <owner/repo> <head-branch> <title> <body-file>
#
# Extra deny patterns (newline-separated EREs) can be added via GH_POST_DENY_EXTRA.
set -euo pipefail

die() { printf 'gh-post: %s\n' "$*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

# Baseline leak patterns. Intentionally conservative: better a false positive
# (author reviews) than a leaked secret in a public repo.
DENY_CLASSES=(
  posix-home-path
  home-shorthand
  windows-home-path
  hostname
  email
  github-token
  slack-token
  aws-access-key-id
  anthropic-key
  stripe-live-key
  bearer-token
  jwt
  private-key-pem
  session-id
  absolute-timestamp
)

DENY_PATTERNS=(
  '/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+'
  "(^|[[:space:]])(~|\\\$HOME)/"
  "[A-Za-z]:\\\\Users\\\\[A-Za-z0-9._-]+\\\\"
  '(^|[^A-Za-z0-9_.-])[A-Za-z0-9][A-Za-z0-9-]*\.(local|lan|internal)([^A-Za-z0-9_.-]|$)|(^|[[:space:]])[Hh]ostname:[[:space:]]*[A-Za-z0-9][A-Za-z0-9._-]*'
  '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
  'gh[pousr]_[A-Za-z0-9_]{20,}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'AKIA[0-9A-Z]{16}'
  'sk-ant-[A-Za-z0-9_-]{10,}'
  'sk_live_[A-Za-z0-9]{16,}'
  '(^|[^A-Za-z0-9_])[Bb]earer[[:space:]]+[A-Za-z0-9._~+/-]{20,}'
  '(^|[^A-Za-z0-9_-])[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}([^A-Za-z0-9_-]|$)'
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
  'ses_[A-Za-z0-9_-]{6,}'
  '[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9]{2}:[0-9]{2}:[0-9]{2}'
)

list_classes() {
  local i
  for i in "${!DENY_CLASSES[@]}"; do
    printf '%s\n' "${DENY_CLASSES[$i]}"
  done
  printf '%s\n' 'extra-deny-term (when GH_POST_DENY_EXTRA is set)'
}

grep_ere() {
  local pattern="$1" file="$2" body="$3" hits status
  set +e
  if [ "$file" = "-" ]; then
    hits=$(printf '%s\n' "$body" | LC_ALL=C grep -nE -e "$pattern")
  else
    hits=$(LC_ALL=C grep -nE -e "$pattern" -- "$file")
  fi
  status=$?
  set -e
  [ "$status" -le 1 ] || die "invalid sanitizer regex: $pattern"
  [ "$status" -eq 0 ] && printf '%s\n' "$hits"
  return 0
}

sanitize_gate() {
  local file="$1"
  local body=""
  local dirty=0
  local checked=${#DENY_CLASSES[@]}
  local i class pattern hits extra

  if [ "$file" = "-" ]; then
    body=$(cat)
  else
    [ -f "$file" ] || die "body file not found: $file"
  fi

  for i in "${!DENY_CLASSES[@]}"; do
    class="${DENY_CLASSES[$i]}"
    pattern="${DENY_PATTERNS[$i]}"
    hits=$(grep_ere "$pattern" "$file" "$body")
    if [ -n "$hits" ]; then
      printf 'sanitize: dirty: %s\n%s\n' "$class" "$hits" >&2
      dirty=1
    fi
  done

  if [ -n "${GH_POST_DENY_EXTRA:-}" ]; then
    checked=$((checked + 1))
    while IFS= read -r extra || [ -n "$extra" ]; do
      [ -n "$extra" ] || continue
      hits=$(grep_ere "$extra" "$file" "$body")
      if [ -n "$hits" ]; then
        printf 'sanitize: dirty: extra-deny-term\n%s\n' "$hits" >&2
        dirty=1
      fi
    done <<EOF
${GH_POST_DENY_EXTRA}
EOF
  fi

  if [ "$dirty" -ne 0 ]; then
    die "sanitization failed; fix the body before posting"
  fi

  printf 'sanitize: no match for %s deny classes (see --list-classes)\n' "$checked"
  printf 'sanitize: still requires agent judgment for real usernames without path context, arbitrary hostnames, and internal names not supplied via GH_POST_DENY_EXTRA\n'
}

active_account() { gh auth status 2>/dev/null | awk '/Active account: true/{print prev} {prev=$0}' | grep -oE 'account [A-Za-z0-9_-]+' | awk '{print $2}' | head -1; }
handle_is_authed() { gh auth status 2>/dev/null | grep -qE "account $1\b"; }

PRIOR=""
restore() { [ -n "$PRIOR" ] && gh auth switch --user "$PRIOR" >/dev/null 2>&1 && printf 'restored active account: %s\n' "$PRIOR"; }

use_account() {
  local h="$1"
  [ -n "$h" ] || die "account handle is required (never inferred)"
  handle_is_authed "$h" || die "account '$h' is not authenticated (gh auth login)"
  PRIOR="$(active_account || true)"
  trap restore EXIT
  gh auth switch --user "$h" >/dev/null 2>&1 || die "failed to switch to $h"
  printf 'posting as: %s (will restore: %s)\n' "$h" "${PRIOR:-none}"
}

cmd="${1:-}"
shift || true
case "$cmd" in
  --list-classes)
    list_classes
    ;;
  --check-only|sanitize-only)
    sanitize_gate "${1:--}"
    ;;
  check)
    have gh || die "gh CLI not found"
    h="${1:?usage: check <handle>}"
    printf 'active now: %s\n' "$(active_account || echo unknown)"
    if handle_is_authed "$h"; then printf "handle '%s': authenticated\n" "$h"; else die "handle '$h' not authenticated"; fi
    ;;
  scan)
    sanitize_gate "${1:?usage: scan <body-file>}"
    ;;
  comment)
    have gh || die "gh CLI not found"
    h="${1:?}"; repo="${2:?}"; num="${3:?}"; body="${4:?usage: comment <handle> <owner/repo> <issue#> <body-file>}"
    sanitize_gate "$body"
    use_account "$h"
    gh issue comment "$num" --repo "$repo" --body-file "$body"
    ;;
  pr)
    have gh || die "gh CLI not found"
    h="${1:?}"; repo="${2:?}"; head="${3:?}"; title="${4:?}"; body="${5:?usage: pr <handle> <repo> <head> <title> <body-file>}"
    sanitize_gate "$body"
    use_account "$h"
    gh pr create --repo "$repo" --head "$h:$head" --title "$title" --body-file "$body"
    ;;
  *)
    die "usage: gh-post.sh {--list-classes | --check-only [<body-file>|-] | sanitize-only [<body-file>|-] | check <handle> | scan <body-file> | comment <handle> <repo> <issue#> <body-file> | pr <handle> <repo> <head> <title> <body-file>}"
    ;;
esac
