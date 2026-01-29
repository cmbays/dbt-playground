#!/usr/bin/env python3
"""
Task 1.3 - Batch 1: N5 Kanji Vocabulary
Generate 3 example words for each of the 32 N5 kanji
Total: 96 vocabulary entries
"""

import json

def load_kanji_data():
    with open('temp/kanji_with_jlpt_complete.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_kanji_data(data):
    with open('temp/kanji_with_jlpt_complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# N5 Kanji Vocabulary Database (32 kanji × 3 words = 96 entries)
# These are the most fundamental kanji for beginners
N5_VOCABULARY = {
    '下': [
        {'japanese': '下', 'hiragana': 'した', 'english': 'under, below', 'jlpt': 'N5'},
        {'japanese': '下さい', 'hiragana': 'ください', 'english': 'please (give me)', 'jlpt': 'N5'},
        {'japanese': '地下', 'hiragana': 'ちか', 'english': 'basement, underground', 'jlpt': 'N4'},
    ],
    '入': [
        {'japanese': '入る', 'hiragana': 'はいる', 'english': 'to enter', 'jlpt': 'N5'},
        {'japanese': '入れる', 'hiragana': 'いれる', 'english': 'to put in', 'jlpt': 'N5'},
        {'japanese': '入口', 'hiragana': 'いりぐち', 'english': 'entrance', 'jlpt': 'N5'},
    ],
    '出': [
        {'japanese': '出る', 'hiragana': 'でる', 'english': 'to go out, leave', 'jlpt': 'N5'},
        {'japanese': '出す', 'hiragana': 'だす', 'english': 'to take out', 'jlpt': 'N5'},
        {'japanese': '出口', 'hiragana': 'でぐち', 'english': 'exit', 'jlpt': 'N5'},
    ],
    '前': [
        {'japanese': '前', 'hiragana': 'まえ', 'english': 'front, before', 'jlpt': 'N5'},
        {'japanese': '午前', 'hiragana': 'ごぜん', 'english': 'morning, AM', 'jlpt': 'N5'},
        {'japanese': '名前', 'hiragana': 'なまえ', 'english': 'name', 'jlpt': 'N5'},
    ],
    '午': [
        {'japanese': '午前', 'hiragana': 'ごぜん', 'english': 'morning, AM', 'jlpt': 'N5'},
        {'japanese': '午後', 'hiragana': 'ごご', 'english': 'afternoon, PM', 'jlpt': 'N5'},
        {'japanese': '正午', 'hiragana': 'しょうご', 'english': 'noon', 'jlpt': 'N4'},
    ],
    '土': [
        {'japanese': '土', 'hiragana': 'つち', 'english': 'soil, earth', 'jlpt': 'N5'},
        {'japanese': '土曜日', 'hiragana': 'どようび', 'english': 'Saturday', 'jlpt': 'N5'},
        {'japanese': '土地', 'hiragana': 'とち', 'english': 'land', 'jlpt': 'N4'},
    ],
    '夜': [
        {'japanese': '夜', 'hiragana': 'よる', 'english': 'night', 'jlpt': 'N5'},
        {'japanese': '今夜', 'hiragana': 'こんや', 'english': 'tonight', 'jlpt': 'N5'},
        {'japanese': '夜中', 'hiragana': 'よなか', 'english': 'midnight', 'jlpt': 'N4'},
    ],
    '天': [
        {'japanese': '天気', 'hiragana': 'てんき', 'english': 'weather', 'jlpt': 'N5'},
        {'japanese': '天井', 'hiragana': 'てんじょう', 'english': 'ceiling', 'jlpt': 'N4'},
        {'japanese': '天国', 'hiragana': 'てんごく', 'english': 'heaven', 'jlpt': 'N3'},
    ],
    '女': [
        {'japanese': '女', 'hiragana': 'おんな', 'english': 'woman', 'jlpt': 'N5'},
        {'japanese': '女の子', 'hiragana': 'おんなのこ', 'english': 'girl', 'jlpt': 'N5'},
        {'japanese': '彼女', 'hiragana': 'かのじょ', 'english': 'she, girlfriend', 'jlpt': 'N5'},
    ],
    '子': [
        {'japanese': '子供', 'hiragana': 'こども', 'english': 'child', 'jlpt': 'N5'},
        {'japanese': '男の子', 'hiragana': 'おとこのこ', 'english': 'boy', 'jlpt': 'N5'},
        {'japanese': '女の子', 'hiragana': 'おんなのこ', 'english': 'girl', 'jlpt': 'N5'},
    ],
    '学': [
        {'japanese': '学校', 'hiragana': 'がっこう', 'english': 'school', 'jlpt': 'N5'},
        {'japanese': '学生', 'hiragana': 'がくせい', 'english': 'student', 'jlpt': 'N5'},
        {'japanese': '大学', 'hiragana': 'だいがく', 'english': 'university', 'jlpt': 'N5'},
    ],
    '帰': [
        {'japanese': '帰る', 'hiragana': 'かえる', 'english': 'to go home, return', 'jlpt': 'N5'},
        {'japanese': '帰り', 'hiragana': 'かえり', 'english': 'return (trip)', 'jlpt': 'N4'},
        {'japanese': '帰国', 'hiragana': 'きこく', 'english': 'return to one\'s country', 'jlpt': 'N3'},
    ],
    '後': [
        {'japanese': '後', 'hiragana': 'あと', 'english': 'after, later', 'jlpt': 'N5'},
        {'japanese': '午後', 'hiragana': 'ごご', 'english': 'afternoon, PM', 'jlpt': 'N5'},
        {'japanese': '後ろ', 'hiragana': 'うしろ', 'english': 'back, behind', 'jlpt': 'N5'},
    ],
    '新': [
        {'japanese': '新しい', 'hiragana': 'あたらしい', 'english': 'new', 'jlpt': 'N5'},
        {'japanese': '新聞', 'hiragana': 'しんぶん', 'english': 'newspaper', 'jlpt': 'N5'},
        {'japanese': '新年', 'hiragana': 'しんねん', 'english': 'new year', 'jlpt': 'N4'},
    ],
    '日': [
        {'japanese': '日', 'hiragana': 'ひ', 'english': 'day, sun', 'jlpt': 'N5'},
        {'japanese': '今日', 'hiragana': 'きょう', 'english': 'today', 'jlpt': 'N5'},
        {'japanese': '毎日', 'hiragana': 'まいにち', 'english': 'every day', 'jlpt': 'N5'},
    ],
    '早': [
        {'japanese': '早い', 'hiragana': 'はやい', 'english': 'early', 'jlpt': 'N5'},
        {'japanese': '早く', 'hiragana': 'はやく', 'english': 'early, quickly', 'jlpt': 'N5'},
        {'japanese': '早朝', 'hiragana': 'そうちょう', 'english': 'early morning', 'jlpt': 'N3'},
    ],
    '明': [
        {'japanese': '明るい', 'hiragana': 'あかるい', 'english': 'bright', 'jlpt': 'N5'},
        {'japanese': '明日', 'hiragana': 'あした', 'english': 'tomorrow', 'jlpt': 'N5'},
        {'japanese': '明らか', 'hiragana': 'あきらか', 'english': 'clear, obvious', 'jlpt': 'N3'},
    ],
    '時': [
        {'japanese': '時', 'hiragana': 'とき', 'english': 'time, when', 'jlpt': 'N5'},
        {'japanese': '時間', 'hiragana': 'じかん', 'english': 'time, hour', 'jlpt': 'N5'},
        {'japanese': '時計', 'hiragana': 'とけい', 'english': 'clock, watch', 'jlpt': 'N5'},
    ],
    '曜': [
        {'japanese': '曜日', 'hiragana': 'ようび', 'english': 'day of the week', 'jlpt': 'N5'},
        {'japanese': '月曜日', 'hiragana': 'げつようび', 'english': 'Monday', 'jlpt': 'N5'},
        {'japanese': '日曜日', 'hiragana': 'にちようび', 'english': 'Sunday', 'jlpt': 'N5'},
    ],
    '朝': [
        {'japanese': '朝', 'hiragana': 'あさ', 'english': 'morning', 'jlpt': 'N5'},
        {'japanese': '朝ごはん', 'hiragana': 'あさごはん', 'english': 'breakfast', 'jlpt': 'N5'},
        {'japanese': '今朝', 'hiragana': 'けさ', 'english': 'this morning', 'jlpt': 'N5'},
    ],
    '校': [
        {'japanese': '学校', 'hiragana': 'がっこう', 'english': 'school', 'jlpt': 'N5'},
        {'japanese': '高校', 'hiragana': 'こうこう', 'english': 'high school', 'jlpt': 'N5'},
        {'japanese': '校長', 'hiragana': 'こうちょう', 'english': 'principal', 'jlpt': 'N3'},
    ],
    '母': [
        {'japanese': '母', 'hiragana': 'はは', 'english': 'mother (one\'s own)', 'jlpt': 'N5'},
        {'japanese': 'お母さん', 'hiragana': 'おかあさん', 'english': 'mother (polite)', 'jlpt': 'N5'},
        {'japanese': '母親', 'hiragana': 'ははおや', 'english': 'mother (formal)', 'jlpt': 'N3'},
    ],
    '気': [
        {'japanese': '気', 'hiragana': 'き', 'english': 'spirit, feeling', 'jlpt': 'N5'},
        {'japanese': '元気', 'hiragana': 'げんき', 'english': 'healthy, energetic', 'jlpt': 'N5'},
        {'japanese': '天気', 'hiragana': 'てんき', 'english': 'weather', 'jlpt': 'N5'},
    ],
    '水': [
        {'japanese': '水', 'hiragana': 'みず', 'english': 'water', 'jlpt': 'N5'},
        {'japanese': '水曜日', 'hiragana': 'すいようび', 'english': 'Wednesday', 'jlpt': 'N5'},
        {'japanese': '水道', 'hiragana': 'すいどう', 'english': 'water supply', 'jlpt': 'N4'},
    ],
    '父': [
        {'japanese': '父', 'hiragana': 'ちち', 'english': 'father (one\'s own)', 'jlpt': 'N5'},
        {'japanese': 'お父さん', 'hiragana': 'おとうさん', 'english': 'father (polite)', 'jlpt': 'N5'},
        {'japanese': '父親', 'hiragana': 'ちちおや', 'english': 'father (formal)', 'jlpt': 'N3'},
    ],
    '男': [
        {'japanese': '男', 'hiragana': 'おとこ', 'english': 'man', 'jlpt': 'N5'},
        {'japanese': '男の子', 'hiragana': 'おとこのこ', 'english': 'boy', 'jlpt': 'N5'},
        {'japanese': '長男', 'hiragana': 'ちょうなん', 'english': 'eldest son', 'jlpt': 'N4'},
    ],
    '花': [
        {'japanese': '花', 'hiragana': 'はな', 'english': 'flower', 'jlpt': 'N5'},
        {'japanese': '花火', 'hiragana': 'はなび', 'english': 'fireworks', 'jlpt': 'N4'},
        {'japanese': '生け花', 'hiragana': 'いけばな', 'english': 'flower arrangement', 'jlpt': 'N3'},
    ],
    '話': [
        {'japanese': '話す', 'hiragana': 'はなす', 'english': 'to speak, talk', 'jlpt': 'N5'},
        {'japanese': '話', 'hiragana': 'はなし', 'english': 'story, talk', 'jlpt': 'N5'},
        {'japanese': '電話', 'hiragana': 'でんわ', 'english': 'telephone', 'jlpt': 'N5'},
    ],
    '足': [
        {'japanese': '足', 'hiragana': 'あし', 'english': 'foot, leg', 'jlpt': 'N5'},
        {'japanese': '足りる', 'hiragana': 'たりる', 'english': 'to be sufficient', 'jlpt': 'N4'},
        {'japanese': '不足', 'hiragana': 'ふそく', 'english': 'shortage', 'jlpt': 'N3'},
    ],
    '長': [
        {'japanese': '長い', 'hiragana': 'ながい', 'english': 'long', 'jlpt': 'N5'},
        {'japanese': '長男', 'hiragana': 'ちょうなん', 'english': 'eldest son', 'jlpt': 'N4'},
        {'japanese': '社長', 'hiragana': 'しゃちょう', 'english': 'company president', 'jlpt': 'N4'},
    ],
    '間': [
        {'japanese': '間', 'hiragana': 'あいだ', 'english': 'between, interval', 'jlpt': 'N5'},
        {'japanese': '時間', 'hiragana': 'じかん', 'english': 'time, hour', 'jlpt': 'N5'},
        {'japanese': '人間', 'hiragana': 'にんげん', 'english': 'human being', 'jlpt': 'N4'},
    ],
    '食': [
        {'japanese': '食べる', 'hiragana': 'たべる', 'english': 'to eat', 'jlpt': 'N5'},
        {'japanese': '食事', 'hiragana': 'しょくじ', 'english': 'meal', 'jlpt': 'N4'},
        {'japanese': '朝食', 'hiragana': 'ちょうしょく', 'english': 'breakfast', 'jlpt': 'N4'},
    ],
}

def main():
    print("Task 1.3 - Batch 1: N5 Kanji Vocabulary Generation")
    print("=" * 60)

    # Load existing kanji data
    kanji_data = load_kanji_data()

    # Add vocabulary to N5 kanji
    added_count = 0
    for kanji_char, words in N5_VOCABULARY.items():
        if kanji_char in kanji_data:
            kanji_data[kanji_char]['words'] = words
            added_count += 1
        else:
            print(f"Warning: {kanji_char} not found in kanji data")

    # Save updated data
    save_kanji_data(kanji_data)

    print(f"\n✅ Batch 1 Complete!")
    print(f"   N5 Kanji processed: {added_count}")
    print(f"   Total words added: {added_count * 3}")
    print(f"\n💾 Saved to: temp/kanji_with_jlpt_complete.json")

    # Verify all N5 kanji have words
    n5_kanji_in_data = {k: v for k, v in kanji_data.items() if v.get('jlpt') == 'N5'}
    missing_words = [k for k, v in n5_kanji_in_data.items() if 'words' not in v]

    if missing_words:
        print(f"\n⚠️  Warning: {len(missing_words)} N5 kanji still missing words:")
        print(f"   {' '.join(missing_words)}")
    else:
        print(f"\n✅ All {len(n5_kanji_in_data)} N5 kanji now have example words!")

if __name__ == '__main__':
    main()
