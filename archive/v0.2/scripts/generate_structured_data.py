#!/usr/bin/env python3
"""
Task 1.5: Create Structured Data File
Convert JSON kanji data to JavaScript format with proper structure and comments
"""

import json
from datetime import datetime

def generate_js_data_file():
    """Generate the final JavaScript data file from JSON"""

    # Load the complete kanji data
    with open('temp/kanji_with_jlpt_complete.json', 'r', encoding='utf-8') as f:
        kanji_data = json.load(f)

    # Sort kanji by JLPT level (N5 -> N2) then alphabetically
    jlpt_order = {'N5': 0, 'N4': 1, 'N3': 2, 'N2': 3}
    sorted_kanji = sorted(
        kanji_data.items(),
        key=lambda x: (jlpt_order.get(x[1].get('jlpt', 'N5'), 99), x[0])
    )

    # Start building the JavaScript file
    js_content = []
    js_content.append('/**')
    js_content.append(' * Home Life Kanji Data')
    js_content.append(' * Complete metadata for all kanji from home-life topic pages')
    js_content.append(' * ')
    js_content.append(f' * Generated: {datetime.now().strftime("%Y-%m-%d")}')
    js_content.append(f' * Total Kanji: {len(kanji_data)}')
    js_content.append(' * JLPT Levels: N5, N4, N3, N2')
    js_content.append(' * ')
    js_content.append(' * Each kanji entry includes:')
    js_content.append(' * - character: The kanji character')
    js_content.append(' * - readings: On-yomi and kun-yomi readings')
    js_content.append(' * - meanings: English meanings')
    js_content.append(' * - jlpt: JLPT level (N5-N2)')
    js_content.append(' * - topics: Related topics (currently all "home-life")')
    js_content.append(' * - categories: Semantic categories from source files')
    js_content.append(' * - words: 3 example vocabulary words with readings and JLPT levels')
    js_content.append(' * - sentence: 1 example sentence in 4 formats (japanese, hiragana, romaji, english)')
    js_content.append(' */')
    js_content.append('')
    js_content.append('const homeLifeKanji = [')

    # Process each kanji
    for i, (char, data) in enumerate(sorted_kanji):
        is_last = (i == len(sorted_kanji) - 1)

        js_content.append('  {')
        js_content.append(f'    character: "{char}",')

        # Readings
        on_readings = '", "'.join(data['readings'].get('on', []))
        kun_readings = '", "'.join(data['readings'].get('kun', []))
        js_content.append(f'    readings: {{ on: ["{on_readings}"], kun: ["{kun_readings}"] }},')

        # Meanings
        meanings = '", "'.join(data['meanings'])
        js_content.append(f'    meanings: ["{meanings}"],')

        # JLPT level
        js_content.append(f'    jlpt: "{data.get("jlpt", "N5")}",')

        # Topics (all home-life for now)
        js_content.append(f'    topics: ["home-life"],')

        # Categories
        categories = '", "'.join(data.get('categories', []))
        js_content.append(f'    categories: ["{categories}"],')

        # Words
        if 'words' in data and data['words']:
            js_content.append('    words: [')
            for j, word in enumerate(data['words']):
                is_last_word = (j == len(data['words']) - 1)
                comma = '' if is_last_word else ','
                js_content.append(f'      {{ japanese: "{word["japanese"]}", hiragana: "{word["hiragana"]}", english: "{word["english"]}", jlpt: "{word["jlpt"]}" }}{comma}')
            js_content.append('    ],')
        else:
            js_content.append('    words: [],')

        # Sentence
        if 'sentence' in data and data['sentence']:
            sent = data['sentence']
            js_content.append('    sentence: {')
            js_content.append(f'      japanese: "{sent["japanese"]}",')
            js_content.append(f'      hiragana: "{sent["hiragana"]}",')
            js_content.append(f'      romaji: "{sent["romaji"]}",')
            js_content.append(f'      english: "{sent["english"]}"')
            js_content.append('    }')
        else:
            js_content.append('    sentence: null')

        # Close this kanji entry
        closing = '  }' if is_last else '  },'
        js_content.append(closing)

        # Add spacing between JLPT levels
        if not is_last:
            next_char = sorted_kanji[i + 1][0]
            next_jlpt = sorted_kanji[i + 1][1].get('jlpt', 'N5')
            current_jlpt = data.get('jlpt', 'N5')
            if next_jlpt != current_jlpt:
                js_content.append('')
                js_content.append(f'  // ===== {next_jlpt} Kanji =====')
                js_content.append('')

    js_content.append('];')
    js_content.append('')
    js_content.append('// Export for use in other modules (if using ES6 modules)')
    js_content.append('// export default homeLifeKanji;')
    js_content.append('')
    js_content.append('// For Node.js / CommonJS')
    js_content.append('// module.exports = homeLifeKanji;')

    # Write to file
    output_file = 'temp/home-life-kanji-data.js'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(js_content))

    print(f"Task 1.5: Create Structured Data File")
    print("=" * 60)
    print(f"\n✅ JavaScript data file created!")
    print(f"   File: {output_file}")
    print(f"   Total kanji: {len(kanji_data)}")
    print(f"   Format: JavaScript array with full metadata")
    print(f"\n💾 Ready for integration with flashcard UI!")

    # Return stats for verification
    return {
        'total_kanji': len(kanji_data),
        'file_path': output_file
    }

if __name__ == '__main__':
    stats = generate_js_data_file()
