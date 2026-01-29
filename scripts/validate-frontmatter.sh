#!/bin/bash
# scripts/validate-frontmatter.sh
# Validates YAML frontmatter in agent files

echo "Frontmatter Validation Report - $(date)"
echo "========================================"
echo ""

valid=0
invalid=0
missing=0

for file in .claude/agents/*.md; do
  if [[ -f "$file" ]]; then
    filename=$(basename "$file")

    # Skip non-agent files
    if [[ "$filename" == "AGENTS.md" ]] || [[ "$filename" == "README.md" ]] || [[ "$filename" == "DOC_MAINTENANCE.md" ]]; then
      continue
    fi

    # Check if file starts with ---
    first_line=$(head -1 "$file")
    if [[ "$first_line" == "---" ]]; then
      # Extract frontmatter (between first and second ---)
      # Use awk for cross-platform compatibility
      frontmatter=$(awk 'NR>1 && /^---$/{exit} NR>1{print}' "$file")

      # Check required fields
      has_name=$(echo "$frontmatter" | grep -c "^name:")
      has_desc=$(echo "$frontmatter" | grep -c "^description:")
      has_tools=$(echo "$frontmatter" | grep -c "^tools:")

      if [[ $has_name -gt 0 ]] && [[ $has_desc -gt 0 ]] && [[ $has_tools -gt 0 ]]; then
        echo "✅ $filename - Valid frontmatter"
        # Show frontmatter summary
        name=$(echo "$frontmatter" | grep "^name:" | cut -d: -f2 | tr -d ' ')
        tools=$(echo "$frontmatter" | grep "^tools:" | cut -d: -f2-)
        echo "   name: $name"
        echo "   tools: $tools"
        ((valid++))
      else
        echo "⚠️  $filename - Missing required fields"
        [[ $has_name -eq 0 ]] && echo "   ❌ Missing: name"
        [[ $has_desc -eq 0 ]] && echo "   ❌ Missing: description"
        [[ $has_tools -eq 0 ]] && echo "   ❌ Missing: tools"
        ((invalid++))
      fi
    else
      echo "❌ $filename - No frontmatter found"
      ((missing++))
    fi
    echo ""
  fi
done

echo "========================================"
echo "Summary:"
echo "  ✅ Valid:   $valid"
echo "  ⚠️  Invalid: $invalid"
echo "  ❌ Missing: $missing"
echo ""

if [[ $missing -gt 0 ]] || [[ $invalid -gt 0 ]]; then
  exit 1
else
  exit 0
fi
