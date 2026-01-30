#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["feedparser", "httpx", "rich", "jinja2"]
# ///
"""
RSS Digest Aggregator for AI/Claude/Agents content.

Fetches RSS feeds from key contributors and generates an interactive HTML digest.

Usage:
    uv run scripts/rss_digest.py              # Generate digest
    uv run scripts/rss_digest.py --days 7     # Last 7 days only
    uv run scripts/rss_digest.py --open       # Open in browser after generating
"""

import argparse
import json
import re
import subprocess
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import feedparser
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

# RSS Feed Configuration - Key AI/Claude/Agents Contributors
FEEDS = {
    # Anthropic (via community-maintained feeds - https://github.com/Olshansk/rss-feeds)
    "Anthropic News": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
    "Anthropic Engineering": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
    "Anthropic Research": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
    "Claude Code Changelog": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_changelog_claude_code.xml",

    # Other AI Companies (via community feeds)
    "OpenAI Research": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_openai_research.xml",
    "Cursor Blog": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_cursor.xml",

    # Company Blogs (with working feeds)
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "LangChain": "https://blog.langchain.dev/rss/",
    "Google AI": "https://blog.google/technology/ai/rss/",

    # Individual Contributors & Researchers
    "Simon Willison": "https://simonwillison.net/atom/everything/",
    "Lilian Weng": "https://lilianweng.github.io/index.xml",
    "Jay Alammar": "https://jalammar.github.io/feed.xml",
    "Chip Huyen": "https://huyenchip.com/feed.xml",
    "Eugene Yan": "https://eugeneyan.com/rss/",

    # Newsletters & Podcasts (Substack)
    "Latent Space": "https://www.latent.space/feed",
    "AI Snake Oil": "https://www.aisnakeoil.com/feed",
    "One Useful Thing (Ethan Mollick)": "https://www.oneusefulthing.org/feed",
    "Interconnects (Nathan Lambert)": "https://www.interconnects.ai/feed",
    "The Algorithmic Bridge": "https://thealgorithmicbridge.substack.com/feed",
    "The Gradient": "https://thegradient.pub/rss/",
    "Import AI (Jack Clark)": "https://importai.substack.com/feed",
    "Ahead of AI (Sebastian Raschka)": "https://magazine.sebastianraschka.com/feed",

    # Technical Blogs
    "Weights & Biases": "https://wandb.ai/fully-connected/rss.xml",
    "Cohere": "https://cohere.com/blog/rss.xml",

    # GitHub Releases (via atom feeds)
    "LangChain Releases": "https://github.com/langchain-ai/langchain/releases.atom",
    "Anthropic SDK Releases": "https://github.com/anthropics/anthropic-sdk-python/releases.atom",
}

# Topic keywords for categorization
TOPICS = {
    "Claude/Anthropic": ["claude", "anthropic", "constitutional ai", "claude code"],
    "Agents & Orchestration": ["agent", "orchestration", "tool use", "function calling", "agentic", "multi-agent", "swarm"],
    "Skills & Capabilities": ["skill", "capability", "benchmark", "evaluation", "reasoning"],
    "Development & Building": ["api", "sdk", "integration", "tutorial", "guide", "building", "developer"],
    "Research & Papers": ["paper", "research", "arxiv", "study", "findings"],
    "Industry & News": ["release", "announcement", "launch", "update", "news"],
}


def fetch_feed(name: str, url: str, timeout: float = 10.0) -> list[dict[str, Any]]:
    """Fetch and parse a single RSS feed."""
    try:
        # Use httpx for better timeout handling
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url, headers={"User-Agent": "RSS-Digest/1.0"})
            response.raise_for_status()

        feed = feedparser.parse(response.text)
        entries = []

        for entry in feed.entries[:20]:  # Limit per feed
            # Parse date
            published = None
            for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
                if hasattr(entry, date_field) and getattr(entry, date_field):
                    try:
                        published = datetime(*getattr(entry, date_field)[:6], tzinfo=timezone.utc)
                        break
                    except (TypeError, ValueError):
                        continue

            if not published:
                published = datetime.now(timezone.utc)

            # Extract summary
            summary = ""
            if hasattr(entry, 'summary'):
                summary = entry.summary[:500] + "..." if len(entry.summary) > 500 else entry.summary
            elif hasattr(entry, 'description'):
                summary = entry.description[:500] + "..." if len(entry.description) > 500 else entry.description

            entries.append({
                "source": name,
                "title": entry.get('title', 'No title'),
                "link": entry.get('link', ''),
                "published": published.isoformat(),
                "published_dt": published,
                "summary": summary,
            })

        return entries
    except httpx.RequestError as e:
        console.print(f"[yellow]Warning: Network error fetching {name}: {e}[/yellow]")
        return []
    except httpx.HTTPStatusError as e:
        console.print(f"[yellow]Warning: HTTP {e.response.status_code} fetching {name}[/yellow]")
        return []
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to parse {name}: {type(e).__name__}: {e}[/yellow]")
        return []


def categorize_entry(entry: dict[str, Any]) -> list[str]:
    """Categorize an entry based on keywords in title and summary."""
    text = f"{entry['title']} {entry['summary']}".lower()
    categories = []

    for category, keywords in TOPICS.items():
        if any(kw in text for kw in keywords):
            categories.append(category)

    return categories if categories else ["General AI"]


def fetch_all_feeds(days: int = 14) -> list[dict[str, Any]]:
    """Fetch all configured RSS feeds."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    all_entries = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching feeds...", total=len(FEEDS))

        for name, url in FEEDS.items():
            progress.update(task, description=f"Fetching {name}...")
            entries = fetch_feed(name, url)

            # Filter by date and add categories
            for entry in entries:
                if entry['published_dt'] >= cutoff:
                    entry['categories'] = categorize_entry(entry)
                    all_entries.append(entry)

            progress.advance(task)

    # Sort by date, newest first
    all_entries.sort(key=lambda x: x['published_dt'], reverse=True)

    # Remove datetime object (not JSON serializable)
    for entry in all_entries:
        del entry['published_dt']

    return all_entries


def generate_html(entries: list[dict[str, Any]], output_path: Path) -> None:
    """Generate interactive HTML digest."""

    # Group by category for stats
    category_counts = {}
    source_counts = {}
    for entry in entries:
        for cat in entry['categories']:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        source_counts[entry['source']] = source_counts.get(entry['source'], 0) + 1

    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI/Claude RSS Digest</title>
    <style>
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --accent-hover: #79b8ff;
            --border: #30363d;
            --green: #3fb950;
            --orange: #d29922;
            --purple: #a371f7;
            --pink: #db61a2;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }

        .container { max-width: 1200px; margin: 0 auto; }

        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }

        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: var(--text-secondary); font-size: 1.1em; }
        .generated { color: var(--text-secondary); font-size: 0.9em; margin-top: 10px; }

        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }

        .stat {
            background: var(--bg-secondary);
            padding: 15px 25px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-number { font-size: 2em; font-weight: bold; color: var(--accent); }
        .stat-label { color: var(--text-secondary); font-size: 0.9em; }

        .filters {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .filter-btn {
            padding: 8px 16px;
            border: 1px solid var(--border);
            background: var(--bg-secondary);
            color: var(--text-primary);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9em;
        }

        .filter-btn:hover { border-color: var(--accent); }
        .filter-btn.active { background: var(--accent); color: var(--bg-primary); border-color: var(--accent); }

        .search-box {
            width: 100%;
            max-width: 500px;
            padding: 12px 20px;
            border: 1px solid var(--border);
            background: var(--bg-secondary);
            color: var(--text-primary);
            border-radius: 8px;
            font-size: 1em;
            margin: 20px auto;
            display: block;
        }

        .search-box:focus { outline: none; border-color: var(--accent); }

        .entries { display: grid; gap: 15px; }

        .entry {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s;
        }

        .entry:hover { border-color: var(--accent); transform: translateY(-2px); }

        .entry-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 15px; margin-bottom: 10px; }

        .entry-title {
            font-size: 1.2em;
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
        }

        .entry-title:hover { color: var(--accent-hover); text-decoration: underline; }

        .entry-meta {
            display: flex;
            gap: 15px;
            color: var(--text-secondary);
            font-size: 0.85em;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }

        .entry-source { color: var(--green); font-weight: 500; }

        .entry-summary {
            color: var(--text-secondary);
            font-size: 0.95em;
            line-height: 1.7;
        }

        .entry-categories { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }

        .category-tag {
            padding: 4px 10px;
            background: var(--bg-tertiary);
            border-radius: 12px;
            font-size: 0.8em;
            color: var(--text-secondary);
        }

        .category-tag.claude { background: #3b2e58; color: var(--purple); }
        .category-tag.agents { background: #2e4058; color: var(--accent); }
        .category-tag.skills { background: #3b4a2e; color: var(--green); }
        .category-tag.development { background: #4a3b2e; color: var(--orange); }
        .category-tag.research { background: #4a2e3b; color: var(--pink); }

        .no-results {
            text-align: center;
            padding: 50px;
            color: var(--text-secondary);
        }

        .source-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
            margin-top: 20px;
            padding: 20px;
            background: var(--bg-secondary);
            border-radius: 8px;
        }

        .source-tag {
            padding: 4px 12px;
            background: var(--bg-tertiary);
            border-radius: 12px;
            font-size: 0.85em;
            cursor: pointer;
            transition: all 0.2s;
        }

        .source-tag:hover { background: var(--accent); color: var(--bg-primary); }

        footer {
            text-align: center;
            padding: 30px;
            color: var(--text-secondary);
            font-size: 0.9em;
            border-top: 1px solid var(--border);
            margin-top: 30px;
        }

        @media (max-width: 600px) {
            .entry-header { flex-direction: column; }
            .stats { gap: 15px; }
            .stat { padding: 10px 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI/Claude RSS Digest</h1>
            <p class="subtitle">Curated content on Claude, Anthropic, Agents & AI Development</p>
            <p class="generated">Generated: GENERATED_TIME</p>

            <div class="stats">
                <div class="stat">
                    <div class="stat-number">TOTAL_ENTRIES</div>
                    <div class="stat-label">Articles</div>
                </div>
                <div class="stat">
                    <div class="stat-number">TOTAL_SOURCES</div>
                    <div class="stat-label">Sources</div>
                </div>
                <div class="stat">
                    <div class="stat-number">DAYS_RANGE</div>
                    <div class="stat-label">Days</div>
                </div>
            </div>
        </header>

        <input type="text" class="search-box" placeholder="Search articles..." id="searchBox">

        <div class="filters" id="categoryFilters">
            <button class="filter-btn active" data-filter="all">All</button>
            CATEGORY_BUTTONS
        </div>

        <div class="source-list" id="sourceFilters">
            SOURCE_TAGS
        </div>

        <div class="entries" id="entriesContainer">
            ENTRIES_HTML
        </div>

        <div class="no-results" id="noResults" style="display: none;">
            No articles match your filters.
        </div>

        <footer>
            <p>Data from RSS feeds • Refresh by running: <code>uv run scripts/rss_digest.py --open</code></p>
        </footer>
    </div>

    <script>
        const entries = ENTRIES_JSON;
        let activeCategory = 'all';
        let activeSource = null;
        let searchQuery = '';

        // Escape HTML to prevent XSS from malicious feed content
        function escapeHtml(str) {
            if (!str) return '';
            return str.replace(/[&<>"']/g, c => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            })[c]);
        }

        // Sanitize URL to prevent javascript: protocol injection
        function sanitizeUrl(url) {
            if (!url) return '#';
            try {
                const parsed = new URL(url);
                if (!['http:', 'https:'].includes(parsed.protocol)) {
                    return '#';
                }
                return url;
            } catch {
                return '#';
            }
        }

        // Strip HTML tags from summary text
        function stripHtml(str) {
            if (!str) return '';
            return str.replace(/<[^>]*>/g, '');
        }

        function getCategoryClass(cat) {
            if (cat.includes('Claude')) return 'claude';
            if (cat.includes('Agent')) return 'agents';
            if (cat.includes('Skill')) return 'skills';
            if (cat.includes('Development')) return 'development';
            if (cat.includes('Research')) return 'research';
            return '';
        }

        function renderEntries() {
            const container = document.getElementById('entriesContainer');
            const noResults = document.getElementById('noResults');

            const filtered = entries.filter(entry => {
                const matchesCategory = activeCategory === 'all' || entry.categories.includes(activeCategory);
                const matchesSource = !activeSource || entry.source === activeSource;
                const matchesSearch = !searchQuery ||
                    entry.title.toLowerCase().includes(searchQuery) ||
                    entry.summary.toLowerCase().includes(searchQuery) ||
                    entry.source.toLowerCase().includes(searchQuery);
                return matchesCategory && matchesSource && matchesSearch;
            });

            if (filtered.length === 0) {
                container.style.display = 'none';
                noResults.style.display = 'block';
                return;
            }

            container.style.display = 'grid';
            noResults.style.display = 'none';

            container.innerHTML = filtered.map(entry => `
                <div class="entry">
                    <div class="entry-header">
                        <a href="${sanitizeUrl(entry.link)}" target="_blank" rel="noopener noreferrer" class="entry-title">${escapeHtml(entry.title)}</a>
                    </div>
                    <div class="entry-meta">
                        <span class="entry-source">${escapeHtml(entry.source)}</span>
                        <span>${new Date(entry.published).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                    </div>
                    <p class="entry-summary">${escapeHtml(stripHtml(entry.summary))}</p>
                    <div class="entry-categories">
                        ${entry.categories.map(cat => `<span class="category-tag ${getCategoryClass(cat)}">${escapeHtml(cat)}</span>`).join('')}
                    </div>
                </div>
            `).join('');
        }

        // Category filter handlers
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeCategory = btn.dataset.filter;
                renderEntries();
            });
        });

        // Source filter handlers
        document.querySelectorAll('.source-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                if (activeSource === tag.dataset.source) {
                    activeSource = null;
                    tag.style.background = '';
                    tag.style.color = '';
                } else {
                    document.querySelectorAll('.source-tag').forEach(t => {
                        t.style.background = '';
                        t.style.color = '';
                    });
                    activeSource = tag.dataset.source;
                    tag.style.background = 'var(--accent)';
                    tag.style.color = 'var(--bg-primary)';
                }
                renderEntries();
            });
        });

        // Search handler
        document.getElementById('searchBox').addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase();
            renderEntries();
        });

        // Initial render
        renderEntries();
    </script>
</body>
</html>'''

    # Generate category buttons
    category_buttons = '\n'.join([
        f'<button class="filter-btn" data-filter="{cat}">{cat} ({count})</button>'
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1])
    ])

    # Generate source tags
    source_tags = '\n'.join([
        f'<span class="source-tag" data-source="{source}">{source} ({count})</span>'
        for source, count in sorted(source_counts.items(), key=lambda x: -x[1])
    ])

    # Generate entries HTML (for initial render / no-JS fallback)
    entries_html = ""  # JS will render

    # Calculate days range
    if entries:
        dates = [datetime.fromisoformat(e['published']) for e in entries]
        days_range = (max(dates) - min(dates)).days + 1
    else:
        days_range = 0

    # Fill template
    html = html_template.replace('GENERATED_TIME', datetime.now().strftime('%B %d, %Y at %H:%M'))
    html = html.replace('TOTAL_ENTRIES', str(len(entries)))
    html = html.replace('TOTAL_SOURCES', str(len(source_counts)))
    html = html.replace('DAYS_RANGE', str(days_range))
    html = html.replace('CATEGORY_BUTTONS', category_buttons)
    html = html.replace('SOURCE_TAGS', source_tags)
    html = html.replace('ENTRIES_HTML', entries_html)
    html = html.replace('ENTRIES_JSON', json.dumps(entries, indent=2))

    output_path.write_text(html)
    console.print(f"[green]✓ Generated digest: {output_path}[/green]")


def cmd_generate(args):
    """Generate the RSS digest."""
    console.print("[bold]🤖 AI/Claude RSS Digest Generator[/bold]\n")

    # Fetch feeds
    console.print(f"Fetching content from last {args.days} days...")
    entries = fetch_all_feeds(days=args.days)

    console.print(f"\n[green]Found {len(entries)} articles from {len(set(e['source'] for e in entries))} sources[/green]\n")

    # Generate HTML
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_html(entries, output_path)

    # Save JSON for programmatic access
    json_path = output_path.with_suffix('.json')
    json_path.write_text(json.dumps(entries, indent=2))
    console.print(f"[green]✓ Saved JSON data: {json_path}[/green]")

    if not args.no_open:
        webbrowser.open(f"file://{output_path.absolute()}")
        console.print("[blue]Opened in browser[/blue]")


def cmd_list(args):
    """List all configured feeds with status."""
    console.print("[bold]📋 Configured RSS Feeds[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Feed Name", style="green")
    table.add_column("URL", style="dim", max_width=60)
    table.add_column("Status", justify="center")

    for name, url in FEEDS.items():
        # Quick check if feed is reachable
        try:
            with httpx.Client(timeout=5.0, follow_redirects=True) as client:
                response = client.head(url, headers={"User-Agent": "RSS-Digest/1.0"})
                status = "[green]✓[/green]" if response.status_code == 200 else f"[yellow]{response.status_code}[/yellow]"
        except httpx.RequestError as e:
            console.print(f"[dim]  {name}: {type(e).__name__}[/dim]")
            status = "[red]✗[/red]"
        except Exception as e:
            console.print(f"[dim]  {name}: {type(e).__name__}: {e}[/dim]")
            status = "[red]✗[/red]"

        table.add_row(name, url[:60] + "..." if len(url) > 60 else url, status)

    console.print(table)
    console.print(f"\n[dim]Total: {len(FEEDS)} feeds[/dim]")


def cmd_config(args):
    """Open the script for editing."""
    script_path = Path(__file__).resolve()
    console.print(f"[bold]Opening {script_path} for editing...[/bold]")
    console.print("\n[dim]Edit the FEEDS dictionary to add/remove feeds.[/dim]\n")

    # Try common editors
    editors = ["code", "cursor", "vim", "nano"]
    for editor in editors:
        try:
            subprocess.run([editor, str(script_path)], check=True)
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    console.print(f"[yellow]Could not open editor. Edit manually: {script_path}[/yellow]")


def cmd_schedule(args):
    """Show and manage schedule status."""
    console.print("[bold]⏰ RSS Digest Schedule[/bold]\n")

    # Check launchctl status
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True,
            text=True
        )
        if "com.dbt-playground.rss-digest" in result.stdout:
            console.print("[green]✓ Schedule is active[/green]")

            # Parse plist for schedule time
            plist_path = Path(__file__).parent / "com.dbt-playground.rss-digest.plist"
            if plist_path.exists():
                content = plist_path.read_text()
                # Simple extraction
                if "<key>Hour</key>" in content:
                    hour_match = re.search(r"<key>Hour</key>\s*<integer>(\d+)</integer>", content)
                    minute_match = re.search(r"<key>Minute</key>\s*<integer>(\d+)</integer>", content)
                    if hour_match and minute_match:
                        console.print(f"[cyan]Time: {hour_match.group(1)}:{minute_match.group(1):0>2} daily[/cyan]")
        else:
            console.print("[yellow]Schedule is not loaded[/yellow]")
            console.print("\n[dim]To enable:[/dim]")
            console.print("  launchctl load ~/Library/LaunchAgents/com.dbt-playground.rss-digest.plist")
    except subprocess.SubprocessError as e:
        console.print(f"[red]Could not check schedule: {type(e).__name__}: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Could not check schedule: {type(e).__name__}: {e}[/red]")

    console.print("\n[bold]Commands:[/bold]")
    console.print("  [cyan]Run now:[/cyan]     launchctl start com.dbt-playground.rss-digest")
    console.print("  [cyan]Disable:[/cyan]     launchctl unload ~/Library/LaunchAgents/com.dbt-playground.rss-digest.plist")
    console.print("  [cyan]Re-enable:[/cyan]   launchctl load ~/Library/LaunchAgents/com.dbt-playground.rss-digest.plist")
    console.print("  [cyan]View logs:[/cyan]   cat temp/rss_digest.log")


def cmd_add(args):
    """Add a new feed (prints instructions)."""
    console.print("[bold]➕ Add New Feed[/bold]\n")
    console.print("To add a feed, edit the FEEDS dictionary in the script:\n")
    console.print(f"  [cyan]uv run {Path(__file__).name} config[/cyan]\n")
    console.print("Then add your feed in this format:")
    console.print('  [green]"Feed Name": "https://example.com/feed.xml",[/green]\n')
    console.print("[bold]Common feed URL patterns:[/bold]")
    console.print("  Substack:  https://name.substack.com/feed")
    console.print("  GitHub:    https://github.com/org/repo/releases.atom")
    console.print("  YouTube:   https://www.youtube.com/feeds/videos.xml?channel_id=ID")
    console.print("  WordPress: https://site.com/feed/")


def main():
    parser = argparse.ArgumentParser(
        description="AI/Claude RSS Digest Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run scripts/rss_digest.py              # Generate digest (14 days, opens browser)
  uv run scripts/rss_digest.py --days 7     # Last 7 days
  uv run scripts/rss_digest.py --no-open    # Generate without opening
  uv run scripts/rss_digest.py list         # Show all feeds
  uv run scripts/rss_digest.py config       # Edit feed configuration
  uv run scripts/rss_digest.py schedule     # View/manage schedule
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate (default)
    gen_parser = subparsers.add_parser("generate", help="Generate digest (default)")
    gen_parser.add_argument("--days", type=int, default=14, help="Days to include (default: 14)")
    gen_parser.add_argument("--no-open", action="store_true", help="Don't open browser")
    gen_parser.add_argument("--output", type=str, default="temp/rss_digest.html", help="Output path")

    # List feeds
    subparsers.add_parser("list", help="List all configured feeds")

    # Config
    subparsers.add_parser("config", help="Edit feed configuration")

    # Schedule
    subparsers.add_parser("schedule", help="View/manage daily schedule")

    # Add feed
    subparsers.add_parser("add", help="Add a new feed (shows instructions)")

    # Also support flags at top level for default generate behavior
    parser.add_argument("--days", type=int, default=14, help="Days to include (default: 14)")
    parser.add_argument("--no-open", action="store_true", help="Don't open browser")
    parser.add_argument("--output", type=str, default="temp/rss_digest.html", help="Output path")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "schedule":
        cmd_schedule(args)
    elif args.command == "add":
        cmd_add(args)
    else:
        # Default: generate
        cmd_generate(args)


if __name__ == "__main__":
    main()
