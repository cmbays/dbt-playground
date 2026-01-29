#!/usr/bin/env python3
"""
Extract kanji data from home-life HTML files
Creates a structured dataset for v0.2 kanji flashcard enhancement
"""

import re
import json
from pathlib import Path

# Files to process
FILES = [
    'topics/home-life/story-morning.html',
    'topics/home-life/story-evening.html',
    'topics/home-life/story-cooking.html',
    'topics/home-life/story-cleaning.html',
    'topics/home-life/phrases.html'
]

# Store unique kanji (key = character)
kanji_data = {}

def normalize_category(category_text):
    """Extract clean category name from header"""
    # Remove emojis and extra text, extract English part
    # Example: "⏰ Time & Morning (時間と朝)" -> "time-morning"
    # Extract text in parentheses if present, otherwise use whole thing
    match = re.search(r'\(([^\)]+)\)', category_text)
    if match:
        # Use Japanese part as it's more complete
        category = match.group(1)
    else:
        # Remove emojis
        category = re.sub(r'[^\w\s&]', '', category_text).strip()

    # Create a simple tag
    category = category.lower().replace(' & ', '-').replace(' ', '-')
    return category

def extract_kanji_from_file(filepath):
    """Extract all kanji from one HTML file"""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    current_category = "general"

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for category header
        if '<strong' in line and 'color:' in line:
            # Next line likely contains category text
            category_match = re.search(r'>([^<]+)</strong>', line)
            if category_match:
                category_text = category_match.group(1).strip()
                current_category = normalize_category(category_text)

        # Check for kanji card start
        if '<div class="kanji-card"' in line:
            # Next few lines contain character, reading, meaning
            character = None
            reading = None
            meaning = None

            # Look ahead for character
            for j in range(i, min(i+10, len(lines))):
                if '<div class="kanji-character">' in lines[j]:
                    char_match = re.search(r'<div class="kanji-character">([^<]+)</div>', lines[j])
                    if char_match:
                        character = char_match.group(1).strip()

                if '<div class="kanji-reading">' in lines[j]:
                    read_match = re.search(r'<div class="kanji-reading">([^<]+)</div>', lines[j])
                    if read_match:
                        reading = read_match.group(1).strip()

                if '<div class="kanji-meaning">' in lines[j]:
                    mean_match = re.search(r'<div class="kanji-meaning">Meaning:\s*([^<]+)</div>', lines[j])
                    if mean_match:
                        meaning = mean_match.group(1).strip()

                # Stop when we hit end of this card
                if '</div>' in lines[j] and j > i + 3:
                    break

            # Process this kanji if we found all parts
            if character and reading:
                # Parse readings
                on_readings = []
                kun_readings = []

                if 'On:' in reading:
                    on_match = re.search(r'On:\s*([^/]+)', reading)
                    if on_match:
                        on_text = on_match.group(1).strip()
                        on_readings = [r.strip() for r in on_text.split('、') if r.strip()]
                        # Also split by comma
                        if ',' in on_text:
                            on_readings = [r.strip() for r in on_text.split(',') if r.strip()]

                if 'Kun:' in reading:
                    kun_match = re.search(r'Kun:\s*(.+?)(?:\s*$)', reading)
                    if kun_match:
                        kun_text = kun_match.group(1).strip()
                        # Remove any trailing slashes
                        kun_text = kun_text.rstrip('/')
                        kun_readings = [r.strip() for r in kun_text.split('、') if r.strip()]
                        # Also split by comma
                        if ',' in kun_text:
                            kun_readings = [r.strip() for r in kun_text.split(',') if r.strip()]

                # If no On/Kun markers, assume it's all On-reading
                if not on_readings and not kun_readings:
                    on_readings = [reading]

                # Parse meanings
                meanings = []
                if meaning:
                    meanings = [m.strip() for m in meaning.split(',') if m.strip()]

                # Store or update
                if character not in kanji_data:
                    kanji_data[character] = {
                        'character': character,
                        'readings': {
                            'on': on_readings,
                            'kun': kun_readings
                        },
                        'meanings': meanings,
                        'categories': [current_category],
                        'source_files': [filepath]
                    }
                else:
                    # Merge data
                    existing = kanji_data[character]

                    if current_category not in existing['categories']:
                        existing['categories'].append(current_category)

                    if filepath not in existing['source_files']:
                        existing['source_files'].append(filepath)

                    # Keep the most complete readings
                    if len(on_readings) > len(existing['readings']['on']):
                        existing['readings']['on'] = on_readings
                    if len(kun_readings) > len(existing['readings']['kun']):
                        existing['readings']['kun'] = kun_readings

                    # Merge meanings
                    for m in meanings:
                        if m not in existing['meanings']:
                            existing['meanings'].append(m)

        i += 1

def main():
    print("Extracting kanji from home-life HTML files...\n")

    for filepath in FILES:
        print(f"Processing: {filepath}")
        try:
            extract_kanji_from_file(filepath)
            print(f"   ✓ Complete")
        except Exception as e:
            print(f"   ✗ Error: {e}")

    print(f"\n✅ Extraction complete!")
    print(f"Total unique kanji found: {len(kanji_data)}")

    # Sort by character
    sorted_kanji = dict(sorted(kanji_data.items()))

    # Save to JSON
    output_file = 'temp/extracted_kanji_raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_kanji, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Saved to: {output_file}")

    # Print summary
    print("\n📊 Summary:")
    print(f"   Total kanji: {len(kanji_data)}")

    # Count kanji by category
    category_counts = {}
    for kanji in kanji_data.values():
        for cat in kanji['categories']:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    print("\n   Kanji by category:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"      {cat}: {count}")

    # Print first 10 kanji as sample
    print("\n   Sample (first 10 kanji):")
    for i, (char, data) in enumerate(list(sorted_kanji.items())[:10]):
        on = ', '.join(data['readings']['on']) if data['readings']['on'] else '-'
        kun = ', '.join(data['readings']['kun']) if data['readings']['kun'] else '-'
        meanings = ', '.join(data['meanings'][:2])  # First 2 meanings
        print(f"      {char}: On: {on} / Kun: {kun} | {meanings}")

    print("\n✨ Next step: Review extracted_kanji_raw.json and proceed to JLPT level research")

if __name__ == '__main__':
    main()
