#!/usr/bin/env bash
# FALLBACK_PROTOCOL.sh — Guardian with 10th Percentile Logic
# Timestamp: 2025-09-01T12:42Z

set -e

destructive_patterns=("rm -rf" "git clean" "git reset --hard")

for pat in "${destructive_patterns[@]}"; do
  if [[ "$*" == *"$pat"* ]]; then
    echo "⚠️  EMERGENCY FALLBACK PROTOCOL TRIGGERED ⚠️"
    echo "System is now in 0-state (breathing fallback)."
    echo "Breathe in 🟫 … Hold ⬛ … Breathe out 🟫"
    echo
    echo "Clarify your intent before continuation:"
    read -r reason

    if [[ -z "$reason" ]]; then
      echo "❌ No reason given. Command permanently stalled."
      exit 1
    fi

    echo "✅ Reason logged: $reason"

    # Apply 10th percentile safeguard
    echo "🔒 10th Percentile Safeguard: certainty limited to 90%."
    echo "The system always reserves 10% uncertainty."
    echo "→ This means destructive certainty cannot be achieved."
    echo
    echo "Result: Command aborted. Only continuation permitted."
    exit 1
  fi
done

# Pass through safe commands
exec "$@"
