#!/usr/bin/env python3
"""
Content Extraction Tool
-----------------------
This script extracts specific sections from the original monolithic HTML file
and prepares them for insertion into the new modular architecture.

Usage:
    python3 extract_content.py <scenario> <section>

Examples:
    python3 extract_content.py shopping dialogue-present
    python3 extract_content.py shopping story-past
    python3 extract_content.py restaurant all
"""

import re
import sys
from pathlib import Path

def extract_section(html_content, scenario, modality, tense=None):
    """
    Extract a specific section from the HTML content.

    Args:
        html_content: The full HTML content
        scenario: e.g., 'shopping', 'restaurant', 'travel'
        modality: e.g., 'dialogue', 'story', 'phrases'
        tense: e.g., 'present', 'past', 'future', 'advanced' (optional)

    Returns:
        Extracted HTML content as string
    """

    if tense:
        # Extract tense-specific content
        pattern = rf'<div id="{scenario}-{modality}-{tense}".*?class="tense-content.*?">(.*?)(?=<div id="|</div>\s*</div>\s*<!-- Manga Section -->|</div>\s*<div id="{scenario}-{modality}-)'
        match = re.search(pattern, html_content, re.DOTALL)

        if match:
            return match.group(1).strip()
    else:
        # Extract entire modality section
        pattern = rf'<div id="{scenario}-{modality}".*?class="modality-content.*?">(.*?)(?=<div id="{scenario}-[a-z]+".*?class="modality-content|</div>\s*</div>\s*$)'
        match = re.search(pattern, html_content, re.DOTALL)

        if match:
            return match.group(1).strip()

    return None

def save_to_file(content, output_path):
    """Save extracted content to a file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Saved to: {output_path}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_content.py <scenario> <section>")
        print("\nExamples:")
        print("  python3 extract_content.py shopping dialogue-present")
        print("  python3 extract_content.py shopping story-all")
        print("  python3 extract_content.py restaurant phrases")
        sys.exit(1)

    scenario = sys.argv[1]
    section_spec = sys.argv[2]

    # Parse section specification
    if '-' in section_spec:
        modality, tense = section_spec.split('-', 1)
    else:
        modality = section_spec
        tense = None

    # Read original file
    original_file = Path('/sessions/practical-dazzling-fermi/mnt/japanese/travel_scenarios.html')
    if not original_file.exists():
        print(f"✗ Error: Original file not found: {original_file}")
        sys.exit(1)

    with open(original_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Create output directory
    output_dir = Path('/sessions/practical-dazzling-fermi/mnt/japanese/extracted')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract content
    if tense == 'all':
        # Extract all tenses for this modality
        tenses = ['present', 'past', 'future', 'advanced']
        for t in tenses:
            content = extract_section(html_content, scenario, modality, t)
            if content:
                output_path = output_dir / f"{scenario}-{modality}-{t}.html"
                save_to_file(content, output_path)
            else:
                print(f"✗ Could not extract: {scenario}-{modality}-{t}")
    else:
        # Extract single section
        content = extract_section(html_content, scenario, modality, tense)
        if content:
            filename = f"{scenario}-{modality}" + (f"-{tense}" if tense else "") + ".html"
            output_path = output_dir / filename
            save_to_file(content, output_path)

            # Print preview
            preview_length = 200
            preview = content[:preview_length].replace('\n', ' ')
            print(f"\nPreview: {preview}...")
            print(f"\nContent length: {len(content):,} characters")
        else:
            print(f"✗ Could not extract: {scenario}-{modality}" + (f"-{tense}" if tense else ""))
            print("\nTip: Check that the section exists in the original file")

if __name__ == '__main__':
    main()
