#!/usr/bin/env python3
"""
Task 1.4 - Batch 2: Add Example Sentences for N4 Kanji
Generate 1 example sentence for each N4 kanji (49 sentences)
"""

import json

# Complete N4 example sentences (49 kanji × 1 sentence each = 49 total)
N4_SENTENCES = {
    '並': {
        'japanese': '本を棚に並べてください。',
        'hiragana': 'ほんをたなにならべてください。',
        'romaji': 'Hon wo tana ni narabete kudasai.',
        'english': 'Please arrange the books on the shelf.'
    },
    '乾': {
        'japanese': '洗濯物がよく乾きました。',
        'hiragana': 'せんたくものがよくかわきました。',
        'romaji': 'Sentakumono ga yoku kawakimashita.',
        'english': 'The laundry dried well.'
    },
    '事': {
        'japanese': '大事なことを忘れました。',
        'hiragana': 'だいじなことをわすれました。',
        'romaji': 'Daiji na koto wo wasuremashita.',
        'english': 'I forgot something important.'
    },
    '仕': {
        'japanese': '父は仕事が忙しいです。',
        'hiragana': 'ちちはしごとがいそがしいです。',
        'romaji': 'Chichi wa shigoto ga isogashii desu.',
        'english': 'My father is busy with work.'
    },
    '作': {
        'japanese': '母が夕食を作っています。',
        'hiragana': 'ははがゆうしょくをつくっています。',
        'romaji': 'Haha ga yuushoku wo tsukutte imasu.',
        'english': 'My mother is making dinner.'
    },
    '供': {
        'japanese': '子供の部屋を掃除しました。',
        'hiragana': 'こどものへやをそうじしました。',
        'romaji': 'Kodomo no heya wo souji shimashita.',
        'english': 'I cleaned the children\'s room.'
    },
    '全': {
        'japanese': '全部きれいにしましょう。',
        'hiragana': 'ぜんぶきれいにしましょう。',
        'romaji': 'Zenbu kirei ni shimashou.',
        'english': 'Let\'s clean everything.'
    },
    '切': {
        'japanese': '野菜を小さく切ります。',
        'hiragana': 'やさいをちいさくきります。',
        'romaji': 'Yasai wo chiisaku kirimasu.',
        'english': 'I cut the vegetables small.'
    },
    '力': {
        'japanese': '力を合わせて頑張りましょう。',
        'hiragana': 'ちからをあわせてがんばりましょう。',
        'romaji': 'Chikara wo awasete ganbarimarou.',
        'english': 'Let\'s work hard together.'
    },
    '台': {
        'japanese': '台所で料理を作ります。',
        'hiragana': 'だいどころでりょうりをつくります。',
        'romaji': 'Daidokoro de ryouri wo tsukurimasu.',
        'english': 'I make food in the kitchen.'
    },
    '味': {
        'japanese': 'この料理は味が美味しいです。',
        'hiragana': 'このりょうりはあじがおいしいです。',
        'romaji': 'Kono ryouri wa aji ga oishii desu.',
        'english': 'This dish tastes delicious.'
    },
    '員': {
        'japanese': '家族全員で食事をします。',
        'hiragana': 'かぞくぜんいんでしょくじをします。',
        'romaji': 'Kazoku zenin de shokuji wo shimasu.',
        'english': 'The whole family eats together.'
    },
    '声': {
        'japanese': '大きい声で話さないでください。',
        'hiragana': 'おおきいこえではなさないでください。',
        'romaji': 'Ookii koe de hanasanai de kudasai.',
        'english': 'Please don\'t speak in a loud voice.'
    },
    '夕': {
        'japanese': '夕方に買い物に行きます。',
        'hiragana': 'ゆうがたにかいものにいきます。',
        'romaji': 'Yuugata ni kaimono ni ikimasu.',
        'english': 'I go shopping in the evening.'
    },
    '始': {
        'japanese': '授業は９時に始まります。',
        'hiragana': 'じゅぎょうはくじにはじまります。',
        'romaji': 'Jugyou wa ku-ji ni hajimarimasu.',
        'english': 'Class begins at 9 o\'clock.'
    },
    '家': {
        'japanese': '家族で旅行に行きたいです。',
        'hiragana': 'かぞくでりょこうにいきたいです。',
        'romaji': 'Kazoku de ryokou ni ikitai desu.',
        'english': 'I want to go on a trip with my family.'
    },
    '寝': {
        'japanese': '昨夜は１０時に寝ました。',
        'hiragana': 'さくやはじゅうじにねました。',
        'romaji': 'Sakuya wa juu-ji ni nemashita.',
        'english': 'I went to bed at 10 o\'clock last night.'
    },
    '屋': {
        'japanese': '部屋の窓を開けましょう。',
        'hiragana': 'へやのまどをあけましょう。',
        'romaji': 'Heya no mado wo akemashou.',
        'english': 'Let\'s open the room\'s window.'
    },
    '度': {
        'japanese': '今日の温度は２０度です。',
        'hiragana': 'きょうのおんどはにじゅうどです。',
        'romaji': 'Kyou no ondo wa nijuu-do desu.',
        'english': 'Today\'s temperature is 20 degrees.'
    },
    '庭': {
        'japanese': '庭の花に水をあげます。',
        'hiragana': 'にわのはなにみずをあげます。',
        'romaji': 'Niwa no hana ni mizu wo agemasu.',
        'english': 'I water the flowers in the garden.'
    },
    '息': {
        'japanese': '息子は毎日学校へ行きます。',
        'hiragana': 'むすこはまいにちがっこうへいきます。',
        'romaji': 'Musuko wa mainichi gakkou e ikimasu.',
        'english': 'My son goes to school every day.'
    },
    '意': {
        'japanese': 'この言葉の意味が分かりません。',
        'hiragana': 'このことばのいみがわかりません。',
        'romaji': 'Kono kotoba no imi ga wakarimasen.',
        'english': 'I don\'t understand the meaning of this word.'
    },
    '所': {
        'japanese': 'ここは静かな所ですね。',
        'hiragana': 'ここはしずかなところですね。',
        'romaji': 'Koko wa shizuka na tokoro desu ne.',
        'english': 'This is a quiet place, isn\'t it?'
    },
    '持': {
        'japanese': '鍵を持って出かけてください。',
        'hiragana': 'かぎをもってでかけてください。',
        'romaji': 'Kagi wo motte dekakete kudasai.',
        'english': 'Please take the key when you go out.'
    },
    '教': {
        'japanese': '先生が漢字を教えてくれました。',
        'hiragana': 'せんせいがかんじをおしえてくれました。',
        'romaji': 'Sensei ga kanji wo oshiete kuremashita.',
        'english': 'The teacher taught me kanji.'
    },
    '料': {
        'japanese': '今晩は魚料理を作ります。',
        'hiragana': 'こんばんはさかなりょうりをつくります。',
        'romaji': 'Konban wa sakana ryouri wo tsukurimasu.',
        'english': 'I\'m making fish dishes tonight.'
    },
    '族': {
        'japanese': '私の家族は四人です。',
        'hiragana': 'わたしのかぞくはよにんです。',
        'romaji': 'Watashi no kazoku wa yo-nin desu.',
        'english': 'My family is four people.'
    },
    '机': {
        'japanese': '机の上を片付けてください。',
        'hiragana': 'つくえのうえをかたづけてください。',
        'romaji': 'Tsukue no ue wo katadzukete kudasai.',
        'english': 'Please tidy up the top of the desk.'
    },
    '楽': {
        'japanese': '音楽を聴くのが楽しいです。',
        'hiragana': 'おんがくをきくのがたのしいです。',
        'romaji': 'Ongaku wo kiku no ga tanoshii desu.',
        'english': 'Listening to music is fun.'
    },
    '汁': {
        'japanese': '朝は味噌汁を飲みます。',
        'hiragana': 'あさはみそしるをのみます。',
        'romaji': 'Asa wa misoshiru wo nomimasu.',
        'english': 'I drink miso soup in the morning.'
    },
    '洗': {
        'japanese': '食事の後で皿を洗います。',
        'hiragana': 'しょくじのあとでさらをあらいます。',
        'romaji': 'Shokuji no ato de sara wo araimasu.',
        'english': 'I wash the dishes after meals.'
    },
    '温': {
        'japanese': 'お風呂の温度がちょうどいいです。',
        'hiragana': 'おふろのおんどがちょうどいいです。',
        'romaji': 'Ofuro no ondo ga choudo ii desu.',
        'english': 'The bath temperature is just right.'
    },
    '満': {
        'japanese': '結果に満足しています。',
        'hiragana': 'けっかにまんぞくしています。',
        'romaji': 'Kekka ni manzoku shite imasu.',
        'english': 'I\'m satisfied with the results.'
    },
    '牛': {
        'japanese': '朝ごはんに牛乳を飲みます。',
        'hiragana': 'あさごはんにぎゅうにゅうをのみます。',
        'romaji': 'Asa-gohan ni gyuunyuu wo nomimasu.',
        'english': 'I drink milk for breakfast.'
    },
    '理': {
        'japanese': '母の料理が一番美味しいです。',
        'hiragana': 'ははのりょうりがいちばんおいしいです。',
        'romaji': 'Haha no ryouri ga ichiban oishii desu.',
        'english': 'My mother\'s cooking is the most delicious.'
    },
    '用': {
        'japanese': '明日は用事があります。',
        'hiragana': 'あしたはようじがあります。',
        'romaji': 'Ashita wa youji ga arimasu.',
        'english': 'I have errands tomorrow.'
    },
    '的': {
        'japanese': '目的地に着きました。',
        'hiragana': 'もくてきちにつきました。',
        'romaji': 'Mokutekichi ni tsukimashita.',
        'english': 'We arrived at our destination.'
    },
    '着': {
        'japanese': '新しい服を着ています。',
        'hiragana': 'あたらしいふくをきています。',
        'romaji': 'Atarashii fuku wo kite imasu.',
        'english': 'I\'m wearing new clothes.'
    },
    '脱': {
        'japanese': '玄関で靴を脱いでください。',
        'hiragana': 'げんかんでくつをぬいでください。',
        'romaji': 'Genkan de kutsu wo nuide kudasai.',
        'english': 'Please take off your shoes at the entrance.'
    },
    '茶': {
        'japanese': '午後にお茶を飲みましょう。',
        'hiragana': 'ごごにおちゃをのみましょう。',
        'romaji': 'Gogo ni ocha wo nomimashou.',
        'english': 'Let\'s drink tea in the afternoon.'
    },
    '菜': {
        'japanese': '野菜をたくさん食べてください。',
        'hiragana': 'やさいをたくさんたべてください。',
        'romaji': 'Yasai wo takusan tabete kudasai.',
        'english': 'Please eat lots of vegetables.'
    },
    '計': {
        'japanese': '時計が止まっています。',
        'hiragana': 'とけいがとまっています。',
        'romaji': 'Tokei ga tomatte imasu.',
        'english': 'The clock has stopped.'
    },
    '起': {
        'japanese': '毎朝６時に起きます。',
        'hiragana': 'まいあさろくじにおきます。',
        'romaji': 'Maiasa roku-ji ni okimasu.',
        'english': 'I wake up at 6 o\'clock every morning.'
    },
    '部': {
        'japanese': 'この部分が難しいです。',
        'hiragana': 'このぶぶんがむずかしいです。',
        'romaji': 'Kono bubun ga muzukashii desu.',
        'english': 'This part is difficult.'
    },
    '重': {
        'japanese': 'この荷物は重いですね。',
        'hiragana': 'このにもつはおもいですね。',
        'romaji': 'Kono nimotsu wa omoi desu ne.',
        'english': 'This luggage is heavy, isn\'t it?'
    },
    '野': {
        'japanese': '野菜と魚を買いました。',
        'hiragana': 'やさいとさかなをかいました。',
        'romaji': 'Yasai to sakana wo kaimashita.',
        'english': 'I bought vegetables and fish.'
    },
    '開': {
        'japanese': '窓を開けてもいいですか。',
        'hiragana': 'まどをあけてもいいですか。',
        'romaji': 'Mado wo akete mo ii desu ka.',
        'english': 'May I open the window?'
    },
    '集': {
        'japanese': '友達が家に集まりました。',
        'hiragana': 'ともだちがいえにあつまりました。',
        'romaji': 'Tomodachi ga ie ni atsumarimashita.',
        'english': 'Friends gathered at my house.'
    },
    '風': {
        'japanese': '夜にお風呂に入ります。',
        'hiragana': 'よるにおふろにはいります。',
        'romaji': 'Yoru ni ofuro ni hairimasu.',
        'english': 'I take a bath at night.'
    },
}

def add_n4_sentences():
    """Add example sentences for N4 kanji"""

    # Load current data
    with open('temp/kanji_with_jlpt_complete.json', 'r', encoding='utf-8') as f:
        kanji_data = json.load(f)

    # Add sentences to N4 kanji
    n4_count = 0
    sentence_count = 0

    for char, sentence in N4_SENTENCES.items():
        if char in kanji_data and kanji_data[char].get('jlpt') == 'N4':
            kanji_data[char]['sentence'] = sentence
            n4_count += 1
            sentence_count += 1

    # Save updated data
    with open('temp/kanji_with_jlpt_complete.json', 'w', encoding='utf-8') as f:
        json.dump(kanji_data, f, ensure_ascii=False, indent=2)

    print(f"Task 1.4 - Batch 2: N4 Kanji Example Sentences")
    print("=" * 60)
    print(f"\n✅ Batch 2 Complete!")
    print(f"   N4 Kanji processed: {n4_count}")
    print(f"   Total sentences added: {sentence_count}")
    print(f"\n💾 Saved to: temp/kanji_with_jlpt_complete.json")
    print(f"\n✅ All {n4_count} N4 kanji now have example sentences!")

if __name__ == '__main__':
    add_n4_sentences()
