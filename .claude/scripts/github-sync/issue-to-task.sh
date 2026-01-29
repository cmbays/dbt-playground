#!/usr/bin/env bash
# issue-to-task.sh - Converts GitHub issue to Claude TaskCreate call
# Usage: issue-to-task.sh <issue-number>
# Output: TaskCreate call with validated metadata (stdout)
# Exit codes: 0 = success, 1 = validation error, 2 = GitHub error

set -euo pipefail

# Check dependencies
for cmd in gh jq; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: $cmd not found. Install required dependencies:" >&2
    echo "  gh: https://cli.github.com/" >&2
    echo "  jq: brew install jq (macOS) or apt-get install jq (Linux)" >&2
    exit 2
  fi
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE_SCRIPT="$SCRIPT_DIR/../core/validate-metadata.sh"

# Step 1: Validate arguments
if [[ $# -ne 1 ]]; then
  echo "Usage: issue-to-task.sh <issue-number>" >&2
  exit 2
fi

ISSUE_NUM="$1"

if ! [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]]; then
  echo "ERROR: Issue number must be integer, got: $ISSUE_NUM" >&2
  exit 2
fi

# Step 2: Fetch issue from GitHub
echo "Fetching GitHub issue #$ISSUE_NUM..." >&2

if ! ISSUE_JSON=$(gh issue view "$ISSUE_NUM" --json title,body,labels,number 2>&1); then
  echo "ERROR: Failed to fetch issue #$ISSUE_NUM" >&2
  echo "$ISSUE_JSON" >&2
  exit 2
fi

# Step 3: Extract basic fields
TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
BODY=$(echo "$ISSUE_JSON" | jq -r '.body // ""')
LABELS=$(echo "$ISSUE_JSON" | jq -r '.labels[].name' | tr '\n' ',' | sed 's/,$//')

echo "Issue: $TITLE" >&2
echo "Labels: $LABELS" >&2

# Step 4: Parse type from labels
# Extract all type: labels and prioritize epic, task, tdd
TYPE_LABELS=$(echo "$LABELS" | grep -oE 'type:[^,]+' | cut -d':' -f2 || echo "")

if [[ -z "$TYPE_LABELS" ]]; then
  echo "ERROR: No type: label found on issue #$ISSUE_NUM" >&2
  echo "Available labels: $LABELS" >&2
  exit 1
fi

# Prioritize: epic > task > tdd > others
if echo "$TYPE_LABELS" | grep -q '^epic$'; then
  TYPE="epic"
elif echo "$TYPE_LABELS" | grep -q '^task$'; then
  TYPE="task"
elif echo "$TYPE_LABELS" | grep -q '^tdd$'; then
  TYPE="tdd"
else
  # Use first valid type
  TYPE=$(echo "$TYPE_LABELS" | head -1)
  echo "WARNING: Multiple type labels found, using: $TYPE" >&2
fi

# Step 5: Extract metadata based on type
case "$TYPE" in
  epic)
    # Extract epic_id from title or body (pattern: PRD-001, PRD-002, etc.)
    EPIC_ID=$(echo "$TITLE $BODY" | awk '{
      match($0, /PRD-[0-9]{3}/)
      if (RSTART) {
        print substr($0, RSTART, RLENGTH)
        exit
      }
    }')

    # Extract PRD link (format: docs/specs/PRD-*.md)
    PRD=$(echo "$BODY" | awk '{
      match($0, /docs\/specs\/PRD-[0-9]{3}[^[:space:]`]*\.md/)
      if (RSTART) {
        print substr($0, RSTART, RLENGTH)
        exit
      }
    }')

    # Extract TDD link (format: docs/tdd/TDD-*.md)
    TDD=$(echo "$BODY" | awk '{
      match($0, /docs\/tdd\/TDD-[0-9]{3}[^[:space:]`]*\.md/)
      if (RSTART) {
        print substr($0, RSTART, RLENGTH)
        exit
      }
    }')

    # Build metadata JSON
    METADATA=$(jq -n \
      --arg github_issue "$ISSUE_NUM" \
      --arg type "$TYPE" \
      --arg epic_id "$EPIC_ID" \
      --arg prd "$PRD" \
      --arg tdd "$TDD" \
      '{
        github_issue: ($github_issue | tonumber),
        type: $type,
        epic_id: $epic_id,
        prd: $prd
      } + (if $tdd != "" then {tdd: $tdd} else {} end)')
    ;;

  task)
    # Extract epic reference using awk
    EPIC=$(echo "$BODY" | awk '
      /[Ee]pic:/ || /[Pp]art of/ {
        match($0, /#[0-9]+/)
        if (RSTART) {
          print substr($0, RSTART+1, RLENGTH-1)
          exit
        }
      }
    ')

    # Extract TDD section
    TDD_SECTION=$(echo "$BODY" | awk '
      /[Ii]mplements:/ || /[Tt][Dd][Dd] [Ss]ection:/ {
        match($0, /§[0-9]+/)
        if (RSTART) {
          print substr($0, RSTART, RLENGTH)
          exit
        }
      }
    ')

    # Extract task ID
    TASK_ID=$(echo "$BODY" | awk '
      /[Tt]ask [Ii][Dd]:/ || /\*\*[Tt]ask\*\*:/ {
        match($0, /T[0-9.]+/)
        if (RSTART) {
          print substr($0, RSTART, RLENGTH)
          exit
        }
      }
    ')

    # Extract effort from labels and uppercase
    EFFORT=$(echo "$LABELS" | grep -oE 'effort:[^,]+' | cut -d':' -f2 | tr '[:lower:]' '[:upper:]' || echo "")

    # Build metadata JSON
    METADATA=$(jq -n \
      --arg github_issue "$ISSUE_NUM" \
      --arg type "$TYPE" \
      --arg task_id "$TASK_ID" \
      --arg epic "$EPIC" \
      --arg tdd_section "$TDD_SECTION" \
      --arg effort "$EFFORT" \
      '{
        github_issue: ($github_issue | tonumber),
        type: $type
      } + (if $task_id != "" then {task_id: $task_id} else {} end)
        + (if $epic != "" then {epic: ($epic | tonumber)} else {} end)
        + (if $tdd_section != "" then {tdd_section: $tdd_section} else {} end)
        + (if $effort != "" then {effort: $effort} else {} end)
        + {sync_on_complete: true}')
    ;;

  tdd)
    # Extract TDD ID from body
    TDD_ID=$(echo "$BODY" | awk '
      /[Tt][Dd][Dd] [Ii][Dd]:/ || /[Tt][Dd][Dd]:/ {
        match($0, /[0-9]{3}/)
        if (RSTART) {
          print substr($0, RSTART, RLENGTH)
          exit
        }
      }
    ')

    # Extract Epic ID
    EPIC_ID=$(echo "$BODY" | awk '
      /[Ee]pic [Ii][Dd]:/ || /[Ee]pic:/ {
        match($0, /PRD-[0-9]{3}/)
        if (RSTART) {
          print substr($0, RSTART, RLENGTH)
          exit
        }
      }
    ')

    # Build metadata JSON
    METADATA=$(jq -n \
      --arg github_issue "$ISSUE_NUM" \
      --arg type "$TYPE" \
      --arg tdd_id "$TDD_ID" \
      --arg epic_id "$EPIC_ID" \
      '{
        github_issue: ($github_issue | tonumber),
        type: $type,
        tdd_id: $tdd_id,
        epic_id: $epic_id,
        sync_on_complete: true
      }')
    ;;

  *)
    echo "ERROR: Unsupported task type: $TYPE" >&2
    exit 1
    ;;
esac

# Step 6: Validate metadata
echo "Validating metadata..." >&2

if ! "$VALIDATE_SCRIPT" "$METADATA" 2>&1; then
  echo "ERROR: Metadata validation failed" >&2
  echo "Metadata: $METADATA" >&2
  exit 1
fi

# Step 7: Generate TaskCreate call
echo "Generating TaskCreate call..." >&2

# Escape body for JSON string
BODY_ESCAPED=$(echo "$BODY" | jq -Rs .)

# Format metadata for display (pretty-printed)
METADATA_PRETTY=$(echo "$METADATA" | jq .)

# Output TaskCreate call
cat <<EOF

TaskCreate({
  subject: "$TITLE",
  description: $BODY_ESCAPED,
  metadata: $METADATA_PRETTY
})

EOF

echo "✓ Conversion successful. Copy the TaskCreate call above." >&2
exit 0
