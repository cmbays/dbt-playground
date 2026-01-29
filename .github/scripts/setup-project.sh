#!/bin/bash
# Setup GitHub Project for Japanese Study Site

PROJECT_ID="PVT_kwHOAX7HsM4BNaAq"  # Used for field creation
PROJECT_NUM="1"                     # Used for item operations
OWNER="cmbays"
REPO="japanese-study-site"

echo "Setting up GitHub Project fields for Japanese Study Site..."
echo ""

# Create Status field
echo "Creating Status field..."
gh project field-create $PROJECT_ID \
  --owner $OWNER \
  --name "Status" \
  --data-type SINGLE_SELECT \
  --single-select-options "Backlog,Blocked,Ready,In Progress,Review,Done" \
  2>/dev/null || echo "  Status field already exists"

# Create Effort field
echo "Creating Effort field..."
gh project field-create $PROJECT_ID \
  --owner $OWNER \
  --name "Effort" \
  --data-type SINGLE_SELECT \
  --single-select-options "XS,S,M,L,XL" \
  2>/dev/null || echo "  Effort field already exists"

# Create Wave field
echo "Creating Wave field..."
gh project field-create $PROJECT_ID \
  --owner $OWNER \
  --name "Wave" \
  --data-type SINGLE_SELECT \
  --single-select-options "Wave 1,Wave 2,Wave 3,Wave 4,Wave 5" \
  2>/dev/null || echo "  Wave field already exists"

# Create Persona field
echo "Creating Persona field..."
gh project field-create $PROJECT_ID \
  --owner $OWNER \
  --name "Persona" \
  --data-type SINGLE_SELECT \
  --single-select-options "PM,Architect,Developer,Tester,Sensei,Design" \
  2>/dev/null || echo "  Persona field already exists"

# Create Priority field
echo "Creating Priority field..."
gh project field-create $PROJECT_ID \
  --owner $OWNER \
  --name "Priority" \
  --data-type SINGLE_SELECT \
  --single-select-options "P0,P1,P2,P3" \
  2>/dev/null || echo "  Priority field already exists"

# Create Epic field (text)
echo "Creating Epic field..."
gh project field-create $PROJECT_ID \
  --owner $OWNER \
  --name "Epic" \
  --data-type TEXT \
  2>/dev/null || echo "  Epic field already exists"

echo ""
echo "✅ Project fields created successfully!"
echo ""
echo "Next steps:"
echo "1. ✅ Issue templates created in .github/ISSUE_TEMPLATE/"
echo "2. ✅ Run this script to create custom fields"
echo "3. Update existing epic issues (#7, #8, #9)"
echo "4. Create all 24 task issues using templates"
echo "5. Link issues to project: gh project item-add $PROJECT_NUM --owner $OWNER --url <ISSUE_URL>"
echo ""
echo "Note: Use PROJECT_NUM=$PROJECT_NUM for item operations (not PROJECT_ID)"
