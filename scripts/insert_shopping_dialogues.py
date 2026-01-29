#!/usr/bin/env python3
"""
Insert all shopping dialogue sections into shopping.html
"""
import re

print("Inserting shopping dialogues...")
print("=" * 60)

# Read the shopping.html file
with open('/sessions/practical-dazzling-fermi/mnt/japanese/shopping.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Read all extracted dialogue files
dialogues = {}
for tense in ['present', 'past', 'future', 'advanced']:
    file_path = f'/sessions/practical-dazzling-fermi/mnt/japanese/extracted/shopping-dialogue-{tense}.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        dialogues[tense] = f.read().strip()
    print(f"✓ Read {tense} dialogue ({len(dialogues[tense]):,} characters)")

# Replace present dialogue
present_pattern = r'<div id="shopping-dialogue-present" class="tense-content active">.*?</div>\s*<div id="shopping-dialogue-past"'
present_replacement = f'''<div id="shopping-dialogue-present" class="tense-content active">
                    {dialogues['present']}
                </div>

                <div id="shopping-dialogue-past"'''
html = re.sub(present_pattern, present_replacement, html, flags=re.DOTALL)
print("✓ Inserted present dialogue")

# Replace past dialogue
past_pattern = r'<div id="shopping-dialogue-past" class="tense-content">.*?</div>\s*<div id="shopping-dialogue-future"'
past_replacement = f'''<div id="shopping-dialogue-past" class="tense-content">
                    {dialogues['past']}
                </div>

                <div id="shopping-dialogue-future"'''
html = re.sub(past_pattern, past_replacement, html, flags=re.DOTALL)
print("✓ Inserted past dialogue")

# Replace future dialogue
future_pattern = r'<div id="shopping-dialogue-future" class="tense-content">.*?</div>\s*<div id="shopping-dialogue-advanced"'
future_replacement = f'''<div id="shopping-dialogue-future" class="tense-content">
                    {dialogues['future']}
                </div>

                <div id="shopping-dialogue-advanced"'''
html = re.sub(future_pattern, future_replacement, html, flags=re.DOTALL)
print("✓ Inserted future dialogue")

# Replace advanced dialogue
advanced_pattern = r'<div id="shopping-dialogue-advanced" class="tense-content">.*?</div>\s*</div>\s*<!-- Story Section -->'
advanced_replacement = f'''<div id="shopping-dialogue-advanced" class="tense-content">
                    {dialogues['advanced']}
                </div>
                </div>

                <!-- Story Section -->'''
html = re.sub(advanced_pattern, advanced_replacement, html, flags=re.DOTALL)
print("✓ Inserted advanced dialogue")

# Write back to file
with open('/sessions/practical-dazzling-fermi/mnt/japanese/shopping.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✓ All dialogues inserted! File size: {len(html):,} characters")
print("\nDialogues added:")
print("  ✓ Present: Supermarket vegetable shopping (with grammar & kanji)")
print("  ✓ Past: 100 yen shop experience (with grammar & kanji)")
print("  ✓ Future: Electronics store laptop shopping (with grammar & kanji)")
print("  ✓ Advanced: Clothing store with polite keigo (with grammar & kanji)")
print("\nEach dialogue includes:")
print("  • Grammar tips")
print("  • Interactive audio buttons")
print("  • Hint buttons for translations")
print("  • Kanji flashcards with relevant vocabulary")
