#!/bin/bash

# Test script for notification hooks
# Run this to verify notifications are working

echo "Testing OS notifications..."
echo ""

# Test 1: Stop notification
echo "1. Testing Stop notification (should show 'Claude has finished')..."
node .claude/hooks/stop-notification.js
sleep 2

# Test 2: Info notification
echo "2. Testing Info notification..."
echo '{"title":"Claude Code Test","message":"This is a test info notification","type":"info"}' | node .claude/hooks/notification-hook.js
sleep 2

# Test 3: Success notification
echo "3. Testing Success notification..."
echo '{"title":"Claude Code Test","message":"This is a test success notification","type":"success"}' | node .claude/hooks/notification-hook.js
sleep 2

# Test 4: Warning notification
echo "4. Testing Warning notification..."
echo '{"title":"Claude Code Test","message":"This is a test warning notification","type":"warning"}' | node .claude/hooks/notification-hook.js
sleep 2

# Test 5: Error notification
echo "5. Testing Error notification..."
echo '{"title":"Claude Code Test","message":"This is a test error notification","type":"error"}' | node .claude/hooks/notification-hook.js

echo ""
echo "✓ All notification tests sent!"
echo "You should have seen 5 macOS notifications with different sounds."
