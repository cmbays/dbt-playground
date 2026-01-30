# RSS Digest Command

Generate and manage AI/Claude/Agents RSS digest for curated learning.

## Usage

```
/rss                    # Generate digest (14 days, open in browser)
/rss --days 7           # Last 7 days only
/rss --no-open          # Generate without opening browser
/rss config             # Edit feed configuration
/rss add <url>          # Add a new feed
/rss remove <name>      # Remove a feed
/rss list               # List all configured feeds
/rss schedule           # Manage daily schedule
```

## Commands

| Command | Description |
|---------|-------------|
| (default) | Generate digest and open in browser |
| `config` | Open feed configuration for editing |
| `add` | Add a new RSS feed |
| `remove` | Remove a feed by name |
| `list` | Show all configured feeds with status |
| `schedule` | View/modify daily schedule |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--days N` | Include articles from last N days | 14 |
| `--open` | Open in browser after generating | Yes |
| `--no-open` | Skip opening browser | - |
| `--output PATH` | Custom output path | `temp/rss_digest.html` |

## Examples

### Generate Default Digest

```
/rss
```

Executes:

```bash
uv run scripts/rss_digest.py --days 14 --open
```

### Quick Weekly Review

```
/rss --days 7
```

Last 7 days for focused reading.

### Generate for Later

```
/rss --no-open
```

Creates digest without opening browser.

### Add New Feed

```
/rss add https://example.com/feed.xml "Example Blog"
```

Adds feed to the configuration.

### List All Feeds

```
/rss list
```

Shows all feeds with last fetch status:

```
Anthropic Feeds (4)
  ✓ Anthropic News          - 3 articles (7d)
  ✓ Anthropic Engineering   - 1 article (7d)
  ✓ Anthropic Research      - 0 articles (7d)
  ✓ Claude Code Changelog   - 2 articles (7d)

Newsletters (6)
  ✓ Simon Willison          - 12 articles (7d)
  ✓ Latent Space            - 2 articles (7d)
  ✗ Import AI               - Failed (timeout)
  ...
```

### Manage Schedule

```
/rss schedule
```

Shows current schedule and options:

```
Current Schedule: Daily at 7:00 AM

Options:
1. Change time
2. Disable schedule
3. Run now
4. View logs
```

## Output Files

| File | Description |
|------|-------------|
| `temp/rss_digest.html` | Interactive HTML digest |
| `temp/rss_digest.json` | Raw data for scripting |
| `temp/rss_digest.log` | Scheduled run logs |

## Feed Categories

The digest automatically categorizes articles:

| Category | Keywords |
|----------|----------|
| Claude/Anthropic | claude, anthropic, constitutional ai |
| Agents & Orchestration | agent, orchestration, tool use, agentic |
| Skills & Capabilities | skill, capability, benchmark, reasoning |
| Development & Building | api, sdk, integration, tutorial |
| Research & Papers | paper, research, arxiv, study |
| Industry & News | release, announcement, launch |

## Interactive Features

The HTML digest supports:

- **Filter by category** - Click category buttons
- **Filter by source** - Click source tags
- **Search** - Full-text search across titles and summaries
- **Dark mode** - Comfortable reading

## Feed Configuration

Edit `scripts/rss_digest.py` to modify the `FEEDS` dictionary:

```python
FEEDS = {
    # Format: "Display Name": "feed_url"
    "Anthropic News": "https://...",
    "Simon Willison": "https://simonwillison.net/atom/everything/",
}
```

### Adding Custom Feeds

```
/rss config
```

Opens the script for editing. Add your feeds to the `FEEDS` dict.

### Feed Sources

| Type | How to Find RSS |
|------|-----------------|
| Substack | `https://name.substack.com/feed` |
| GitHub Releases | `https://github.com/org/repo/releases.atom` |
| YouTube | `https://www.youtube.com/feeds/videos.xml?channel_id=ID` |
| Blogs | Look for RSS icon or `/feed`, `/rss`, `/atom` |

## Scheduled Execution

The digest runs daily via launchd:

```
~/Library/LaunchAgents/com.dbt-playground.rss-digest.plist
```

### Schedule Commands

```bash
# Check status
launchctl list | grep rss-digest

# Run now
launchctl start com.dbt-playground.rss-digest

# Disable
launchctl unload ~/Library/LaunchAgents/com.dbt-playground.rss-digest.plist

# Re-enable
launchctl load ~/Library/LaunchAgents/com.dbt-playground.rss-digest.plist
```

## Workflow Integration

Suggested daily workflow:

1. **Morning**: Open `temp/rss_digest.html` (auto-generated at 7 AM)
2. **Scan**: Use category filters to focus on interests
3. **Bookmark**: Save important articles for deep reading
4. **Weekly**: Use `/rss --days 7` for focused weekly review

## Troubleshooting

### Feed Not Loading

```
/rss list
```

Check for failed feeds. Common issues:
- URL changed (find new RSS URL)
- Site blocks automated requests (try different User-Agent)
- Feed discontinued

### Empty Results

```
/rss --days 30
```

Expand date range if feeds are low-volume.

### Schedule Not Running

```bash
# Check if loaded
launchctl list | grep rss-digest

# View logs
cat temp/rss_digest.log

# Reload
launchctl unload ~/Library/LaunchAgents/com.dbt-playground.rss-digest.plist
launchctl load ~/Library/LaunchAgents/com.dbt-playground.rss-digest.plist
```

## Related

- `scripts/rss_digest.py` - Main script
- `scripts/com.dbt-playground.rss-digest.plist` - Schedule config
- `temp/rss_digest.html` - Generated digest
- [Olshansk/rss-feeds](https://github.com/Olshansk/rss-feeds) - Community feeds for sites without RSS
