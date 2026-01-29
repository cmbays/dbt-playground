#!/bin/bash
# scripts/count-agent-tokens.sh
# Counts approximate tokens in agent files
# Token estimation: 1 token ≈ 4 characters

echo "Agent Token Count Report - $(date)"
echo "================================"
echo ""

total=0
for file in .claude/agents/*.md; do
  if [[ -f "$file" ]]; then
    filename=$(basename "$file")
    # Skip non-agent files
    if [[ "$filename" == "AGENTS.md" ]] || [[ "$filename" == "README.md" ]] || [[ "$filename" == "DOC_MAINTENANCE.md" ]]; then
      continue
    fi
    chars=$(wc -c < "$file" | tr -d ' ')
    tokens=$((chars / 4))
    total=$((total + tokens))
    printf "%-35s %6d chars  ~%5d tokens\n" "$filename" "$chars" "$tokens"
  fi
done

echo ""
echo "================================"
printf "%-35s %6d chars  ~%5d tokens\n" "TOTAL (agents only)" "$((total * 4))" "$total"
echo ""

# Also count supporting files
echo "Supporting files:"
for file in .claude/agents/AGENTS.md .claude/agents/README.md .claude/agents/DOC_MAINTENANCE.md; do
  if [[ -f "$file" ]]; then
    chars=$(wc -c < "$file" | tr -d ' ')
    tokens=$((chars / 4))
    printf "%-35s %6d chars  ~%5d tokens\n" "$(basename $file)" "$chars" "$tokens"
  fi
done
