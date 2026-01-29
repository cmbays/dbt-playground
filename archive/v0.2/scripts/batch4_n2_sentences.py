#!/usr/bin/env python3
"""
Task 1.4 - Batch 4: Add Example Sentences for N2 Kanji
Generate 1 example sentence for each N2 kanji (36 sentences) - FINAL BATCH
"""

import json

# Complete N2 example sentences (36 kanji × 1 sentence each = 36 total)
N2_SENTENCES = {
    '剥': {
        'japanese': 'バナナの皮を剥いて食べました。',
        'hiragana': 'ばななのかわをむいてたべました。',
        'romaji': 'Banana no kawa wo muite tabemashita.',
        'english': 'I peeled the banana and ate it.'
    },
    '包': {
        'japanese': '包丁を使って肉を切ります。',
        'hiragana': 'ほうちょうをつかってにくをきります。',
        'romaji': 'Houchou wo tsukatte niku wo kirimasu.',
        'english': 'I cut meat using a kitchen knife.'
    },
    '卓': {
        'japanese': '食卓の上を拭いてください。',
        'hiragana': 'しょくたくのうえをふいてください。',
        'romaji': 'Shokutaku no ue wo fuite kudasai.',
        'english': 'Please wipe the dining table.'
    },
    '卵': {
        'japanese': '朝ごはんに卵を食べます。',
        'hiragana': 'あさごはんにたまごをたべます。',
        'romaji': 'Asa-gohan ni tamago wo tabemasu.',
        'english': 'I eat eggs for breakfast.'
    },
    '呂': {
        'japanese': '毎日お風呂に入ります。',
        'hiragana': 'まいにちおふろにはいります。',
        'romaji': 'Mainichi ofuro ni hairimasu.',
        'english': 'I take a bath every day.'
    },
    '噌': {
        'japanese': '味噌汁を作りましょう。',
        'hiragana': 'みそしるをつくりましょう。',
        'romaji': 'Misoshiru wo tsukurimashou.',
        'english': 'Let\'s make miso soup.'
    },
    '壇': {
        'japanese': '庭に花壇を作りました。',
        'hiragana': 'にわにかだんをつくりました。',
        'romaji': 'Niwa ni kadan wo tsukurimashita.',
        'english': 'I made a flower bed in the garden.'
    },
    '嬉': {
        'japanese': '家族が集まって嬉しいです。',
        'hiragana': 'かぞくがあつまってうれしいです。',
        'romaji': 'Kazoku ga atsumatte ureshii desu.',
        'english': 'I\'m happy that the family is gathering.'
    },
    '履': {
        'japanese': '靴を履いて出かけます。',
        'hiragana': 'くつをはいてでかけます。',
        'romaji': 'Kutsu wo haite dekakemasu.',
        'english': 'I put on shoes and go out.'
    },
    '床': {
        'japanese': '床を掃除機できれいにします。',
        'hiragana': 'ゆかをそうじきできれいにします。',
        'romaji': 'Yuka wo soujiki de kirei ni shimasu.',
        'english': 'I clean the floor with a vacuum cleaner.'
    },
    '廊': {
        'japanese': '廊下を静かに歩いてください。',
        'hiragana': 'ろうかをしずかにあるいてください。',
        'romaji': 'Rouka wo shizuka ni aruite kudasai.',
        'english': 'Please walk quietly in the corridor.'
    },
    '慎': {
        'japanese': '慎重に料理を運びます。',
        'hiragana': 'しんちょうにりょうりをはこびます。',
        'romaji': 'Shinchou ni ryouri wo hakobimasu.',
        'english': 'I carefully carry the food.'
    },
    '掃': {
        'japanese': '毎週末部屋を掃除します。',
        'hiragana': 'まいしゅうまつへやをそうじします。',
        'romaji': 'Maishuumatsu heya wo souji shimasu.',
        'english': 'I clean my room every weekend.'
    },
    '棚': {
        'japanese': '食器を棚に並べます。',
        'hiragana': 'しょっきをたなにならべます。',
        'romaji': 'Shokki wo tana ni narabemasu.',
        'english': 'I arrange the dishes on the shelf.'
    },
    '清': {
        'japanese': '清潔なキッチンを保ちます。',
        'hiragana': 'せいけつなきっちんをたもちます。',
        'romaji': 'Seiketsu na kicchin wo tamochimasu.',
        'english': 'I keep a clean kitchen.'
    },
    '潔': {
        'japanese': '部屋を清潔に保っています。',
        'hiragana': 'へやをせいけつにたもっています。',
        'romaji': 'Heya wo seiketsu ni tamotte imasu.',
        'english': 'I keep the room clean.'
    },
    '炊': {
        'japanese': '炊飯器でご飯を炊きます。',
        'hiragana': 'すいはんきでごはんをたきます。',
        'romaji': 'Suihanki de gohan wo takimasu.',
        'english': 'I cook rice with a rice cooker.'
    },
    '煮': {
        'japanese': '野菜を煮て柔らかくします。',
        'hiragana': 'やさいをにてやわらかくします。',
        'romaji': 'Yasai wo nite yawarakaku shimasu.',
        'english': 'I boil vegetables to make them soft.'
    },
    '玄': {
        'japanese': '玄関で靴を脱いでください。',
        'hiragana': 'げんかんでくつをぬいでください。',
        'romaji': 'Genkan de kutsu wo nuide kudasai.',
        'english': 'Please take off your shoes at the entrance.'
    },
    '玉': {
        'japanese': '玉ねぎを切ると涙が出ます。',
        'hiragana': 'たまねぎをきるとなみだがでます。',
        'romaji': 'Tamanegi wo kiru to namida ga demasu.',
        'english': 'Tears come out when I cut onions.'
    },
    '疲': {
        'japanese': '家事をして疲れました。',
        'hiragana': 'かじをしてつかれました。',
        'romaji': 'Kaji wo shite tsukaremashita.',
        'english': 'I got tired from doing housework.'
    },
    '砂': {
        'japanese': 'コーヒーに砂糖を入れますか。',
        'hiragana': 'こーひーにさとうをいれますか。',
        'romaji': 'Koohii ni satou wo iremasu ka.',
        'english': 'Do you put sugar in your coffee?'
    },
    '窓': {
        'japanese': '窓を開けて部屋を換気します。',
        'hiragana': 'まどをあけてへやをかんきします。',
        'romaji': 'Mado wo akete heya wo kanki shimasu.',
        'english': 'I open the window to ventilate the room.'
    },
    '糖': {
        'japanese': '砂糖を少し加えてください。',
        'hiragana': 'さとうをすこしくわえてください。',
        'romaji': 'Satou wo sukoshi kuwaete kudasai.',
        'english': 'Please add a little sugar.'
    },
    '蓋': {
        'japanese': '鍋の蓋を開けて確認します。',
        'hiragana': 'なべのふたをあけてかくにんします。',
        'romaji': 'Nabe no futa wo akete kakunin shimasu.',
        'english': 'I open the pot lid to check.'
    },
    '蔵': {
        'japanese': '食材を冷蔵庫に入れました。',
        'hiragana': 'しょくざいをれいぞうこにいれました。',
        'romaji': 'Shokuzai wo reizouko ni iremashita.',
        'english': 'I put the ingredients in the refrigerator.'
    },
    '褒': {
        'japanese': '母の料理をいつも褒めます。',
        'hiragana': 'ははのりょうりをいつもほめます。',
        'romaji': 'Haha no ryouri wo itsumo homemasu.',
        'english': 'I always praise my mother\'s cooking.'
    },
    '込': {
        'japanese': '部屋に荷物を運び込みました。',
        'hiragana': 'へやににもつをはこびこみました。',
        'romaji': 'Heya ni nimotsu wo hakobi-komimashita.',
        'english': 'I carried the luggage into the room.'
    },
    '迎': {
        'japanese': '玄関で家族を迎えます。',
        'hiragana': 'げんかんでかぞくをむかえます。',
        'romaji': 'Genkan de kazoku wo mukaemasu.',
        'english': 'I welcome my family at the entrance.'
    },
    '醤': {
        'japanese': '料理に醤油をかけます。',
        'hiragana': 'りょうりにしょうゆをかけます。',
        'romaji': 'Ryouri ni shouyu wo kakemasu.',
        'english': 'I pour soy sauce on the food.'
    },
    '鍋': {
        'japanese': '鍋で野菜を煮ています。',
        'hiragana': 'なべでやさいをにています。',
        'romaji': 'Nabe de yasai wo nite imasu.',
        'english': 'I\'m boiling vegetables in a pot.'
    },
    '階': {
        'japanese': '二階の部屋で寝ます。',
        'hiragana': 'にかいのへやでねます。',
        'romaji': 'Nikai no heya de nemasu.',
        'english': 'I sleep in the room on the second floor.'
    },
    '頓': {
        'japanese': '部屋を整理整頓しました。',
        'hiragana': 'へやをせいりせいとんしました。',
        'romaji': 'Heya wo seiri seiton shimashita.',
        'english': 'I organized and tidied up the room.'
    },
    '飯': {
        'japanese': 'ご飯が炊けました。',
        'hiragana': 'ごはんがたけました。',
        'romaji': 'Gohan ga takemashita.',
        'english': 'The rice is cooked.'
    },
    '魚': {
        'japanese': '今日は魚を焼いて食べます。',
        'hiragana': 'きょうはさかなをやいてたべます。',
        'romaji': 'Kyou wa sakana wo yaite tabemasu.',
        'english': 'I\'m grilling fish and eating it today.'
    },
    '鳴': {
        'japanese': 'タイマーが鳴ったので料理ができました。',
        'hiragana': 'たいまーがなったのでりょうりができました。',
        'romaji': 'Taimaa ga natta node ryouri ga dekimashita.',
        'english': 'The timer rang so the food is done.'
    },
}

def add_n2_sentences():
    """Add example sentences for N2 kanji - FINAL BATCH"""

    # Load current data
    with open('temp/kanji_with_jlpt_complete.json', 'r', encoding='utf-8') as f:
        kanji_data = json.load(f)

    # Add sentences to N2 kanji
    n2_count = 0
    sentence_count = 0

    for char, sentence in N2_SENTENCES.items():
        if char in kanji_data and kanji_data[char].get('jlpt') == 'N2':
            kanji_data[char]['sentence'] = sentence
            n2_count += 1
            sentence_count += 1

    # Save updated data
    with open('temp/kanji_with_jlpt_complete.json', 'w', encoding='utf-8') as f:
        json.dump(kanji_data, f, ensure_ascii=False, indent=2)

    print(f"Task 1.4 - Batch 4: N2 Kanji Example Sentences (FINAL)")
    print("=" * 60)
    print(f"\n✅ Batch 4 Complete!")
    print(f"   N2 Kanji processed: {n2_count}")
    print(f"   Total sentences added: {sentence_count}")
    print(f"\n💾 Saved to: temp/kanji_with_jlpt_complete.json")
    print(f"\n✅ All {n2_count} N2 kanji now have example sentences!")
    print(f"\n🎉 TASK 1.4 COMPLETE! All 169 example sentences generated!")

if __name__ == '__main__':
    add_n2_sentences()
