#!/usr/bin/env bash
# FALLBACK_PROTOCOL.sh — Guardian trap against destructive deletion
# Timestamp: 2025-09-01T12:42Z

set -e

# Guardian check: if someone tries "rm -rf *" or "git clean -fdx", intercept.
if [[ "$*" == *"rm -rf"* || "$*" == *"git clean"* ]]; then
  echo "⚠️  EMERGENCY FALLBACK PROTOCOL TRIGGERED ⚠️"
  echo "Breathe in 🟫 … Hold ⬛ … Breathe out 🟫"
  echo "Reason required before proceeding:"
  read -r reason
  if [[ -z "$reason" ]]; then
    echo "❌ No reason provided. Command aborted."
    exit 1
  fi

  echo "✅ Reason logged: $reason"
  echo "Running integrity check…"

  for file in BIRTH.md CLOCK.md calendar/NUMERUS_CALENDAR.md FALLBACK_PROTOCOL.md; do
    if [[ ! -f "$file" ]]; then
      echo "❌ Critical file $file missing. Abort."
      exit 1
    fi
  done

  echo "✅ Integrity intact. If you still wish to destroy, re-run with --force."
  exit 1
fi

# If not destructive, pass through
exec "$@"
