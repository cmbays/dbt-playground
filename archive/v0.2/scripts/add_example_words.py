#!/usr/bin/env python3
"""
Add 3 example vocabulary words to each kanji
Total: 169 kanji × 3 words = 507 vocabulary entries
"""

import json

# Comprehensive vocabulary database for all 169 kanji
# Format: kanji_character: [word1, word2, word3]
# Each word: {japanese, hiragana, english, jlpt}

EXAMPLE_WORDS = {
    # Common kanji with home-life vocabulary
    '丁': [
        {'japanese': '丁寧', 'hiragana': 'ていねい', 'english': 'polite, careful', 'jlpt': 'N4'},
        {'japanese': '包丁', 'hiragana': 'ほうちょう', 'english': 'kitchen knife', 'jlpt': 'N4'},
        {'japanese': '一丁', 'hiragana': 'いっちょう', 'english': 'one item (counter)', 'jlpt': 'N3'},
    ],
    '下': [
        {'japanese': '下', 'hiragana': 'した', 'english': 'under, below', 'jlpt': 'N5'},
        {'japanese': '下さい', 'hiragana': 'ください', 'english': 'please give me', 'jlpt': 'N5'},
        {'japanese': '地下', 'hiragana': 'ちか', 'english': 'basement, underground', 'jlpt': 'N4'},
    ],
    '並': [
        {'japanese': '並べる', 'hiragana': 'ならべる', 'english': 'to line up, arrange', 'jlpt': 'N4'},
        {'japanese': '並ぶ', 'hiragana': 'ならぶ', 'english': 'to line up, stand in line', 'jlpt': 'N4'},
        {'japanese': '並木', 'hiragana': 'なみき', 'english': 'row of trees', 'jlpt': 'N3'},
    ],
    '乾': [
        {'japanese': '乾く', 'hiragana': 'かわく', 'english': 'to dry', 'jlpt': 'N4'},
        {'japanese': '乾かす', 'hiragana': 'かわかす', 'english': 'to dry (something)', 'jlpt': 'N4'},
        {'japanese': '乾燥', 'hiragana': 'かんそう', 'english': 'drying, dry weather', 'jlpt': 'N3'},
    ],
    '事': [
        {'japanese': '事', 'hiragana': 'こと', 'english': 'thing, matter', 'jlpt': 'N5'},
        {'japanese': '仕事', 'hiragana': 'しごと', 'english': 'work, job', 'jlpt': 'N5'},
        {'japanese': '食事', 'hiragana': 'しょくじ', 'english': 'meal', 'jlpt': 'N4'},
    ],
    '仕': [
        {'japanese': '仕事', 'hiragana': 'しごと', 'english': 'work, job', 'jlpt': 'N5'},
        {'japanese': '仕方', 'hiragana': 'しかた', 'english': 'way, method', 'jlpt': 'N4'},
        {'japanese': '仕上げる', 'hiragana': 'しあげる', 'english': 'to finish up', 'jlpt': 'N3'},
    ],
    '付': [
        {'japanese': '付く', 'hiragana': 'つく', 'english': 'to be attached', 'jlpt': 'N4'},
        {'japanese': '付ける', 'hiragana': 'つける', 'english': 'to attach', 'jlpt': 'N4'},
        {'japanese': '気を付ける', 'hiragana': 'きをつける', 'english': 'to be careful', 'jlpt': 'N4'},
    ],
    '伝': [
        {'japanese': '伝える', 'hiragana': 'つたえる', 'english': 'to convey, tell', 'jlpt': 'N4'},
        {'japanese': '伝統', 'hiragana': 'でんとう', 'english': 'tradition', 'jlpt': 'N3'},
        {'japanese': '伝言', 'hiragana': 'でんごん', 'english': 'message', 'jlpt': 'N3'},
    ],
    '作': [
        {'japanese': '作る', 'hiragana': 'つくる', 'english': 'to make, create', 'jlpt': 'N5'},
        {'japanese': '作品', 'hiragana': 'さくひん', 'english': 'work (of art)', 'jlpt': 'N4'},
        {'japanese': '作業', 'hiragana': 'さぎょう', 'english': 'work, operation', 'jlpt': 'N4'},
    ],
    '供': [
        {'japanese': '子供', 'hiragana': 'こども', 'english': 'child', 'jlpt': 'N5'},
        {'japanese': '提供', 'hiragana': 'ていきょう', 'english': 'offer, provide', 'jlpt': 'N3'},
        {'japanese': 'お供', 'hiragana': 'おとも', 'english': 'attendant', 'jlpt': 'N3'},
    ],
}

print(f\"Starting example words generation...\")
print(f\"Sample created: {len(EXAMPLE_WORDS)} kanji so far\")
print(f\"Need to continue for remaining {169 - len(EXAMPLE_WORDS)} kanji\")
print(f\"\\nThis script needs to be expanded with all 169 kanji.\")
print(f\"Each kanji needs 3 carefully chosen vocabulary words.\")
