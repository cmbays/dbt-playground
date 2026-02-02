#!/usr/bin/env bash
# validate-metadata.sh - Validates Claude task metadata against JSON schema
# Usage: validate-metadata.sh <metadata-json-string>
# Exit codes: 0 = valid, 1 = invalid, 2 = schema error

set -euo pipefail

# Check dependency
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq not found. Install with:" >&2
  echo "  macOS: brew install jq" >&2
  echo "  Linux: apt-get install jq or yum install jq" >&2
  exit 2
fi

# Check if metadata argument provided
if [[ $# -ne 1 ]]; then
  echo "Usage: validate-metadata.sh <metadata-json-string>" >&2
  exit 2
fi

METADATA="$1"

# Step 1: Parse JSON (catch syntax errors)
if ! echo "$METADATA" | jq empty 2>/dev/null; then
  echo "ERROR: Invalid JSON syntax" >&2
  exit 1
fi

# Step 2: Extract type field (required)
TYPE=$(echo "$METADATA" | jq -r '.type // empty')
if [[ -z "$TYPE" ]]; then
  echo "ERROR: Missing required field 'type'" >&2
  exit 1
fi

# Step 3: Validate type is whitelisted
VALID_TYPES=("epic" "task" "tdd" "pm-work" "documentation")
if [[ ! " ${VALID_TYPES[@]} " =~ " ${TYPE} " ]]; then
  echo "ERROR: Invalid type '$TYPE'. Must be one of: ${VALID_TYPES[*]}" >&2
  exit 1
fi

# Step 4: Validate github_issue (if present)
GITHUB_ISSUE=$(echo "$METADATA" | jq -r '.github_issue // empty')
if [[ -n "$GITHUB_ISSUE" ]]; then
  if ! [[ "$GITHUB_ISSUE" =~ ^[0-9]+$ ]] || [[ "$GITHUB_ISSUE" -lt 1 ]]; then
    echo "ERROR: github_issue must be integer > 0, got: $GITHUB_ISSUE" >&2
    exit 1
  fi
fi

# Step 5: Validate sync_on_complete (if present)
SYNC_FLAG=$(echo "$METADATA" | jq -r '.sync_on_complete // empty')
if [[ -n "$SYNC_FLAG" ]] && [[ "$SYNC_FLAG" != "true" ]] && [[ "$SYNC_FLAG" != "false" ]]; then
  echo "ERROR: sync_on_complete must be boolean, got: $SYNC_FLAG" >&2
  exit 1
fi

# Step 6: Type-specific validation
case "$TYPE" in
  epic)
    # Epic requires: epic_id, prd
    EPIC_ID=$(echo "$METADATA" | jq -r '.epic_id // empty')
    PRD=$(echo "$METADATA" | jq -r '.prd // empty')

    if [[ -z "$EPIC_ID" ]]; then
      echo "ERROR: Epic requires 'epic_id' field" >&2
      exit 1
    fi

    if ! [[ "$EPIC_ID" =~ ^PRD-[0-9]{3}$ ]]; then
      echo "ERROR: epic_id must match pattern PRD-XXX, got: $EPIC_ID" >&2
      exit 1
    fi

    if [[ -z "$PRD" ]]; then
      echo "ERROR: Epic requires 'prd' field" >&2
      exit 1
    fi
    ;;

  task)
    # Task optional fields: validate if present
    TDD_SECTION=$(echo "$METADATA" | jq -r '.tdd_section // empty')
    EFFORT=$(echo "$METADATA" | jq -r '.effort // empty')

    if [[ -n "$TDD_SECTION" ]] && ! [[ "$TDD_SECTION" =~ ^§[0-9]+$ ]]; then
      echo "ERROR: tdd_section must match pattern §N, got: $TDD_SECTION" >&2
      exit 1
    fi

    if [[ -n "$EFFORT" ]] && ! [[ "$EFFORT" =~ ^(S|M|L|XL)$ ]]; then
      echo "ERROR: effort must be S/M/L/XL, got: $EFFORT" >&2
      exit 1
    fi
    ;;

  tdd)
    # TDD requires: tdd_id, epic_id
    TDD_ID=$(echo "$METADATA" | jq -r '.tdd_id // empty')
    EPIC_ID=$(echo "$METADATA" | jq -r '.epic_id // empty')

    if [[ -z "$TDD_ID" ]]; then
      echo "ERROR: TDD requires 'tdd_id' field" >&2
      exit 1
    fi

    if ! [[ "$TDD_ID" =~ ^[0-9]{3}$ ]]; then
      echo "ERROR: tdd_id must be 3 digits (001-999), got: $TDD_ID" >&2
      exit 1
    fi

    if [[ -z "$EPIC_ID" ]]; then
      echo "ERROR: TDD requires 'epic_id' field" >&2
      exit 1
    fi

    if ! [[ "$EPIC_ID" =~ ^PRD-[0-9]{3}$ ]]; then
      echo "ERROR: epic_id must match pattern PRD-XXX, got: $EPIC_ID" >&2
      exit 1
    fi
    ;;

  pm-work|documentation)
    # No required fields beyond 'type'
    ;;
esac

# Step 7: All validations passed
echo "✓ Metadata valid: type=$TYPE" >&2
exit 0
