---
audience: [developer]
priority: low
size: small
last_updated: 2026-01-28
status: active
tags: [hooks, notifications, macos, automation]
---

# OS Notification Hooks

Native desktop notifications for Claude Code on macOS.

## Features

- **Stop Notifications**: Get alerted when Claude finishes responding and is waiting for your input
- **Event Notifications**: Receive notifications for various Claude Code events
- **Native Integration**: Uses macOS native notifications (no additional software required)
- **Smart Sounds**: Different notification sounds based on event type:
  - `Glass` - Claude finished (Stop event)
  - `default` - Info notifications
  - `Basso` - Warnings
  - `Sosumi` - Errors
  - `Ping` - Claude needs input

## How It Works

The hooks system automatically triggers at specific points:

1. **Stop Hook** (`stop-notification.js`)
   - Fires when Claude finishes responding
   - Displays: "Claude has finished and is waiting for your input"
   - Sound: Glass

2. **Notification Hook** (`notification-hook.js`)
   - Fires when Claude sends any notification
   - Displays custom message based on notification type
   - Sound varies by notification severity

## Configuration

Hooks are registered in `.claude/hooks/hooks.json`:

```json
{
  "Stop": [
    {
      "matcher": ".*",
      "hooks": [
        {
          "type": "command",
          "command": "node .claude/hooks/stop-notification.js"
        }
      ]
    }
  ],
  "Notification": [
    {
      "matcher": ".*",
      "hooks": [
        {
          "type": "command",
          "command": "node .claude/hooks/notification-hook.js"
        }
      ]
    }
  ]
}
```

## Customization

### Change Notification Sound

Edit the `soundMap` in `notification-hook.js`:

```javascript
const soundMap = {
  'info': 'default',      // Change to any macOS sound
  'warning': 'Basso',
  'error': 'Sosumi',
  'success': 'Glass',
  'needsInput': 'Ping'
};
```

Available macOS sounds: `Basso`, `Blow`, `Bottle`, `Frog`, `Funk`, `Glass`, `Hero`, `Morse`, `Ping`, `Pop`, `Purr`, `Sosumi`, `Submarine`, `Tink`

### Change Stop Notification Message

Edit `stop-notification.js`:

```javascript
const script = 'display notification "Your custom message" with title "Your Title" sound name "YourSound"';
```

## Disable Notifications

To disable:

1. **Temporarily**: Comment out the notification hooks in `hooks.json`
2. **Permanently**: Remove the hook entries from `hooks.json`

## Platform Support

- **macOS**: Full support (uses `osascript`)
- **Linux**: Would require `notify-send` (not implemented)
- **Windows**: Would require different implementation (not implemented)

## Troubleshooting

### Notifications Not Appearing

1. Check macOS System Preferences → Notifications → Script Editor → Allow Notifications
2. Ensure hooks are executable: `chmod +x .claude/hooks/*.js`
3. Check for errors in Claude Code console output

### Custom Sounds Not Working

Ensure the sound name matches exactly with macOS system sounds (case-sensitive).

## Resources

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)
- [macOS AppleScript Notification Guide](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/)

## Related Files

- `hooks.json` - Hook configuration
- `notification-hook.js` - General notification handler
- `stop-notification.js` - Stop event notification handler
