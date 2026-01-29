#!/usr/bin/env python3
"""
Task 1.4 - Batch 1: Add Example Sentences for N5 Kanji
Generate 1 example sentence for each N5 kanji (32 sentences)
"""

import json

# Complete N5 example sentences (32 kanji × 1 sentence each = 32 total)
N5_SENTENCES = {
    '下': {
        'japanese': '本は机の下にあります。',
        'hiragana': 'ほんはつくえのしたにあります。',
        'romaji': 'Hon wa tsukue no shita ni arimasu.',
        'english': 'The book is under the desk.'
    },
    '入': {
        'japanese': '部屋に入ってください。',
        'hiragana': 'へやにはいってください。',
        'romaji': 'Heya ni haitte kudasai.',
        'english': 'Please enter the room.'
    },
    '出': {
        'japanese': '毎朝７時に家を出ます。',
        'hiragana': 'まいあさしちじにいえをでます。',
        'romaji': 'Maiasa shichi-ji ni ie wo demasu.',
        'english': 'I leave home at 7 o\'clock every morning.'
    },
    '前': {
        'japanese': '学校の前で待っています。',
        'hiragana': 'がっこうのまえでまっています。',
        'romaji': 'Gakkou no mae de matte imasu.',
        'english': 'I\'m waiting in front of the school.'
    },
    '午': {
        'japanese': '午後に友達と会います。',
        'hiragana': 'ごごにともだちとあいます。',
        'romaji': 'Gogo ni tomodachi to aimasu.',
        'english': 'I\'m meeting a friend in the afternoon.'
    },
    '土': {
        'japanese': '土曜日は家族と過ごします。',
        'hiragana': 'どようびはかぞくとすごします。',
        'romaji': 'Doyoubi wa kazoku to sugoshimasu.',
        'english': 'I spend Saturdays with my family.'
    },
    '夜': {
        'japanese': '夜は静かに勉強します。',
        'hiragana': 'よるはしずかにべんきょうします。',
        'romaji': 'Yoru wa shizuka ni benkyou shimasu.',
        'english': 'I study quietly at night.'
    },
    '天': {
        'japanese': '今日は天気がいいですね。',
        'hiragana': 'きょうはてんきがいいですね。',
        'romaji': 'Kyou wa tenki ga ii desu ne.',
        'english': 'The weather is nice today, isn\'t it?'
    },
    '女': {
        'japanese': '私の姉は女子大学生です。',
        'hiragana': 'わたしのあねはじょしだいがくせいです。',
        'romaji': 'Watashi no ane wa joshi daigakusei desu.',
        'english': 'My older sister is a female university student.'
    },
    '子': {
        'japanese': '子供たちは庭で遊んでいます。',
        'hiragana': 'こどもたちはにわであそんでいます。',
        'romaji': 'Kodomo-tachi wa niwa de asonde imasu.',
        'english': 'The children are playing in the garden.'
    },
    '学': {
        'japanese': '毎日学校で日本語を学びます。',
        'hiragana': 'まいにちがっこうでにほんごをまなびます。',
        'romaji': 'Mainichi gakkou de nihongo wo manabimasu.',
        'english': 'I learn Japanese at school every day.'
    },
    '帰': {
        'japanese': '６時に家に帰ります。',
        'hiragana': 'ろくじにいえにかえります。',
        'romaji': 'Roku-ji ni ie ni kaerimasu.',
        'english': 'I return home at 6 o\'clock.'
    },
    '後': {
        'japanese': '授業の後で図書館に行きます。',
        'hiragana': 'じゅぎょうのあとでとしょかんにいきます。',
        'romaji': 'Jugyou no ato de toshokan ni ikimasu.',
        'english': 'I go to the library after class.'
    },
    '新': {
        'japanese': '新しい家に引っ越しました。',
        'hiragana': 'あたらしいいえにひっこしました。',
        'romaji': 'Atarashii ie ni hikkoshimashita.',
        'english': 'I moved to a new house.'
    },
    '日': {
        'japanese': '日曜日は家でゆっくりします。',
        'hiragana': 'にちようびはいえでゆっくりします。',
        'romaji': 'Nichiyoubi wa ie de yukkuri shimasu.',
        'english': 'I relax at home on Sundays.'
    },
    '早': {
        'japanese': '毎朝早く起きます。',
        'hiragana': 'まいあさはやくおきます。',
        'romaji': 'Maiasa hayaku okimasu.',
        'english': 'I wake up early every morning.'
    },
    '明': {
        'japanese': '明日は天気が良さそうです。',
        'hiragana': 'あしたはてんきがよさそうです。',
        'romaji': 'Ashita wa tenki ga yosasou desu.',
        'english': 'The weather looks like it will be good tomorrow.'
    },
    '時': {
        'japanese': '時計を見てください。',
        'hiragana': 'とけいをみてください。',
        'romaji': 'Tokei wo mite kudasai.',
        'english': 'Please look at the clock.'
    },
    '曜': {
        'japanese': '今日は何曜日ですか。',
        'hiragana': 'きょうはなんようびですか。',
        'romaji': 'Kyou wa nan-youbi desu ka.',
        'english': 'What day of the week is it today?'
    },
    '朝': {
        'japanese': '朝ごはんを食べましたか。',
        'hiragana': 'あさごはんをたべましたか。',
        'romaji': 'Asa-gohan wo tabemashita ka.',
        'english': 'Did you eat breakfast?'
    },
    '校': {
        'japanese': '学校まで歩いて１５分です。',
        'hiragana': 'がっこうまであるいてじゅうごふんです。',
        'romaji': 'Gakkou made aruite juugo-fun desu.',
        'english': 'It\'s a 15-minute walk to school.'
    },
    '母': {
        'japanese': '母は料理が上手です。',
        'hiragana': 'ははははりょうりがじょうずです。',
        'romaji': 'Haha wa ryouri ga jouzu desu.',
        'english': 'My mother is good at cooking.'
    },
    '気': {
        'japanese': '今日は気分がいいです。',
        'hiragana': 'きょうはきぶんがいいです。',
        'romaji': 'Kyou wa kibun ga ii desu.',
        'english': 'I feel good today.'
    },
    '水': {
        'japanese': '水を一杯ください。',
        'hiragana': 'みずをいっぱいください。',
        'romaji': 'Mizu wo ippai kudasai.',
        'english': 'Please give me a glass of water.'
    },
    '父': {
        'japanese': '父は会社で働いています。',
        'hiragana': 'ちちはかいしゃではたらいています。',
        'romaji': 'Chichi wa kaisha de hataraite imasu.',
        'english': 'My father works at a company.'
    },
    '男': {
        'japanese': '男の子が二人います。',
        'hiragana': 'おとこのこがふたりいます。',
        'romaji': 'Otoko no ko ga futari imasu.',
        'english': 'There are two boys.'
    },
    '花': {
        'japanese': '庭に花が咲いています。',
        'hiragana': 'にわにはながさいています。',
        'romaji': 'Niwa ni hana ga saite imasu.',
        'english': 'Flowers are blooming in the garden.'
    },
    '話': {
        'japanese': '友達と日本語で話します。',
        'hiragana': 'ともだちとにほんごではなします。',
        'romaji': 'Tomodachi to nihongo de hanashimasu.',
        'english': 'I talk with friends in Japanese.'
    },
    '足': {
        'japanese': '足が痛いです。',
        'hiragana': 'あしがいたいです。',
        'romaji': 'Ashi ga itai desu.',
        'english': 'My foot hurts.'
    },
    '長': {
        'japanese': '兄は背が長いです。',
        'hiragana': 'あにはせがながいです。',
        'romaji': 'Ani wa se ga nagai desu.',
        'english': 'My older brother is tall.'
    },
    '間': {
        'japanese': '授業と授業の間に休みます。',
        'hiragana': 'じゅぎょうとじゅぎょうのあいだにやすみます。',
        'romaji': 'Jugyou to jugyou no aida ni yasumimasu.',
        'english': 'I rest between classes.'
    },
    '食': {
        'japanese': '毎日三回食事をします。',
        'hiragana': 'まいにちさんかいしょくじをします。',
        'romaji': 'Mainichi san-kai shokuji wo shimasu.',
        'english': 'I eat three meals every day.'
    },
}

def add_n5_sentences():
    """Add example sentences for N5 kanji"""

    # Load current data
    with open('temp/kanji_with_jlpt_complete.json', 'r', encoding='utf-8') as f:
        kanji_data = json.load(f)

    # Add sentences to N5 kanji
    n5_count = 0
    sentence_count = 0

    for char, sentence in N5_SENTENCES.items():
        if char in kanji_data and kanji_data[char].get('jlpt') == 'N5':
            kanji_data[char]['sentence'] = sentence
            n5_count += 1
            sentence_count += 1

    # Save updated data
    with open('temp/kanji_with_jlpt_complete.json', 'w', encoding='utf-8') as f:
        json.dump(kanji_data, f, ensure_ascii=False, indent=2)

    print(f"Task 1.4 - Batch 1: N5 Kanji Example Sentences")
    print("=" * 60)
    print(f"\n✅ Batch 1 Complete!")
    print(f"   N5 Kanji processed: {n5_count}")
    print(f"   Total sentences added: {sentence_count}")
    print(f"\n💾 Saved to: temp/kanji_with_jlpt_complete.json")
    print(f"\n✅ All {n5_count} N5 kanji now have example sentences!")

if __name__ == '__main__':
    add_n5_sentences()
