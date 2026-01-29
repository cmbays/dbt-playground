#!/usr/bin/env python3
"""
Task 1.4 - Batch 3: Add Example Sentences for N3 Kanji
Generate 1 example sentence for each N3 kanji (52 sentences)
"""

import json

# Complete N3 example sentences (52 kanji × 1 sentence each = 52 total)
N3_SENTENCES = {
    '丁': {
        'japanese': '包丁で野菜を切ります。',
        'hiragana': 'ほうちょうでやさいをきります。',
        'romaji': 'Houchou de yasai wo kirimasu.',
        'english': 'I cut vegetables with a kitchen knife.'
    },
    '付': {
        'japanese': 'メモを冷蔵庫に付けました。',
        'hiragana': 'めもをれいぞうこにつけました。',
        'romaji': 'Memo wo reizouko ni tsukemashita.',
        'english': 'I attached a memo to the refrigerator.'
    },
    '伝': {
        'japanese': '母に伝言を伝えてください。',
        'hiragana': 'ははにでんごんをつたえてください。',
        'romaji': 'Haha ni dengon wo tsutaete kudasai.',
        'english': 'Please convey the message to my mother.'
    },
    '備': {
        'japanese': '明日の準備をしています。',
        'hiragana': 'あしたのじゅんびをしています。',
        'romaji': 'Ashita no junbi wo shite imasu.',
        'english': 'I\'m preparing for tomorrow.'
    },
    '冷': {
        'japanese': '冷蔵庫に食べ物を入れます。',
        'hiragana': 'れいぞうこにたべものをいれます。',
        'romaji': 'Reizouko ni tabemono wo iremasu.',
        'english': 'I put food in the refrigerator.'
    },
    '初': {
        'japanese': '初めてこの料理を作りました。',
        'hiragana': 'はじめてこのりょうりをつくりました。',
        'romaji': 'Hajimete kono ryouri wo tsukurimashita.',
        'english': 'I made this dish for the first time.'
    },
    '加': {
        'japanese': '料理に塩を加えます。',
        'hiragana': 'りょうりにしおをくわえます。',
        'romaji': 'Ryouri ni shio wo kuwaemasu.',
        'english': 'I add salt to the dish.'
    },
    '協': {
        'japanese': '家族で協力して掃除します。',
        'hiragana': 'かぞくできょうりょくしてそうじします。',
        'romaji': 'Kazoku de kyouryoku shite souji shimasu.',
        'english': 'The family cooperates to clean.'
    },
    '器': {
        'japanese': '食器を洗って棚に戻します。',
        'hiragana': 'しょっきをあらってたなにもどします。',
        'romaji': 'Shokki wo aratte tana ni modoshimasu.',
        'english': 'I wash the dishes and put them back on the shelf.'
    },
    '娘': {
        'japanese': '娘は部屋で宿題をしています。',
        'hiragana': 'むすめはへやでしゅくだいをしています。',
        'romaji': 'Musume wa heya de shukudai wo shite imasu.',
        'english': 'My daughter is doing homework in her room.'
    },
    '居': {
        'japanese': '居間でテレビを見ます。',
        'hiragana': 'いまでてれびをみます。',
        'romaji': 'Ima de terebi wo mimasu.',
        'english': 'I watch TV in the living room.'
    },
    '弁': {
        'japanese': 'お弁当を作って持って行きます。',
        'hiragana': 'おべんとうをつくってもっていきます。',
        'romaji': 'Obentou wo tsukutte motte ikimasu.',
        'english': 'I make a boxed lunch and take it with me.'
    },
    '当': {
        'japanese': '本当にきれいな庭ですね。',
        'hiragana': 'ほんとうにきれいなにわですね。',
        'romaji': 'Hontou ni kirei na niwa desu ne.',
        'english': 'It\'s a really beautiful garden, isn\'t it?'
    },
    '抜': {
        'japanese': 'コンセントを抜いてください。',
        'hiragana': 'こんせんとをぬいてください。',
        'romaji': 'Konsento wo nuite kudasai.',
        'english': 'Please unplug the outlet.'
    },
    '担': {
        'japanese': '今週は私が料理を担当します。',
        'hiragana': 'こんしゅうはわたしがりょうりをたんとうします。',
        'romaji': 'Konshuu wa watashi ga ryouri wo tantou shimasu.',
        'english': 'I\'m in charge of cooking this week.'
    },
    '拭': {
        'japanese': 'テーブルを布で拭きます。',
        'hiragana': 'てーぶるをぬのでふきます。',
        'romaji': 'Teeburu wo nuno de fukimasu.',
        'english': 'I wipe the table with a cloth.'
    },
    '捨': {
        'japanese': 'ゴミを捨てに行きましょう。',
        'hiragana': 'ごみをすてにいきましょう。',
        'romaji': 'Gomi wo sute ni ikimashou.',
        'english': 'Let\'s go throw away the garbage.'
    },
    '揚': {
        'japanese': '夕食に鶏肉を揚げます。',
        'hiragana': 'ゆうしょくにとりにくをあげます。',
        'romaji': 'Yuushoku ni toriniku wo agemasu.',
        'english': 'I\'m frying chicken for dinner.'
    },
    '整': {
        'japanese': '部屋を整理整頓しましょう。',
        'hiragana': 'へやをせいりせいとんしましょう。',
        'romaji': 'Heya wo seiri seiton shimashou.',
        'english': 'Let\'s organize and tidy up the room.'
    },
    '替': {
        'japanese': '電球を新しいのに替えました。',
        'hiragana': 'でんきゅうをあたらしいのにかえました。',
        'romaji': 'Denkyuu wo atarashii no ni kaemashita.',
        'english': 'I replaced the light bulb with a new one.'
    },
    '最': {
        'japanese': '最近忙しくなりました。',
        'hiragana': 'さいきんいそがしくなりました。',
        'romaji': 'Saikin isogashiku narimashita.',
        'english': 'I\'ve become busy recently.'
    },
    '材': {
        'japanese': '料理の材料を買いました。',
        'hiragana': 'りょうりのざいりょうをかいました。',
        'romaji': 'Ryouri no zairyou wo kaimashita.',
        'english': 'I bought ingredients for cooking.'
    },
    '柔': {
        'japanese': 'この肉は柔らかくて美味しいです。',
        'hiragana': 'このにくはやわらかくておいしいです。',
        'romaji': 'Kono niku wa yawarakakute oishii desu.',
        'english': 'This meat is soft and delicious.'
    },
    '機': {
        'japanese': '洗濯機が壊れてしまいました。',
        'hiragana': 'せんたくきがこわれてしまいました。',
        'romaji': 'Sentakuki ga kowarete shimaimashita.',
        'english': 'The washing machine broke.'
    },
    '汚': {
        'japanese': '部屋が汚れているので掃除します。',
        'hiragana': 'へやがよごれているのでそうじします。',
        'romaji': 'Heya ga yogorete iru node souji shimasu.',
        'english': 'I\'ll clean because the room is dirty.'
    },
    '油': {
        'japanese': 'フライパンに油を入れます。',
        'hiragana': 'ふらいぱんにあぶらをいれます。',
        'romaji': 'Furaipan ni abura wo iremasu.',
        'english': 'I put oil in the frying pan.'
    },
    '準': {
        'japanese': '朝食の準備ができました。',
        'hiragana': 'ちょうしょくのじゅんびができました。',
        'romaji': 'Choushoku no junbi ga dekimashita.',
        'english': 'Breakfast preparation is done.'
    },
    '溶': {
        'japanese': '砂糖が水に溶けました。',
        'hiragana': 'さとうがみずにとけました。',
        'romaji': 'Satou ga mizu ni tokemashita.',
        'english': 'The sugar dissolved in the water.'
    },
    '炒': {
        'japanese': '野菜を炒めて食べます。',
        'hiragana': 'やさいをいためてたべます。',
        'romaji': 'Yasai wo itamete tabemasu.',
        'english': 'I stir-fry vegetables and eat them.'
    },
    '焼': {
        'japanese': 'パンを焼いて朝食にします。',
        'hiragana': 'ぱんをやいてちょうしょくにします。',
        'romaji': 'Pan wo yaite choushoku ni shimasu.',
        'english': 'I toast bread for breakfast.'
    },
    '片': {
        'japanese': '食事の後で片付けます。',
        'hiragana': 'しょくじのあとでかたづけます。',
        'romaji': 'Shokuji no ato de katadzukemasu.',
        'english': 'I tidy up after meals.'
    },
    '皮': {
        'japanese': 'リンゴの皮をむいてください。',
        'hiragana': 'りんごのかわをむいてください。',
        'romaji': 'Ringo no kawa wo muite kudasai.',
        'english': 'Please peel the apple skin.'
    },
    '磨': {
        'japanese': '毎晩歯を磨きます。',
        'hiragana': 'まいばんはをみがきます。',
        'romaji': 'Maiban ha wo migakimasu.',
        'english': 'I brush my teeth every night.'
    },
    '笑': {
        'japanese': '家族で笑いながら食事をします。',
        'hiragana': 'かぞくでわらいながらしょくじをします。',
        'romaji': 'Kazoku de warai nagara shokuji wo shimasu.',
        'english': 'We eat meals while laughing with family.'
    },
    '箱': {
        'japanese': '箱の中に本を入れました。',
        'hiragana': 'はこのなかにほんをいれました。',
        'romaji': 'Hako no naka ni hon wo iremashita.',
        'english': 'I put books in the box.'
    },
    '粉': {
        'japanese': '小麦粉でパンを作ります。',
        'hiragana': 'こむぎこでぱんをつくります。',
        'romaji': 'Komugiko de pan wo tsukurimasu.',
        'english': 'I make bread with flour.'
    },
    '統': {
        'japanese': '我が家の伝統料理です。',
        'hiragana': 'わがやのでんとうりょうりです。',
        'romaji': 'Wagaya no dentou ryouri desu.',
        'english': 'It\'s our family\'s traditional dish.'
    },
    '肉': {
        'japanese': '今日は肉を買って帰ります。',
        'hiragana': 'きょうはにくをかってかえります。',
        'romaji': 'Kyou wa niku wo katte kaerimasu.',
        'english': 'I\'ll buy meat and go home today.'
    },
    '良': {
        'japanese': '良い天気なので洗濯します。',
        'hiragana': 'よいてんきなのでせんたくします。',
        'romaji': 'Yoi tenki nanode sentaku shimasu.',
        'english': 'I\'ll do laundry because the weather is good.'
    },
    '草': {
        'japanese': '庭の草を抜きました。',
        'hiragana': 'にわのくさをぬきました。',
        'romaji': 'Niwa no kusa wo nukimashita.',
        'english': 'I pulled the grass in the garden.'
    },
    '落': {
        'japanese': '葉が地面に落ちました。',
        'hiragana': 'はがじめんにおちました。',
        'romaji': 'Ha ga jimen ni ochimashita.',
        'english': 'The leaves fell to the ground.'
    },
    '葉': {
        'japanese': '木の葉が色づいています。',
        'hiragana': 'きのはがいろづいています。',
        'romaji': 'Ki no ha ga irozuite imasu.',
        'english': 'The tree leaves are changing color.'
    },
    '薄': {
        'japanese': 'この紙は薄いので注意してください。',
        'hiragana': 'このかみはうすいのでちゅういしてください。',
        'romaji': 'Kono kami wa usui node chuui shite kudasai.',
        'english': 'Please be careful because this paper is thin.'
    },
    '衣': {
        'japanese': '衣類を洗濯機に入れます。',
        'hiragana': 'いるいをせんたくきにいれます。',
        'romaji': 'Irui wo sentakuki ni iremasu.',
        'english': 'I put clothes in the washing machine.'
    },
    '袋': {
        'japanese': 'ゴミ袋を買いに行きます。',
        'hiragana': 'ごみぶくろをかいにいきます。',
        'romaji': 'Gomi bukuro wo kai ni ikimasu.',
        'english': 'I\'m going to buy garbage bags.'
    },
    '説': {
        'japanese': '使い方を説明してください。',
        'hiragana': 'つかいかたをせつめいしてください。',
        'romaji': 'Tsukaikata wo setsumei shite kudasai.',
        'english': 'Please explain how to use it.'
    },
    '軽': {
        'japanese': 'この箱は軽いので持ちやすいです。',
        'hiragana': 'このはこはかるいのでもちやすいです。',
        'romaji': 'Kono hako wa karui node mochiyasui desu.',
        'english': 'This box is light so it\'s easy to carry.'
    },
    '適': {
        'japanese': '適当な温度で調理します。',
        'hiragana': 'てきとうなおんどでちょうりします。',
        'romaji': 'Tekitou na ondo de chouri shimasu.',
        'english': 'I cook at a suitable temperature.'
    },
    '関': {
        'japanese': '玄関の鍵を閉めてください。',
        'hiragana': 'げんかんのかぎをしめてください。',
        'romaji': 'Genkan no kagi wo shimete kudasai.',
        'english': 'Please lock the entrance.'
    },
    '除': {
        'japanese': '毎日掃除機をかけます。',
        'hiragana': 'まいにちそうじきをかけます。',
        'romaji': 'Mainichi soujiki wo kakemasu.',
        'english': 'I vacuum every day.'
    },
    '雑': {
        'japanese': '雑誌を読んでリラックスします。',
        'hiragana': 'ざっしをよんでりらっくすします。',
        'romaji': 'Zasshi wo yonde rirakkusu shimasu.',
        'english': 'I relax by reading magazines.'
    },
    '静': {
        'japanese': '夜は静かに過ごします。',
        'hiragana': 'よるはしずかにすごします。',
        'romaji': 'Yoru wa shizuka ni sugoshimasu.',
        'english': 'I spend the evening quietly.'
    },
}

def add_n3_sentences():
    """Add example sentences for N3 kanji"""

    # Load current data
    with open('temp/kanji_with_jlpt_complete.json', 'r', encoding='utf-8') as f:
        kanji_data = json.load(f)

    # Add sentences to N3 kanji
    n3_count = 0
    sentence_count = 0

    for char, sentence in N3_SENTENCES.items():
        if char in kanji_data and kanji_data[char].get('jlpt') == 'N3':
            kanji_data[char]['sentence'] = sentence
            n3_count += 1
            sentence_count += 1

    # Save updated data
    with open('temp/kanji_with_jlpt_complete.json', 'w', encoding='utf-8') as f:
        json.dump(kanji_data, f, ensure_ascii=False, indent=2)

    print(f"Task 1.4 - Batch 3: N3 Kanji Example Sentences")
    print("=" * 60)
    print(f"\n✅ Batch 3 Complete!")
    print(f"   N3 Kanji processed: {n3_count}")
    print(f"   Total sentences added: {sentence_count}")
    print(f"\n💾 Saved to: temp/kanji_with_jlpt_complete.json")
    print(f"\n✅ All {n3_count} N3 kanji now have example sentences!")

if __name__ == '__main__':
    add_n3_sentences()
