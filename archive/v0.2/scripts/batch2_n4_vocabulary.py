#!/usr/bin/env python3
"""
Task 1.3 - Batch 2: Add Example Vocabulary for N4 Kanji
Generate 3 example words for each N4 kanji (49 kanji × 3 = 147 words)
"""

import json

# Complete N4 vocabulary (49 kanji × 3 words each = 147 total)
N4_VOCABULARY = {
    '並': [
        {'japanese': '並ぶ', 'hiragana': 'ならぶ', 'english': 'to line up', 'jlpt': 'N4'},
        {'japanese': '並べる', 'hiragana': 'ならべる', 'english': 'to arrange', 'jlpt': 'N4'},
        {'japanese': '人並み', 'hiragana': 'ひとなみ', 'english': 'average, ordinary', 'jlpt': 'N3'},
    ],
    '乾': [
        {'japanese': '乾く', 'hiragana': 'かわく', 'english': 'to dry', 'jlpt': 'N4'},
        {'japanese': '乾かす', 'hiragana': 'かわかす', 'english': 'to dry (something)', 'jlpt': 'N3'},
        {'japanese': '乾燥', 'hiragana': 'かんそう', 'english': 'dryness', 'jlpt': 'N3'},
    ],
    '事': [
        {'japanese': '事', 'hiragana': 'こと', 'english': 'thing, matter', 'jlpt': 'N5'},
        {'japanese': '仕事', 'hiragana': 'しごと', 'english': 'work, job', 'jlpt': 'N5'},
        {'japanese': '大事', 'hiragana': 'だいじ', 'english': 'important', 'jlpt': 'N4'},
    ],
    '仕': [
        {'japanese': '仕事', 'hiragana': 'しごと', 'english': 'work, job', 'jlpt': 'N5'},
        {'japanese': '仕方', 'hiragana': 'しかた', 'english': 'way, method', 'jlpt': 'N4'},
        {'japanese': '仕上げる', 'hiragana': 'しあげる', 'english': 'to finish up', 'jlpt': 'N3'},
    ],
    '作': [
        {'japanese': '作る', 'hiragana': 'つくる', 'english': 'to make', 'jlpt': 'N5'},
        {'japanese': '作文', 'hiragana': 'さくぶん', 'english': 'composition', 'jlpt': 'N4'},
        {'japanese': '作品', 'hiragana': 'さくひん', 'english': 'work of art', 'jlpt': 'N4'},
    ],
    '供': [
        {'japanese': '子供', 'hiragana': 'こども', 'english': 'child', 'jlpt': 'N5'},
        {'japanese': '提供', 'hiragana': 'ていきょう', 'english': 'offer, provision', 'jlpt': 'N3'},
        {'japanese': '供給', 'hiragana': 'きょうきゅう', 'english': 'supply', 'jlpt': 'N2'},
    ],
    '全': [
        {'japanese': '全部', 'hiragana': 'ぜんぶ', 'english': 'all, everything', 'jlpt': 'N4'},
        {'japanese': '全員', 'hiragana': 'ぜんいん', 'english': 'all members', 'jlpt': 'N4'},
        {'japanese': '全て', 'hiragana': 'すべて', 'english': 'all, everything', 'jlpt': 'N3'},
    ],
    '切': [
        {'japanese': '切る', 'hiragana': 'きる', 'english': 'to cut', 'jlpt': 'N5'},
        {'japanese': '切手', 'hiragana': 'きって', 'english': 'stamp', 'jlpt': 'N5'},
        {'japanese': '大切', 'hiragana': 'たいせつ', 'english': 'important', 'jlpt': 'N4'},
    ],
    '力': [
        {'japanese': '力', 'hiragana': 'ちから', 'english': 'power, strength', 'jlpt': 'N4'},
        {'japanese': '電力', 'hiragana': 'でんりょく', 'english': 'electric power', 'jlpt': 'N3'},
        {'japanese': '努力', 'hiragana': 'どりょく', 'english': 'effort', 'jlpt': 'N3'},
    ],
    '台': [
        {'japanese': '台所', 'hiragana': 'だいどころ', 'english': 'kitchen', 'jlpt': 'N4'},
        {'japanese': '台風', 'hiragana': 'たいふう', 'english': 'typhoon', 'jlpt': 'N4'},
        {'japanese': '一台', 'hiragana': 'いちだい', 'english': 'one (machine)', 'jlpt': 'N4'},
    ],
    '味': [
        {'japanese': '味', 'hiragana': 'あじ', 'english': 'taste, flavor', 'jlpt': 'N4'},
        {'japanese': '味噌', 'hiragana': 'みそ', 'english': 'miso', 'jlpt': 'N4'},
        {'japanese': '意味', 'hiragana': 'いみ', 'english': 'meaning', 'jlpt': 'N4'},
    ],
    '員': [
        {'japanese': '全員', 'hiragana': 'ぜんいん', 'english': 'all members', 'jlpt': 'N4'},
        {'japanese': '会員', 'hiragana': 'かいいん', 'english': 'member', 'jlpt': 'N4'},
        {'japanese': '店員', 'hiragana': 'てんいん', 'english': 'store clerk', 'jlpt': 'N4'},
    ],
    '声': [
        {'japanese': '声', 'hiragana': 'こえ', 'english': 'voice', 'jlpt': 'N4'},
        {'japanese': '大声', 'hiragana': 'おおごえ', 'english': 'loud voice', 'jlpt': 'N3'},
        {'japanese': '声明', 'hiragana': 'せいめい', 'english': 'statement', 'jlpt': 'N2'},
    ],
    '夕': [
        {'japanese': '夕方', 'hiragana': 'ゆうがた', 'english': 'evening', 'jlpt': 'N4'},
        {'japanese': '夕食', 'hiragana': 'ゆうしょく', 'english': 'dinner', 'jlpt': 'N4'},
        {'japanese': '夕日', 'hiragana': 'ゆうひ', 'english': 'setting sun', 'jlpt': 'N3'},
    ],
    '始': [
        {'japanese': '始める', 'hiragana': 'はじめる', 'english': 'to begin', 'jlpt': 'N5'},
        {'japanese': '始まる', 'hiragana': 'はじまる', 'english': 'to start', 'jlpt': 'N5'},
        {'japanese': '始発', 'hiragana': 'しはつ', 'english': 'first train', 'jlpt': 'N3'},
    ],
    '家': [
        {'japanese': '家', 'hiragana': 'いえ', 'english': 'house', 'jlpt': 'N5'},
        {'japanese': '家族', 'hiragana': 'かぞく', 'english': 'family', 'jlpt': 'N5'},
        {'japanese': '家庭', 'hiragana': 'かてい', 'english': 'home, family', 'jlpt': 'N4'},
    ],
    '寝': [
        {'japanese': '寝る', 'hiragana': 'ねる', 'english': 'to sleep', 'jlpt': 'N5'},
        {'japanese': '寝室', 'hiragana': 'しんしつ', 'english': 'bedroom', 'jlpt': 'N4'},
        {'japanese': '寝坊', 'hiragana': 'ねぼう', 'english': 'oversleep', 'jlpt': 'N3'},
    ],
    '屋': [
        {'japanese': '部屋', 'hiragana': 'へや', 'english': 'room', 'jlpt': 'N5'},
        {'japanese': '屋根', 'hiragana': 'やね', 'english': 'roof', 'jlpt': 'N4'},
        {'japanese': '屋上', 'hiragana': 'おくじょう', 'english': 'rooftop', 'jlpt': 'N4'},
    ],
    '度': [
        {'japanese': '度', 'hiragana': 'ど', 'english': 'degree, time', 'jlpt': 'N4'},
        {'japanese': '温度', 'hiragana': 'おんど', 'english': 'temperature', 'jlpt': 'N4'},
        {'japanese': '一度', 'hiragana': 'いちど', 'english': 'once', 'jlpt': 'N4'},
    ],
    '庭': [
        {'japanese': '庭', 'hiragana': 'にわ', 'english': 'garden', 'jlpt': 'N4'},
        {'japanese': '家庭', 'hiragana': 'かてい', 'english': 'home, family', 'jlpt': 'N4'},
        {'japanese': '庭園', 'hiragana': 'ていえん', 'english': 'garden, park', 'jlpt': 'N3'},
    ],
    '息': [
        {'japanese': '息子', 'hiragana': 'むすこ', 'english': 'son', 'jlpt': 'N5'},
        {'japanese': '息', 'hiragana': 'いき', 'english': 'breath', 'jlpt': 'N4'},
        {'japanese': '休息', 'hiragana': 'きゅうそく', 'english': 'rest', 'jlpt': 'N3'},
    ],
    '意': [
        {'japanese': '意味', 'hiragana': 'いみ', 'english': 'meaning', 'jlpt': 'N4'},
        {'japanese': '意見', 'hiragana': 'いけん', 'english': 'opinion', 'jlpt': 'N4'},
        {'japanese': '注意', 'hiragana': 'ちゅうい', 'english': 'attention, caution', 'jlpt': 'N4'},
    ],
    '所': [
        {'japanese': '所', 'hiragana': 'ところ', 'english': 'place', 'jlpt': 'N5'},
        {'japanese': '台所', 'hiragana': 'だいどころ', 'english': 'kitchen', 'jlpt': 'N4'},
        {'japanese': '場所', 'hiragana': 'ばしょ', 'english': 'location', 'jlpt': 'N4'},
    ],
    '持': [
        {'japanese': '持つ', 'hiragana': 'もつ', 'english': 'to hold', 'jlpt': 'N5'},
        {'japanese': '気持ち', 'hiragana': 'きもち', 'english': 'feeling', 'jlpt': 'N4'},
        {'japanese': '持って行く', 'hiragana': 'もっていく', 'english': 'to take', 'jlpt': 'N4'},
    ],
    '教': [
        {'japanese': '教える', 'hiragana': 'おしえる', 'english': 'to teach', 'jlpt': 'N5'},
        {'japanese': '教室', 'hiragana': 'きょうしつ', 'english': 'classroom', 'jlpt': 'N5'},
        {'japanese': '教科書', 'hiragana': 'きょうかしょ', 'english': 'textbook', 'jlpt': 'N4'},
    ],
    '料': [
        {'japanese': '料理', 'hiragana': 'りょうり', 'english': 'cooking, cuisine', 'jlpt': 'N5'},
        {'japanese': '料金', 'hiragana': 'りょうきん', 'english': 'fee, charge', 'jlpt': 'N4'},
        {'japanese': '材料', 'hiragana': 'ざいりょう', 'english': 'ingredients', 'jlpt': 'N4'},
    ],
    '族': [
        {'japanese': '家族', 'hiragana': 'かぞく', 'english': 'family', 'jlpt': 'N5'},
        {'japanese': '民族', 'hiragana': 'みんぞく', 'english': 'ethnic group', 'jlpt': 'N3'},
        {'japanese': '部族', 'hiragana': 'ぶぞく', 'english': 'tribe', 'jlpt': 'N2'},
    ],
    '机': [
        {'japanese': '机', 'hiragana': 'つくえ', 'english': 'desk', 'jlpt': 'N5'},
        {'japanese': '机上', 'hiragana': 'きじょう', 'english': 'on the desk', 'jlpt': 'N2'},
        {'japanese': '勉強机', 'hiragana': 'べんきょうづくえ', 'english': 'study desk', 'jlpt': 'N4'},
    ],
    '楽': [
        {'japanese': '楽しい', 'hiragana': 'たのしい', 'english': 'fun, enjoyable', 'jlpt': 'N5'},
        {'japanese': '楽', 'hiragana': 'らく', 'english': 'easy, comfortable', 'jlpt': 'N4'},
        {'japanese': '音楽', 'hiragana': 'おんがく', 'english': 'music', 'jlpt': 'N5'},
    ],
    '汁': [
        {'japanese': '汁', 'hiragana': 'しる', 'english': 'soup, juice', 'jlpt': 'N4'},
        {'japanese': '味噌汁', 'hiragana': 'みそしる', 'english': 'miso soup', 'jlpt': 'N5'},
        {'japanese': '果汁', 'hiragana': 'かじゅう', 'english': 'fruit juice', 'jlpt': 'N3'},
    ],
    '洗': [
        {'japanese': '洗う', 'hiragana': 'あらう', 'english': 'to wash', 'jlpt': 'N5'},
        {'japanese': '洗濯', 'hiragana': 'せんたく', 'english': 'laundry', 'jlpt': 'N5'},
        {'japanese': '洗面所', 'hiragana': 'せんめんじょ', 'english': 'bathroom', 'jlpt': 'N4'},
    ],
    '温': [
        {'japanese': '温かい', 'hiragana': 'あたたかい', 'english': 'warm', 'jlpt': 'N5'},
        {'japanese': '温度', 'hiragana': 'おんど', 'english': 'temperature', 'jlpt': 'N4'},
        {'japanese': '温泉', 'hiragana': 'おんせん', 'english': 'hot spring', 'jlpt': 'N4'},
    ],
    '満': [
        {'japanese': '満足', 'hiragana': 'まんぞく', 'english': 'satisfaction', 'jlpt': 'N4'},
        {'japanese': '満ちる', 'hiragana': 'みちる', 'english': 'to be full', 'jlpt': 'N3'},
        {'japanese': '満員', 'hiragana': 'まんいん', 'english': 'full capacity', 'jlpt': 'N3'},
    ],
    '牛': [
        {'japanese': '牛', 'hiragana': 'うし', 'english': 'cow', 'jlpt': 'N5'},
        {'japanese': '牛肉', 'hiragana': 'ぎゅうにく', 'english': 'beef', 'jlpt': 'N5'},
        {'japanese': '牛乳', 'hiragana': 'ぎゅうにゅう', 'english': 'milk', 'jlpt': 'N5'},
    ],
    '理': [
        {'japanese': '料理', 'hiragana': 'りょうり', 'english': 'cooking, cuisine', 'jlpt': 'N5'},
        {'japanese': '理由', 'hiragana': 'りゆう', 'english': 'reason', 'jlpt': 'N4'},
        {'japanese': '整理', 'hiragana': 'せいり', 'english': 'organization', 'jlpt': 'N4'},
    ],
    '用': [
        {'japanese': '用事', 'hiragana': 'ようじ', 'english': 'errand, business', 'jlpt': 'N4'},
        {'japanese': '使用', 'hiragana': 'しよう', 'english': 'use', 'jlpt': 'N4'},
        {'japanese': '用意', 'hiragana': 'ようい', 'english': 'preparation', 'jlpt': 'N4'},
    ],
    '的': [
        {'japanese': '的', 'hiragana': 'てき', 'english': '-tic, -ical', 'jlpt': 'N4'},
        {'japanese': '目的', 'hiragana': 'もくてき', 'english': 'purpose', 'jlpt': 'N4'},
        {'japanese': '基本的', 'hiragana': 'きほんてき', 'english': 'basic', 'jlpt': 'N4'},
    ],
    '着': [
        {'japanese': '着る', 'hiragana': 'きる', 'english': 'to wear', 'jlpt': 'N5'},
        {'japanese': '着く', 'hiragana': 'つく', 'english': 'to arrive', 'jlpt': 'N5'},
        {'japanese': '到着', 'hiragana': 'とうちゃく', 'english': 'arrival', 'jlpt': 'N4'},
    ],
    '脱': [
        {'japanese': '脱ぐ', 'hiragana': 'ぬぐ', 'english': 'to take off', 'jlpt': 'N5'},
        {'japanese': '脱衣所', 'hiragana': 'だついじょ', 'english': 'changing room', 'jlpt': 'N3'},
        {'japanese': '脱出', 'hiragana': 'だっしゅつ', 'english': 'escape', 'jlpt': 'N3'},
    ],
    '茶': [
        {'japanese': 'お茶', 'hiragana': 'おちゃ', 'english': 'tea', 'jlpt': 'N5'},
        {'japanese': '茶色', 'hiragana': 'ちゃいろ', 'english': 'brown', 'jlpt': 'N5'},
        {'japanese': '紅茶', 'hiragana': 'こうちゃ', 'english': 'black tea', 'jlpt': 'N4'},
    ],
    '菜': [
        {'japanese': '野菜', 'hiragana': 'やさい', 'english': 'vegetable', 'jlpt': 'N5'},
        {'japanese': '菜食', 'hiragana': 'さいしょく', 'english': 'vegetarian diet', 'jlpt': 'N2'},
        {'japanese': '白菜', 'hiragana': 'はくさい', 'english': 'Chinese cabbage', 'jlpt': 'N3'},
    ],
    '計': [
        {'japanese': '時計', 'hiragana': 'とけい', 'english': 'clock, watch', 'jlpt': 'N5'},
        {'japanese': '計画', 'hiragana': 'けいかく', 'english': 'plan', 'jlpt': 'N4'},
        {'japanese': '合計', 'hiragana': 'ごうけい', 'english': 'total', 'jlpt': 'N3'},
    ],
    '起': [
        {'japanese': '起きる', 'hiragana': 'おきる', 'english': 'to wake up', 'jlpt': 'N5'},
        {'japanese': '起こす', 'hiragana': 'おこす', 'english': 'to wake (someone)', 'jlpt': 'N4'},
        {'japanese': '起立', 'hiragana': 'きりつ', 'english': 'stand up', 'jlpt': 'N3'},
    ],
    '部': [
        {'japanese': '部屋', 'hiragana': 'へや', 'english': 'room', 'jlpt': 'N5'},
        {'japanese': '全部', 'hiragana': 'ぜんぶ', 'english': 'all, everything', 'jlpt': 'N4'},
        {'japanese': '部分', 'hiragana': 'ぶぶん', 'english': 'part, portion', 'jlpt': 'N4'},
    ],
    '重': [
        {'japanese': '重い', 'hiragana': 'おもい', 'english': 'heavy', 'jlpt': 'N5'},
        {'japanese': '重要', 'hiragana': 'じゅうよう', 'english': 'important', 'jlpt': 'N4'},
        {'japanese': '重さ', 'hiragana': 'おもさ', 'english': 'weight', 'jlpt': 'N4'},
    ],
    '野': [
        {'japanese': '野菜', 'hiragana': 'やさい', 'english': 'vegetable', 'jlpt': 'N5'},
        {'japanese': '野球', 'hiragana': 'やきゅう', 'english': 'baseball', 'jlpt': 'N5'},
        {'japanese': '平野', 'hiragana': 'へいや', 'english': 'plain, field', 'jlpt': 'N3'},
    ],
    '開': [
        {'japanese': '開く', 'hiragana': 'あく', 'english': 'to open', 'jlpt': 'N5'},
        {'japanese': '開ける', 'hiragana': 'あける', 'english': 'to open', 'jlpt': 'N5'},
        {'japanese': '開始', 'hiragana': 'かいし', 'english': 'start', 'jlpt': 'N4'},
    ],
    '集': [
        {'japanese': '集める', 'hiragana': 'あつめる', 'english': 'to collect', 'jlpt': 'N4'},
        {'japanese': '集まる', 'hiragana': 'あつまる', 'english': 'to gather', 'jlpt': 'N4'},
        {'japanese': '集中', 'hiragana': 'しゅうちゅう', 'english': 'concentration', 'jlpt': 'N3'},
    ],
    '風': [
        {'japanese': '風', 'hiragana': 'かぜ', 'english': 'wind', 'jlpt': 'N4'},
        {'japanese': '風呂', 'hiragana': 'ふろ', 'english': 'bath', 'jlpt': 'N5'},
        {'japanese': '台風', 'hiragana': 'たいふう', 'english': 'typhoon', 'jlpt': 'N4'},
    ],
}

def add_n4_vocabulary():
    """Add example vocabulary for N4 kanji"""

    # Load current data
    with open('temp/kanji_with_jlpt_complete.json', 'r', encoding='utf-8') as f:
        kanji_data = json.load(f)

    # Add words to N4 kanji
    n4_count = 0
    word_count = 0

    for char, words in N4_VOCABULARY.items():
        if char in kanji_data and kanji_data[char].get('jlpt') == 'N4':
            kanji_data[char]['words'] = words
            n4_count += 1
            word_count += len(words)

    # Save updated data
    with open('temp/kanji_with_jlpt_complete.json', 'w', encoding='utf-8') as f:
        json.dump(kanji_data, f, ensure_ascii=False, indent=2)

    print(f"Task 1.3 - Batch 2: N4 Kanji Vocabulary Generation")
    print("=" * 60)
    print(f"\n✅ Batch 2 Complete!")
    print(f"   N4 Kanji processed: {n4_count}")
    print(f"   Total words added: {word_count}")
    print(f"\n💾 Saved to: temp/kanji_with_jlpt_complete.json")
    print(f"\n✅ All {n4_count} N4 kanji now have example words!")

if __name__ == '__main__':
    add_n4_vocabulary()
