#!/usr/bin/env python3
"""
Task 1.3 - Batch 3: Add Example Vocabulary for N3 Kanji
Generate 3 example words for each N3 kanji (52 kanji × 3 = 156 words)
"""

import json

# Complete N3 vocabulary (52 kanji × 3 words each = 156 total)
N3_VOCABULARY = {
    '丁': [
        {'japanese': '丁寧', 'hiragana': 'ていねい', 'english': 'polite, careful', 'jlpt': 'N4'},
        {'japanese': '包丁', 'hiragana': 'ほうちょう', 'english': 'kitchen knife', 'jlpt': 'N3'},
        {'japanese': '一丁', 'hiragana': 'いっちょう', 'english': 'one block, one item', 'jlpt': 'N3'},
    ],
    '付': [
        {'japanese': '付ける', 'hiragana': 'つける', 'english': 'to attach', 'jlpt': 'N5'},
        {'japanese': '付く', 'hiragana': 'つく', 'english': 'to be attached', 'jlpt': 'N5'},
        {'japanese': '受付', 'hiragana': 'うけつけ', 'english': 'reception', 'jlpt': 'N4'},
    ],
    '伝': [
        {'japanese': '伝える', 'hiragana': 'つたえる', 'english': 'to convey', 'jlpt': 'N4'},
        {'japanese': '伝統', 'hiragana': 'でんとう', 'english': 'tradition', 'jlpt': 'N3'},
        {'japanese': '伝言', 'hiragana': 'でんごん', 'english': 'message', 'jlpt': 'N3'},
    ],
    '備': [
        {'japanese': '準備', 'hiragana': 'じゅんび', 'english': 'preparation', 'jlpt': 'N4'},
        {'japanese': '設備', 'hiragana': 'せつび', 'english': 'equipment', 'jlpt': 'N3'},
        {'japanese': '予備', 'hiragana': 'よび', 'english': 'reserve, spare', 'jlpt': 'N3'},
    ],
    '冷': [
        {'japanese': '冷たい', 'hiragana': 'つめたい', 'english': 'cold', 'jlpt': 'N5'},
        {'japanese': '冷蔵庫', 'hiragana': 'れいぞうこ', 'english': 'refrigerator', 'jlpt': 'N5'},
        {'japanese': '冷凍', 'hiragana': 'れいとう', 'english': 'freezing', 'jlpt': 'N3'},
    ],
    '初': [
        {'japanese': '初めて', 'hiragana': 'はじめて', 'english': 'for the first time', 'jlpt': 'N5'},
        {'japanese': '最初', 'hiragana': 'さいしょ', 'english': 'first, beginning', 'jlpt': 'N4'},
        {'japanese': '初級', 'hiragana': 'しょきゅう', 'english': 'beginner level', 'jlpt': 'N3'},
    ],
    '加': [
        {'japanese': '加える', 'hiragana': 'くわえる', 'english': 'to add', 'jlpt': 'N3'},
        {'japanese': '参加', 'hiragana': 'さんか', 'english': 'participation', 'jlpt': 'N4'},
        {'japanese': '追加', 'hiragana': 'ついか', 'english': 'addition', 'jlpt': 'N3'},
    ],
    '協': [
        {'japanese': '協力', 'hiragana': 'きょうりょく', 'english': 'cooperation', 'jlpt': 'N3'},
        {'japanese': '協会', 'hiragana': 'きょうかい', 'english': 'association', 'jlpt': 'N3'},
        {'japanese': '協定', 'hiragana': 'きょうてい', 'english': 'agreement', 'jlpt': 'N2'},
    ],
    '器': [
        {'japanese': '器', 'hiragana': 'うつわ', 'english': 'container, dish', 'jlpt': 'N3'},
        {'japanese': '食器', 'hiragana': 'しょっき', 'english': 'tableware', 'jlpt': 'N3'},
        {'japanese': '機器', 'hiragana': 'きき', 'english': 'equipment', 'jlpt': 'N2'},
    ],
    '娘': [
        {'japanese': '娘', 'hiragana': 'むすめ', 'english': 'daughter', 'jlpt': 'N5'},
        {'japanese': 'お嬢さん', 'hiragana': 'おじょうさん', 'english': 'daughter (polite)', 'jlpt': 'N4'},
        {'japanese': '娘さん', 'hiragana': 'むすめさん', 'english': 'daughter (polite)', 'jlpt': 'N4'},
    ],
    '居': [
        {'japanese': '居る', 'hiragana': 'いる', 'english': 'to be (animate)', 'jlpt': 'N5'},
        {'japanese': '居間', 'hiragana': 'いま', 'english': 'living room', 'jlpt': 'N4'},
        {'japanese': '居住', 'hiragana': 'きょじゅう', 'english': 'residence', 'jlpt': 'N3'},
    ],
    '弁': [
        {'japanese': '弁当', 'hiragana': 'べんとう', 'english': 'boxed lunch', 'jlpt': 'N5'},
        {'japanese': '弁護士', 'hiragana': 'べんごし', 'english': 'lawyer', 'jlpt': 'N3'},
        {'japanese': '答弁', 'hiragana': 'とうべん', 'english': 'answer, reply', 'jlpt': 'N2'},
    ],
    '当': [
        {'japanese': '当たる', 'hiragana': 'あたる', 'english': 'to hit', 'jlpt': 'N4'},
        {'japanese': '本当', 'hiragana': 'ほんとう', 'english': 'truth, really', 'jlpt': 'N5'},
        {'japanese': '弁当', 'hiragana': 'べんとう', 'english': 'boxed lunch', 'jlpt': 'N5'},
    ],
    '抜': [
        {'japanese': '抜く', 'hiragana': 'ぬく', 'english': 'to pull out', 'jlpt': 'N3'},
        {'japanese': '抜ける', 'hiragana': 'ぬける', 'english': 'to come out', 'jlpt': 'N3'},
        {'japanese': '選抜', 'hiragana': 'せんばつ', 'english': 'selection', 'jlpt': 'N2'},
    ],
    '担': [
        {'japanese': '担当', 'hiragana': 'たんとう', 'english': 'in charge of', 'jlpt': 'N3'},
        {'japanese': '担ぐ', 'hiragana': 'かつぐ', 'english': 'to carry on shoulder', 'jlpt': 'N3'},
        {'japanese': '負担', 'hiragana': 'ふたん', 'english': 'burden', 'jlpt': 'N3'},
    ],
    '拭': [
        {'japanese': '拭く', 'hiragana': 'ふく', 'english': 'to wipe', 'jlpt': 'N3'},
        {'japanese': '拭き取る', 'hiragana': 'ふきとる', 'english': 'to wipe off', 'jlpt': 'N3'},
        {'japanese': '払拭', 'hiragana': 'ふっしょく', 'english': 'wiping out', 'jlpt': 'N1'},
    ],
    '捨': [
        {'japanese': '捨てる', 'hiragana': 'すてる', 'english': 'to throw away', 'jlpt': 'N5'},
        {'japanese': '見捨てる', 'hiragana': 'みすてる', 'english': 'to abandon', 'jlpt': 'N3'},
        {'japanese': '使い捨て', 'hiragana': 'つかいすて', 'english': 'disposable', 'jlpt': 'N3'},
    ],
    '揚': [
        {'japanese': '揚げる', 'hiragana': 'あげる', 'english': 'to deep-fry', 'jlpt': 'N3'},
        {'japanese': '唐揚げ', 'hiragana': 'からあげ', 'english': 'fried chicken', 'jlpt': 'N3'},
        {'japanese': '揚げ物', 'hiragana': 'あげもの', 'english': 'fried food', 'jlpt': 'N3'},
    ],
    '整': [
        {'japanese': '整理', 'hiragana': 'せいり', 'english': 'organize', 'jlpt': 'N3'},
        {'japanese': '整える', 'hiragana': 'ととのえる', 'english': 'to arrange', 'jlpt': 'N3'},
        {'japanese': '整頓', 'hiragana': 'せいとん', 'english': 'tidying up', 'jlpt': 'N3'},
    ],
    '替': [
        {'japanese': '替える', 'hiragana': 'かえる', 'english': 'to replace', 'jlpt': 'N3'},
        {'japanese': '両替', 'hiragana': 'りょうがえ', 'english': 'money exchange', 'jlpt': 'N3'},
        {'japanese': '交替', 'hiragana': 'こうたい', 'english': 'alternation', 'jlpt': 'N3'},
    ],
    '最': [
        {'japanese': '最も', 'hiragana': 'もっとも', 'english': 'most', 'jlpt': 'N3'},
        {'japanese': '最初', 'hiragana': 'さいしょ', 'english': 'first', 'jlpt': 'N4'},
        {'japanese': '最近', 'hiragana': 'さいきん', 'english': 'recently', 'jlpt': 'N5'},
    ],
    '材': [
        {'japanese': '材料', 'hiragana': 'ざいりょう', 'english': 'ingredients', 'jlpt': 'N4'},
        {'japanese': '教材', 'hiragana': 'きょうざい', 'english': 'teaching materials', 'jlpt': 'N3'},
        {'japanese': '題材', 'hiragana': 'だいざい', 'english': 'subject matter', 'jlpt': 'N2'},
    ],
    '柔': [
        {'japanese': '柔らかい', 'hiragana': 'やわらかい', 'english': 'soft', 'jlpt': 'N4'},
        {'japanese': '柔道', 'hiragana': 'じゅうどう', 'english': 'judo', 'jlpt': 'N4'},
        {'japanese': '柔軟', 'hiragana': 'じゅうなん', 'english': 'flexible', 'jlpt': 'N3'},
    ],
    '機': [
        {'japanese': '機械', 'hiragana': 'きかい', 'english': 'machine', 'jlpt': 'N4'},
        {'japanese': '飛行機', 'hiragana': 'ひこうき', 'english': 'airplane', 'jlpt': 'N5'},
        {'japanese': '機会', 'hiragana': 'きかい', 'english': 'opportunity', 'jlpt': 'N3'},
    ],
    '汚': [
        {'japanese': '汚い', 'hiragana': 'きたない', 'english': 'dirty', 'jlpt': 'N5'},
        {'japanese': '汚れる', 'hiragana': 'よごれる', 'english': 'to get dirty', 'jlpt': 'N3'},
        {'japanese': '汚す', 'hiragana': 'よごす', 'english': 'to make dirty', 'jlpt': 'N3'},
    ],
    '油': [
        {'japanese': '油', 'hiragana': 'あぶら', 'english': 'oil', 'jlpt': 'N4'},
        {'japanese': '石油', 'hiragana': 'せきゆ', 'english': 'petroleum', 'jlpt': 'N3'},
        {'japanese': '醤油', 'hiragana': 'しょうゆ', 'english': 'soy sauce', 'jlpt': 'N5'},
    ],
    '準': [
        {'japanese': '準備', 'hiragana': 'じゅんび', 'english': 'preparation', 'jlpt': 'N4'},
        {'japanese': '基準', 'hiragana': 'きじゅん', 'english': 'standard', 'jlpt': 'N3'},
        {'japanese': '水準', 'hiragana': 'すいじゅん', 'english': 'level, standard', 'jlpt': 'N3'},
    ],
    '溶': [
        {'japanese': '溶ける', 'hiragana': 'とける', 'english': 'to melt, dissolve', 'jlpt': 'N3'},
        {'japanese': '溶かす', 'hiragana': 'とかす', 'english': 'to melt (something)', 'jlpt': 'N3'},
        {'japanese': '溶液', 'hiragana': 'ようえき', 'english': 'solution (chemistry)', 'jlpt': 'N2'},
    ],
    '炒': [
        {'japanese': '炒める', 'hiragana': 'いためる', 'english': 'to stir-fry', 'jlpt': 'N3'},
        {'japanese': '炒め物', 'hiragana': 'いためもの', 'english': 'stir-fried dish', 'jlpt': 'N3'},
        {'japanese': '炒飯', 'hiragana': 'チャーハン', 'english': 'fried rice', 'jlpt': 'N3'},
    ],
    '焼': [
        {'japanese': '焼く', 'hiragana': 'やく', 'english': 'to bake, grill', 'jlpt': 'N5'},
        {'japanese': '焼ける', 'hiragana': 'やける', 'english': 'to be baked', 'jlpt': 'N4'},
        {'japanese': '焼き鳥', 'hiragana': 'やきとり', 'english': 'grilled chicken', 'jlpt': 'N4'},
    ],
    '片': [
        {'japanese': '片方', 'hiragana': 'かたほう', 'english': 'one side', 'jlpt': 'N4'},
        {'japanese': '片付ける', 'hiragana': 'かたづける', 'english': 'to tidy up', 'jlpt': 'N5'},
        {'japanese': '片道', 'hiragana': 'かたみち', 'english': 'one way', 'jlpt': 'N4'},
    ],
    '皮': [
        {'japanese': '皮', 'hiragana': 'かわ', 'english': 'skin, peel', 'jlpt': 'N3'},
        {'japanese': '革', 'hiragana': 'かわ', 'english': 'leather', 'jlpt': 'N3'},
        {'japanese': '皮膚', 'hiragana': 'ひふ', 'english': 'skin (body)', 'jlpt': 'N3'},
    ],
    '磨': [
        {'japanese': '磨く', 'hiragana': 'みがく', 'english': 'to polish, brush', 'jlpt': 'N3'},
        {'japanese': '研磨', 'hiragana': 'けんま', 'english': 'polishing', 'jlpt': 'N2'},
        {'japanese': '歯磨き', 'hiragana': 'はみがき', 'english': 'tooth brushing', 'jlpt': 'N4'},
    ],
    '笑': [
        {'japanese': '笑う', 'hiragana': 'わらう', 'english': 'to laugh', 'jlpt': 'N5'},
        {'japanese': '笑顔', 'hiragana': 'えがお', 'english': 'smiling face', 'jlpt': 'N3'},
        {'japanese': '微笑む', 'hiragana': 'ほほえむ', 'english': 'to smile', 'jlpt': 'N3'},
    ],
    '箱': [
        {'japanese': '箱', 'hiragana': 'はこ', 'english': 'box', 'jlpt': 'N5'},
        {'japanese': '郵便箱', 'hiragana': 'ゆうびんばこ', 'english': 'mailbox', 'jlpt': 'N4'},
        {'japanese': 'ゴミ箱', 'hiragana': 'ごみばこ', 'english': 'trash can', 'jlpt': 'N4'},
    ],
    '粉': [
        {'japanese': '粉', 'hiragana': 'こな', 'english': 'powder, flour', 'jlpt': 'N3'},
        {'japanese': '小麦粉', 'hiragana': 'こむぎこ', 'english': 'flour', 'jlpt': 'N3'},
        {'japanese': '粉末', 'hiragana': 'ふんまつ', 'english': 'powder', 'jlpt': 'N2'},
    ],
    '統': [
        {'japanese': '統一', 'hiragana': 'とういつ', 'english': 'unification', 'jlpt': 'N3'},
        {'japanese': '伝統', 'hiragana': 'でんとう', 'english': 'tradition', 'jlpt': 'N3'},
        {'japanese': '統計', 'hiragana': 'とうけい', 'english': 'statistics', 'jlpt': 'N2'},
    ],
    '肉': [
        {'japanese': '肉', 'hiragana': 'にく', 'english': 'meat', 'jlpt': 'N5'},
        {'japanese': '牛肉', 'hiragana': 'ぎゅうにく', 'english': 'beef', 'jlpt': 'N5'},
        {'japanese': '肉体', 'hiragana': 'にくたい', 'english': 'body, flesh', 'jlpt': 'N3'},
    ],
    '良': [
        {'japanese': '良い', 'hiragana': 'よい', 'english': 'good', 'jlpt': 'N5'},
        {'japanese': '良く', 'hiragana': 'よく', 'english': 'well, often', 'jlpt': 'N5'},
        {'japanese': '改良', 'hiragana': 'かいりょう', 'english': 'improvement', 'jlpt': 'N3'},
    ],
    '草': [
        {'japanese': '草', 'hiragana': 'くさ', 'english': 'grass', 'jlpt': 'N4'},
        {'japanese': '雑草', 'hiragana': 'ざっそう', 'english': 'weed', 'jlpt': 'N2'},
        {'japanese': '草花', 'hiragana': 'くさばな', 'english': 'flowering plant', 'jlpt': 'N3'},
    ],
    '落': [
        {'japanese': '落ちる', 'hiragana': 'おちる', 'english': 'to fall', 'jlpt': 'N4'},
        {'japanese': '落とす', 'hiragana': 'おとす', 'english': 'to drop', 'jlpt': 'N4'},
        {'japanese': '落ち着く', 'hiragana': 'おちつく', 'english': 'to calm down', 'jlpt': 'N3'},
    ],
    '葉': [
        {'japanese': '葉', 'hiragana': 'は', 'english': 'leaf', 'jlpt': 'N3'},
        {'japanese': '言葉', 'hiragana': 'ことば', 'english': 'word, language', 'jlpt': 'N5'},
        {'japanese': '葉っぱ', 'hiragana': 'はっぱ', 'english': 'leaf (casual)', 'jlpt': 'N3'},
    ],
    '薄': [
        {'japanese': '薄い', 'hiragana': 'うすい', 'english': 'thin', 'jlpt': 'N4'},
        {'japanese': '薄暗い', 'hiragana': 'うすぐらい', 'english': 'dim, gloomy', 'jlpt': 'N3'},
        {'japanese': '薄れる', 'hiragana': 'うすれる', 'english': 'to fade', 'jlpt': 'N3'},
    ],
    '衣': [
        {'japanese': '衣服', 'hiragana': 'いふく', 'english': 'clothing', 'jlpt': 'N3'},
        {'japanese': '衣類', 'hiragana': 'いるい', 'english': 'clothes', 'jlpt': 'N3'},
        {'japanese': '浴衣', 'hiragana': 'ゆかた', 'english': 'yukata', 'jlpt': 'N4'},
    ],
    '袋': [
        {'japanese': '袋', 'hiragana': 'ふくろ', 'english': 'bag', 'jlpt': 'N4'},
        {'japanese': 'ビニール袋', 'hiragana': 'びにーるぶくろ', 'english': 'plastic bag', 'jlpt': 'N4'},
        {'japanese': '紙袋', 'hiragana': 'かみぶくろ', 'english': 'paper bag', 'jlpt': 'N4'},
    ],
    '説': [
        {'japanese': '説明', 'hiragana': 'せつめい', 'english': 'explanation', 'jlpt': 'N4'},
        {'japanese': '小説', 'hiragana': 'しょうせつ', 'english': 'novel', 'jlpt': 'N4'},
        {'japanese': '伝説', 'hiragana': 'でんせつ', 'english': 'legend', 'jlpt': 'N3'},
    ],
    '軽': [
        {'japanese': '軽い', 'hiragana': 'かるい', 'english': 'light (weight)', 'jlpt': 'N4'},
        {'japanese': '軽く', 'hiragana': 'かるく', 'english': 'lightly', 'jlpt': 'N3'},
        {'japanese': '手軽', 'hiragana': 'てがる', 'english': 'easy, simple', 'jlpt': 'N3'},
    ],
    '適': [
        {'japanese': '適当', 'hiragana': 'てきとう', 'english': 'suitable, random', 'jlpt': 'N3'},
        {'japanese': '適切', 'hiragana': 'てきせつ', 'english': 'appropriate', 'jlpt': 'N3'},
        {'japanese': '適用', 'hiragana': 'てきよう', 'english': 'application', 'jlpt': 'N2'},
    ],
    '関': [
        {'japanese': '関係', 'hiragana': 'かんけい', 'english': 'relationship', 'jlpt': 'N4'},
        {'japanese': '関心', 'hiragana': 'かんしん', 'english': 'interest, concern', 'jlpt': 'N3'},
        {'japanese': '関する', 'hiragana': 'かんする', 'english': 'to concern', 'jlpt': 'N4'},
    ],
    '除': [
        {'japanese': '除く', 'hiragana': 'のぞく', 'english': 'to exclude', 'jlpt': 'N3'},
        {'japanese': '掃除', 'hiragana': 'そうじ', 'english': 'cleaning', 'jlpt': 'N5'},
        {'japanese': '除去', 'hiragana': 'じょきょ', 'english': 'removal', 'jlpt': 'N2'},
    ],
    '雑': [
        {'japanese': '雑誌', 'hiragana': 'ざっし', 'english': 'magazine', 'jlpt': 'N5'},
        {'japanese': '雑音', 'hiragana': 'ざつおん', 'english': 'noise', 'jlpt': 'N3'},
        {'japanese': '複雑', 'hiragana': 'ふくざつ', 'english': 'complex', 'jlpt': 'N3'},
    ],
    '静': [
        {'japanese': '静か', 'hiragana': 'しずか', 'english': 'quiet', 'jlpt': 'N5'},
        {'japanese': '静まる', 'hiragana': 'しずまる', 'english': 'to become quiet', 'jlpt': 'N3'},
        {'japanese': '冷静', 'hiragana': 'れいせい', 'english': 'calm, composed', 'jlpt': 'N3'},
    ],
}

def add_n3_vocabulary():
    """Add example vocabulary for N3 kanji"""

    # Load current data
    with open('temp/kanji_with_jlpt_complete.json', 'r', encoding='utf-8') as f:
        kanji_data = json.load(f)

    # Add words to N3 kanji
    n3_count = 0
    word_count = 0

    for char, words in N3_VOCABULARY.items():
        if char in kanji_data and kanji_data[char].get('jlpt') == 'N3':
            kanji_data[char]['words'] = words
            n3_count += 1
            word_count += len(words)

    # Save updated data
    with open('temp/kanji_with_jlpt_complete.json', 'w', encoding='utf-8') as f:
        json.dump(kanji_data, f, ensure_ascii=False, indent=2)

    print(f"Task 1.3 - Batch 3: N3 Kanji Vocabulary Generation")
    print("=" * 60)
    print(f"\n✅ Batch 3 Complete!")
    print(f"   N3 Kanji processed: {n3_count}")
    print(f"   Total words added: {word_count}")
    print(f"\n💾 Saved to: temp/kanji_with_jlpt_complete.json")
    print(f"\n✅ All {n3_count} N3 kanji now have example words!")

if __name__ == '__main__':
    add_n3_vocabulary()
