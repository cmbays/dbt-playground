# Scripts Folder

Python scripts used for building and maintaining the Japanese Learning App.

## Available Scripts

### extract_content.py
**Purpose:** Extract dialogue/story content from monolithic HTML files

**Usage:**
```bash
python3 extract_content.py <topic> <section>
```

**Examples:**
```bash
# Extract all shopping dialogues
python3 extract_content.py shopping dialogue-all

# Extract present tense story
python3 extract_content.py shopping story-present
```

**Output:** Creates files in `../extracted/` directory

---

### insert_shopping_dialogues.py
**Purpose:** Insert extracted dialogue content into shopping.html

**Usage:**
```bash
python3 insert_shopping_dialogues.py
```

**Note:** This was used during migration from single-page to multi-page architecture. May not be needed for new sections.

---

## When to Use These Scripts

- **During migration:** When converting old monolithic HTML files to new section-based architecture
- **Content extraction:** When you need to pull specific dialogues or stories from existing files
- **Batch operations:** When updating multiple sections at once

## Development Workflow

1. Create content in large files (easier to generate)
2. Use `extract_content.py` to split into sections
3. Manually place extracted content into section pages
4. Clean up and test

## Future Scripts

Consider creating:
- `validate_links.py` - Check all internal links work
- `generate_section.py` - Auto-generate section page template
- `count_kanji.py` - Analyze kanji coverage across all sections
