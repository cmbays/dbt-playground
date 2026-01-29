/**
 * Home Life Kanji Data
 * Complete metadata for all kanji from home-life topic pages
 * 
 * Generated: 2026-01-21
 * Total Kanji: 169
 * JLPT Levels: N5, N4, N3, N2
 * 
 * Each kanji entry includes:
 * - character: The kanji character
 * - readings: On-yomi and kun-yomi readings
 * - meanings: English meanings
 * - jlpt: JLPT level (N5-N2)
 * - topics: Related topics (currently all "home-life")
 * - categories: Semantic categories from source files
 * - words: 3 example vocabulary words with readings and JLPT levels
 * - sentence: 1 example sentence in 4 formats (japanese, hiragana, romaji, english)
 */

const homeLifeKanji = [
  {
    character: "下",
    readings: { on: ["カ"], kun: ["した", "さ(がる)", "お(りる)"] },
    meanings: ["down", "below", "under"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "下", hiragana: "した", english: "under, below", jlpt: "N5" },
      { japanese: "下さい", hiragana: "ください", english: "please (give me)", jlpt: "N5" },
      { japanese: "地下", hiragana: "ちか", english: "basement, underground", jlpt: "N4" }
    ],
    sentence: {
      japanese: "本は机の下にあります。",
      hiragana: "ほんはつくえのしたにあります。",
      romaji: "Hon wa tsukue no shita ni arimasu.",
      english: "The book is under the desk."
    }
  },
  {
    character: "入",
    readings: { on: ["ニュウ"], kun: ["い(れる)", "はい(る)"] },
    meanings: ["enter", "put in", "go in"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["朝の動作", "夜の活動"],
    words: [
      { japanese: "入る", hiragana: "はいる", english: "to enter", jlpt: "N5" },
      { japanese: "入れる", hiragana: "いれる", english: "to put in", jlpt: "N5" },
      { japanese: "入口", hiragana: "いりぐち", english: "entrance", jlpt: "N5" }
    ],
    sentence: {
      japanese: "部屋に入ってください。",
      hiragana: "へやにはいってください。",
      romaji: "Heya ni haitte kudasai.",
      english: "Please enter the room."
    }
  },
  {
    character: "出",
    readings: { on: ["シュツ"], kun: ["で(る)", "だ(す)"] },
    meanings: ["exit", "come out"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["夜の活動"],
    words: [
      { japanese: "出る", hiragana: "でる", english: "to go out, leave", jlpt: "N5" },
      { japanese: "出す", hiragana: "だす", english: "to take out", jlpt: "N5" },
      { japanese: "出口", hiragana: "でぐち", english: "exit", jlpt: "N5" }
    ],
    sentence: {
      japanese: "毎朝７時に家を出ます。",
      hiragana: "まいあさしちじにいえをでます。",
      romaji: "Maiasa shichi-ji ni ie wo demasu.",
      english: "I leave home at 7 o'clock every morning."
    }
  },
  {
    character: "前",
    readings: { on: ["ゼン"], kun: ["まえ"] },
    meanings: ["front", "before"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と朝"],
    words: [
      { japanese: "前", hiragana: "まえ", english: "front, before", jlpt: "N5" },
      { japanese: "午前", hiragana: "ごぜん", english: "morning, AM", jlpt: "N5" },
      { japanese: "名前", hiragana: "なまえ", english: "name", jlpt: "N5" }
    ],
    sentence: {
      japanese: "学校の前で待っています。",
      hiragana: "がっこうのまえでまっています。",
      romaji: "Gakkou no mae de matte imasu.",
      english: "I'm waiting in front of the school."
    }
  },
  {
    character: "午",
    readings: { on: ["ゴ"], kun: [""] },
    meanings: ["noon", "AM/PM"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と朝", "時間と夜", "時間と描写"],
    words: [
      { japanese: "午前", hiragana: "ごぜん", english: "morning, AM", jlpt: "N5" },
      { japanese: "午後", hiragana: "ごご", english: "afternoon, PM", jlpt: "N5" },
      { japanese: "正午", hiragana: "しょうご", english: "noon", jlpt: "N4" }
    ],
    sentence: {
      japanese: "午後に友達と会います。",
      hiragana: "ごごにともだちとあいます。",
      romaji: "Gogo ni tomodachi to aimasu.",
      english: "I'm meeting a friend in the afternoon."
    }
  },
  {
    character: "土",
    readings: { on: ["ド"], kun: ["つち"] },
    meanings: ["earth", "soil", "Saturday"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と描写"],
    words: [
      { japanese: "土", hiragana: "つち", english: "soil, earth", jlpt: "N5" },
      { japanese: "土曜日", hiragana: "どようび", english: "Saturday", jlpt: "N5" },
      { japanese: "土地", hiragana: "とち", english: "land", jlpt: "N4" }
    ],
    sentence: {
      japanese: "土曜日は家族と過ごします。",
      hiragana: "どようびはかぞくとすごします。",
      romaji: "Doyoubi wa kazoku to sugoshimasu.",
      english: "I spend Saturdays with my family."
    }
  },
  {
    character: "夜",
    readings: { on: ["ヤ"], kun: ["よる", "よ"] },
    meanings: ["night"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と夜"],
    words: [
      { japanese: "夜", hiragana: "よる", english: "night", jlpt: "N5" },
      { japanese: "今夜", hiragana: "こんや", english: "tonight", jlpt: "N5" },
      { japanese: "夜中", hiragana: "よなか", english: "midnight", jlpt: "N4" }
    ],
    sentence: {
      japanese: "夜は静かに勉強します。",
      hiragana: "よるはしずかにべんきょうします。",
      romaji: "Yoru wa shizuka ni benkyou shimasu.",
      english: "I study quietly at night."
    }
  },
  {
    character: "天",
    readings: { on: ["テン"], kun: ["あま"] },
    meanings: ["heaven", "tempura"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["調味料と食べ物"],
    words: [
      { japanese: "天気", hiragana: "てんき", english: "weather", jlpt: "N5" },
      { japanese: "天井", hiragana: "てんじょう", english: "ceiling", jlpt: "N4" },
      { japanese: "天国", hiragana: "てんごく", english: "heaven", jlpt: "N3" }
    ],
    sentence: {
      japanese: "今日は天気がいいですね。",
      hiragana: "きょうはてんきがいいですね。",
      romaji: "Kyou wa tenki ga ii desu ne.",
      english: "The weather is nice today, isn't it?"
    }
  },
  {
    character: "女",
    readings: { on: ["ジョ"], kun: ["おんな"] },
    meanings: ["woman", "female"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["家族"],
    words: [
      { japanese: "女", hiragana: "おんな", english: "woman", jlpt: "N5" },
      { japanese: "女の子", hiragana: "おんなのこ", english: "girl", jlpt: "N5" },
      { japanese: "彼女", hiragana: "かのじょ", english: "she, girlfriend", jlpt: "N5" }
    ],
    sentence: {
      japanese: "私の姉は女子大学生です。",
      hiragana: "わたしのあねはじょしだいがくせいです。",
      romaji: "Watashi no ane wa joshi daigakusei desu.",
      english: "My older sister is a female university student."
    }
  },
  {
    character: "子",
    readings: { on: ["シ"], kun: ["こ"] },
    meanings: ["child"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["家族", "家族と人"],
    words: [
      { japanese: "子供", hiragana: "こども", english: "child", jlpt: "N5" },
      { japanese: "男の子", hiragana: "おとこのこ", english: "boy", jlpt: "N5" },
      { japanese: "女の子", hiragana: "おんなのこ", english: "girl", jlpt: "N5" }
    ],
    sentence: {
      japanese: "子供たちは庭で遊んでいます。",
      hiragana: "こどもたちはにわであそんでいます。",
      romaji: "Kodomo-tachi wa niwa de asonde imasu.",
      english: "The children are playing in the garden."
    }
  },
  {
    character: "学",
    readings: { on: ["ガク"], kun: ["まな(ぶ)"] },
    meanings: ["learn", "school", "study"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["よく使う言葉", "描写と動作"],
    words: [
      { japanese: "学校", hiragana: "がっこう", english: "school", jlpt: "N5" },
      { japanese: "学生", hiragana: "がくせい", english: "student", jlpt: "N5" },
      { japanese: "大学", hiragana: "だいがく", english: "university", jlpt: "N5" }
    ],
    sentence: {
      japanese: "毎日学校で日本語を学びます。",
      hiragana: "まいにちがっこうでにほんごをまなびます。",
      romaji: "Mainichi gakkou de nihongo wo manabimasu.",
      english: "I learn Japanese at school every day."
    }
  },
  {
    character: "帰",
    readings: { on: ["キ"], kun: ["かえ(る)"] },
    meanings: ["return", "go home"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["夜の活動"],
    words: [
      { japanese: "帰る", hiragana: "かえる", english: "to go home, return", jlpt: "N5" },
      { japanese: "帰り", hiragana: "かえり", english: "return (trip)", jlpt: "N4" },
      { japanese: "帰国", hiragana: "きこく", english: "return to one's country", jlpt: "N3" }
    ],
    sentence: {
      japanese: "６時に家に帰ります。",
      hiragana: "ろくじにいえにかえります。",
      romaji: "Roku-ji ni ie ni kaerimasu.",
      english: "I return home at 6 o'clock."
    }
  },
  {
    character: "後",
    readings: { on: ["ゴ"], kun: ["あと", "うし(ろ)"] },
    meanings: ["after", "behind"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と夜", "時間と描写"],
    words: [
      { japanese: "後", hiragana: "あと", english: "after, later", jlpt: "N5" },
      { japanese: "午後", hiragana: "ごご", english: "afternoon, PM", jlpt: "N5" },
      { japanese: "後ろ", hiragana: "うしろ", english: "back, behind", jlpt: "N5" }
    ],
    sentence: {
      japanese: "授業の後で図書館に行きます。",
      hiragana: "じゅぎょうのあとでとしょかんにいきます。",
      romaji: "Jugyou no ato de toshokan ni ikimasu.",
      english: "I go to the library after class."
    }
  },
  {
    character: "新",
    readings: { on: ["シン"], kun: ["あたら(しい)"] },
    meanings: ["new"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "新しい", hiragana: "あたらしい", english: "new", jlpt: "N5" },
      { japanese: "新聞", hiragana: "しんぶん", english: "newspaper", jlpt: "N5" },
      { japanese: "新年", hiragana: "しんねん", english: "new year", jlpt: "N4" }
    ],
    sentence: {
      japanese: "新しい家に引っ越しました。",
      hiragana: "あたらしいいえにひっこしました。",
      romaji: "Atarashii ie ni hikkoshimashita.",
      english: "I moved to a new house."
    }
  },
  {
    character: "日",
    readings: { on: ["ニチ"], kun: ["ひ", "か"] },
    meanings: ["sun", "day"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["よく使う言葉", "時間と夜"],
    words: [
      { japanese: "日", hiragana: "ひ", english: "day, sun", jlpt: "N5" },
      { japanese: "今日", hiragana: "きょう", english: "today", jlpt: "N5" },
      { japanese: "毎日", hiragana: "まいにち", english: "every day", jlpt: "N5" }
    ],
    sentence: {
      japanese: "日曜日は家でゆっくりします。",
      hiragana: "にちようびはいえでゆっくりします。",
      romaji: "Nichiyoubi wa ie de yukkuri shimasu.",
      english: "I relax at home on Sundays."
    }
  },
  {
    character: "早",
    readings: { on: ["ソウ"], kun: ["はや(い)"] },
    meanings: ["early", "fast"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と朝"],
    words: [
      { japanese: "早い", hiragana: "はやい", english: "early", jlpt: "N5" },
      { japanese: "早く", hiragana: "はやく", english: "early, quickly", jlpt: "N5" },
      { japanese: "早朝", hiragana: "そうちょう", english: "early morning", jlpt: "N3" }
    ],
    sentence: {
      japanese: "毎朝早く起きます。",
      hiragana: "まいあさはやくおきます。",
      romaji: "Maiasa hayaku okimasu.",
      english: "I wake up early every morning."
    }
  },
  {
    character: "明",
    readings: { on: ["メイ"], kun: ["あ(かり)", "あ(ける)"] },
    meanings: ["bright", "clear", "tomorrow"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["よく使う言葉", "時間と夜"],
    words: [
      { japanese: "明るい", hiragana: "あかるい", english: "bright", jlpt: "N5" },
      { japanese: "明日", hiragana: "あした", english: "tomorrow", jlpt: "N5" },
      { japanese: "明らか", hiragana: "あきらか", english: "clear, obvious", jlpt: "N3" }
    ],
    sentence: {
      japanese: "明日は天気が良さそうです。",
      hiragana: "あしたはてんきがよさそうです。",
      romaji: "Ashita wa tenki ga yosasou desu.",
      english: "The weather looks like it will be good tomorrow."
    }
  },
  {
    character: "時",
    readings: { on: ["ジ"], kun: ["とき"] },
    meanings: ["time", "hour"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と朝", "時間と夜"],
    words: [
      { japanese: "時", hiragana: "とき", english: "time, when", jlpt: "N5" },
      { japanese: "時間", hiragana: "じかん", english: "time, hour", jlpt: "N5" },
      { japanese: "時計", hiragana: "とけい", english: "clock, watch", jlpt: "N5" }
    ],
    sentence: {
      japanese: "時計を見てください。",
      hiragana: "とけいをみてください。",
      romaji: "Tokei wo mite kudasai.",
      english: "Please look at the clock."
    }
  },
  {
    character: "曜",
    readings: { on: ["ヨウ"], kun: [""] },
    meanings: ["day of the week"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と描写"],
    words: [
      { japanese: "曜日", hiragana: "ようび", english: "day of the week", jlpt: "N5" },
      { japanese: "月曜日", hiragana: "げつようび", english: "Monday", jlpt: "N5" },
      { japanese: "日曜日", hiragana: "にちようび", english: "Sunday", jlpt: "N5" }
    ],
    sentence: {
      japanese: "今日は何曜日ですか。",
      hiragana: "きょうはなんようびですか。",
      romaji: "Kyou wa nan-youbi desu ka.",
      english: "What day of the week is it today?"
    }
  },
  {
    character: "朝",
    readings: { on: ["チョウ"], kun: ["あさ"] },
    meanings: ["morning"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と朝"],
    words: [
      { japanese: "朝", hiragana: "あさ", english: "morning", jlpt: "N5" },
      { japanese: "朝ごはん", hiragana: "あさごはん", english: "breakfast", jlpt: "N5" },
      { japanese: "今朝", hiragana: "けさ", english: "this morning", jlpt: "N5" }
    ],
    sentence: {
      japanese: "朝ごはんを食べましたか。",
      hiragana: "あさごはんをたべましたか。",
      romaji: "Asa-gohan wo tabemashita ka.",
      english: "Did you eat breakfast?"
    }
  },
  {
    character: "校",
    readings: { on: ["コウ"], kun: [""] },
    meanings: ["school"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "学校", hiragana: "がっこう", english: "school", jlpt: "N5" },
      { japanese: "高校", hiragana: "こうこう", english: "high school", jlpt: "N5" },
      { japanese: "校長", hiragana: "こうちょう", english: "principal", jlpt: "N3" }
    ],
    sentence: {
      japanese: "学校まで歩いて１５分です。",
      hiragana: "がっこうまであるいてじゅうごふんです。",
      romaji: "Gakkou made aruite juugo-fun desu.",
      english: "It's a 15-minute walk to school."
    }
  },
  {
    character: "母",
    readings: { on: ["ボ"], kun: ["はは"] },
    meanings: ["mother"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["家族", "家族と人"],
    words: [
      { japanese: "母", hiragana: "はは", english: "mother (one's own)", jlpt: "N5" },
      { japanese: "お母さん", hiragana: "おかあさん", english: "mother (polite)", jlpt: "N5" },
      { japanese: "母親", hiragana: "ははおや", english: "mother (formal)", jlpt: "N3" }
    ],
    sentence: {
      japanese: "母は料理が上手です。",
      hiragana: "ははははりょうりがじょうずです。",
      romaji: "Haha wa ryouri ga jouzu desu.",
      english: "My mother is good at cooking."
    }
  },
  {
    character: "気",
    readings: { on: ["キ"], kun: ["いき"] },
    meanings: ["spirit", "feeling", "air"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "気", hiragana: "き", english: "spirit, feeling", jlpt: "N5" },
      { japanese: "元気", hiragana: "げんき", english: "healthy, energetic", jlpt: "N5" },
      { japanese: "天気", hiragana: "てんき", english: "weather", jlpt: "N5" }
    ],
    sentence: {
      japanese: "今日は気分がいいです。",
      hiragana: "きょうはきぶんがいいです。",
      romaji: "Kyou wa kibun ga ii desu.",
      english: "I feel good today."
    }
  },
  {
    character: "水",
    readings: { on: ["スイ"], kun: ["みず"] },
    meanings: ["water"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["庭と外"],
    words: [
      { japanese: "水", hiragana: "みず", english: "water", jlpt: "N5" },
      { japanese: "水曜日", hiragana: "すいようび", english: "Wednesday", jlpt: "N5" },
      { japanese: "水道", hiragana: "すいどう", english: "water supply", jlpt: "N4" }
    ],
    sentence: {
      japanese: "水を一杯ください。",
      hiragana: "みずをいっぱいください。",
      romaji: "Mizu wo ippai kudasai.",
      english: "Please give me a glass of water."
    }
  },
  {
    character: "父",
    readings: { on: ["フ"], kun: ["ちち"] },
    meanings: ["father"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["家族", "家族と人"],
    words: [
      { japanese: "父", hiragana: "ちち", english: "father (one's own)", jlpt: "N5" },
      { japanese: "お父さん", hiragana: "おとうさん", english: "father (polite)", jlpt: "N5" },
      { japanese: "父親", hiragana: "ちちおや", english: "father (formal)", jlpt: "N3" }
    ],
    sentence: {
      japanese: "父は会社で働いています。",
      hiragana: "ちちはかいしゃではたらいています。",
      romaji: "Chichi wa kaisha de hataraite imasu.",
      english: "My father works at a company."
    }
  },
  {
    character: "男",
    readings: { on: ["ダン"], kun: ["おとこ"] },
    meanings: ["man", "male"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["家族"],
    words: [
      { japanese: "男", hiragana: "おとこ", english: "man", jlpt: "N5" },
      { japanese: "男の子", hiragana: "おとこのこ", english: "boy", jlpt: "N5" },
      { japanese: "長男", hiragana: "ちょうなん", english: "eldest son", jlpt: "N4" }
    ],
    sentence: {
      japanese: "男の子が二人います。",
      hiragana: "おとこのこがふたりいます。",
      romaji: "Otoko no ko ga futari imasu.",
      english: "There are two boys."
    }
  },
  {
    character: "花",
    readings: { on: ["カ"], kun: ["はな"] },
    meanings: ["flower"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["庭と外"],
    words: [
      { japanese: "花", hiragana: "はな", english: "flower", jlpt: "N5" },
      { japanese: "花火", hiragana: "はなび", english: "fireworks", jlpt: "N4" },
      { japanese: "生け花", hiragana: "いけばな", english: "flower arrangement", jlpt: "N3" }
    ],
    sentence: {
      japanese: "庭に花が咲いています。",
      hiragana: "にわにはながさいています。",
      romaji: "Niwa ni hana ga saite imasu.",
      english: "Flowers are blooming in the garden."
    }
  },
  {
    character: "話",
    readings: { on: ["ワ"], kun: ["はな(す)"] },
    meanings: ["speak", "talk"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "話す", hiragana: "はなす", english: "to speak, talk", jlpt: "N5" },
      { japanese: "話", hiragana: "はなし", english: "story, talk", jlpt: "N5" },
      { japanese: "電話", hiragana: "でんわ", english: "telephone", jlpt: "N5" }
    ],
    sentence: {
      japanese: "友達と日本語で話します。",
      hiragana: "ともだちとにほんごではなします。",
      romaji: "Tomodachi to nihongo de hanashimasu.",
      english: "I talk with friends in Japanese."
    }
  },
  {
    character: "足",
    readings: { on: ["ソク"], kun: ["あし", "た(りる)"] },
    meanings: ["foot", "sufficient"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["時間と描写"],
    words: [
      { japanese: "足", hiragana: "あし", english: "foot, leg", jlpt: "N5" },
      { japanese: "足りる", hiragana: "たりる", english: "to be sufficient", jlpt: "N4" },
      { japanese: "不足", hiragana: "ふそく", english: "shortage", jlpt: "N3" }
    ],
    sentence: {
      japanese: "足が痛いです。",
      hiragana: "あしがいたいです。",
      romaji: "Ashi ga itai desu.",
      english: "My foot hurts."
    }
  },
  {
    character: "長",
    readings: { on: ["チョウ"], kun: ["なが(い)"] },
    meanings: ["long", "eldest"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["家族"],
    words: [
      { japanese: "長い", hiragana: "ながい", english: "long", jlpt: "N5" },
      { japanese: "長男", hiragana: "ちょうなん", english: "eldest son", jlpt: "N4" },
      { japanese: "社長", hiragana: "しゃちょう", english: "company president", jlpt: "N4" }
    ],
    sentence: {
      japanese: "兄は背が長いです。",
      hiragana: "あにはせがながいです。",
      romaji: "Ani wa se ga nagai desu.",
      english: "My older brother is tall."
    }
  },
  {
    character: "間",
    readings: { on: ["カン"], kun: ["ま", "あいだ"] },
    meanings: ["interval", "room", "time"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "間", hiragana: "あいだ", english: "between, interval", jlpt: "N5" },
      { japanese: "時間", hiragana: "じかん", english: "time, hour", jlpt: "N5" },
      { japanese: "人間", hiragana: "にんげん", english: "human being", jlpt: "N4" }
    ],
    sentence: {
      japanese: "授業と授業の間に休みます。",
      hiragana: "じゅぎょうとじゅぎょうのあいだにやすみます。",
      romaji: "Jugyou to jugyou no aida ni yasumimasu.",
      english: "I rest between classes."
    }
  },
  {
    character: "食",
    readings: { on: ["ショク"], kun: ["た(べる)", "く(う)"] },
    meanings: ["eat", "food", "meal"],
    jlpt: "N5",
    topics: ["home-life"],
    categories: ["食事"],
    words: [
      { japanese: "食べる", hiragana: "たべる", english: "to eat", jlpt: "N5" },
      { japanese: "食事", hiragana: "しょくじ", english: "meal", jlpt: "N4" },
      { japanese: "朝食", hiragana: "ちょうしょく", english: "breakfast", jlpt: "N4" }
    ],
    sentence: {
      japanese: "毎日三回食事をします。",
      hiragana: "まいにちさんかいしょくじをします。",
      romaji: "Mainichi san-kai shokuji wo shimasu.",
      english: "I eat three meals every day."
    }
  },

  // ===== N4 Kanji =====

  {
    character: "並",
    readings: { on: ["ヘイ"], kun: ["なら(べる)"] },
    meanings: ["arrange", "line up"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "並ぶ", hiragana: "ならぶ", english: "to line up", jlpt: "N4" },
      { japanese: "並べる", hiragana: "ならべる", english: "to arrange", jlpt: "N4" },
      { japanese: "人並み", hiragana: "ひとなみ", english: "average, ordinary", jlpt: "N3" }
    ],
    sentence: {
      japanese: "本を棚に並べてください。",
      hiragana: "ほんをたなにならべてください。",
      romaji: "Hon wo tana ni narabete kudasai.",
      english: "Please arrange the books on the shelf."
    }
  },
  {
    character: "乾",
    readings: { on: ["カン"], kun: ["かわ(く)", "かわ(かす)"] },
    meanings: ["dry"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["夜の活動"],
    words: [
      { japanese: "乾く", hiragana: "かわく", english: "to dry", jlpt: "N4" },
      { japanese: "乾かす", hiragana: "かわかす", english: "to dry (something)", jlpt: "N3" },
      { japanese: "乾燥", hiragana: "かんそう", english: "dryness", jlpt: "N3" }
    ],
    sentence: {
      japanese: "洗濯物がよく乾きました。",
      hiragana: "せんたくものがよくかわきました。",
      romaji: "Sentakumono ga yoku kawakimashita.",
      english: "The laundry dried well."
    }
  },
  {
    character: "事",
    readings: { on: ["ジ"], kun: ["こと"] },
    meanings: ["thing", "matter", "work"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "事", hiragana: "こと", english: "thing, matter", jlpt: "N5" },
      { japanese: "仕事", hiragana: "しごと", english: "work, job", jlpt: "N5" },
      { japanese: "大事", hiragana: "だいじ", english: "important", jlpt: "N4" }
    ],
    sentence: {
      japanese: "大事なことを忘れました。",
      hiragana: "だいじなことをわすれました。",
      romaji: "Daiji na koto wo wasuremashita.",
      english: "I forgot something important."
    }
  },
  {
    character: "仕",
    readings: { on: ["シ"], kun: ["つか(える)"] },
    meanings: ["serve", "work"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "仕事", hiragana: "しごと", english: "work, job", jlpt: "N5" },
      { japanese: "仕方", hiragana: "しかた", english: "way, method", jlpt: "N4" },
      { japanese: "仕上げる", hiragana: "しあげる", english: "to finish up", jlpt: "N3" }
    ],
    sentence: {
      japanese: "父は仕事が忙しいです。",
      hiragana: "ちちはしごとがいそがしいです。",
      romaji: "Chichi wa shigoto ga isogashii desu.",
      english: "My father is busy with work."
    }
  },
  {
    character: "作",
    readings: { on: ["サク"], kun: ["つく(る)"] },
    meanings: ["make", "create"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["朝の動作"],
    words: [
      { japanese: "作る", hiragana: "つくる", english: "to make", jlpt: "N5" },
      { japanese: "作文", hiragana: "さくぶん", english: "composition", jlpt: "N4" },
      { japanese: "作品", hiragana: "さくひん", english: "work of art", jlpt: "N4" }
    ],
    sentence: {
      japanese: "母が夕食を作っています。",
      hiragana: "ははがゆうしょくをつくっています。",
      romaji: "Haha ga yuushoku wo tsukutte imasu.",
      english: "My mother is making dinner."
    }
  },
  {
    character: "供",
    readings: { on: ["キョウ"], kun: ["そな(える)", "とも"] },
    meanings: ["offer", "children (plural)"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家族"],
    words: [
      { japanese: "子供", hiragana: "こども", english: "child", jlpt: "N5" },
      { japanese: "提供", hiragana: "ていきょう", english: "offer, provision", jlpt: "N3" },
      { japanese: "供給", hiragana: "きょうきゅう", english: "supply", jlpt: "N2" }
    ],
    sentence: {
      japanese: "子供の部屋を掃除しました。",
      hiragana: "こどものへやをそうじしました。",
      romaji: "Kodomo no heya wo souji shimashita.",
      english: "I cleaned the children's room."
    }
  },
  {
    character: "全",
    readings: { on: ["ゼン"], kun: ["まった(く)"] },
    meanings: ["whole", "all"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家族", "家族と人"],
    words: [
      { japanese: "全部", hiragana: "ぜんぶ", english: "all, everything", jlpt: "N4" },
      { japanese: "全員", hiragana: "ぜんいん", english: "all members", jlpt: "N4" },
      { japanese: "全て", hiragana: "すべて", english: "all, everything", jlpt: "N3" }
    ],
    sentence: {
      japanese: "全部きれいにしましょう。",
      hiragana: "ぜんぶきれいにしましょう。",
      romaji: "Zenbu kirei ni shimashou.",
      english: "Let's clean everything."
    }
  },
  {
    character: "切",
    readings: { on: ["セツ"], kun: ["き(る)"] },
    meanings: ["cut"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "切る", hiragana: "きる", english: "to cut", jlpt: "N5" },
      { japanese: "切手", hiragana: "きって", english: "stamp", jlpt: "N5" },
      { japanese: "大切", hiragana: "たいせつ", english: "important", jlpt: "N4" }
    ],
    sentence: {
      japanese: "野菜を小さく切ります。",
      hiragana: "やさいをちいさくきります。",
      romaji: "Yasai wo chiisaku kirimasu.",
      english: "I cut the vegetables small."
    }
  },
  {
    character: "力",
    readings: { on: ["リョク"], kun: ["ちから"] },
    meanings: ["power", "strength"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["よく使う言葉", "家族と動作"],
    words: [
      { japanese: "力", hiragana: "ちから", english: "power, strength", jlpt: "N4" },
      { japanese: "電力", hiragana: "でんりょく", english: "electric power", jlpt: "N3" },
      { japanese: "努力", hiragana: "どりょく", english: "effort", jlpt: "N3" }
    ],
    sentence: {
      japanese: "力を合わせて頑張りましょう。",
      hiragana: "ちからをあわせてがんばりましょう。",
      romaji: "Chikara wo awasete ganbarimarou.",
      english: "Let's work hard together."
    }
  },
  {
    character: "台",
    readings: { on: ["ダイ"], kun: ["だい"] },
    meanings: ["stand", "platform", "counter", "kitchen"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "台所", hiragana: "だいどころ", english: "kitchen", jlpt: "N4" },
      { japanese: "台風", hiragana: "たいふう", english: "typhoon", jlpt: "N4" },
      { japanese: "一台", hiragana: "いちだい", english: "one (machine)", jlpt: "N4" }
    ],
    sentence: {
      japanese: "台所で料理を作ります。",
      hiragana: "だいどころでりょうりをつくります。",
      romaji: "Daidokoro de ryouri wo tsukurimasu.",
      english: "I make food in the kitchen."
    }
  },
  {
    character: "味",
    readings: { on: ["ミ"], kun: ["あじ"] },
    meanings: ["flavor", "taste"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["食事", "調味料と食べ物"],
    words: [
      { japanese: "味", hiragana: "あじ", english: "taste, flavor", jlpt: "N4" },
      { japanese: "味噌", hiragana: "みそ", english: "miso", jlpt: "N4" },
      { japanese: "意味", hiragana: "いみ", english: "meaning", jlpt: "N4" }
    ],
    sentence: {
      japanese: "この料理は味が美味しいです。",
      hiragana: "このりょうりはあじがおいしいです。",
      romaji: "Kono ryouri wa aji ga oishii desu.",
      english: "This dish tastes delicious."
    }
  },
  {
    character: "員",
    readings: { on: ["イン"], kun: [""] },
    meanings: ["member", "staff"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家族", "家族と人"],
    words: [
      { japanese: "全員", hiragana: "ぜんいん", english: "all members", jlpt: "N4" },
      { japanese: "会員", hiragana: "かいいん", english: "member", jlpt: "N4" },
      { japanese: "店員", hiragana: "てんいん", english: "store clerk", jlpt: "N4" }
    ],
    sentence: {
      japanese: "家族全員で食事をします。",
      hiragana: "かぞくぜんいんでしょくじをします。",
      romaji: "Kazoku zenin de shokuji wo shimasu.",
      english: "The whole family eats together."
    }
  },
  {
    character: "声",
    readings: { on: ["セイ"], kun: ["こえ"] },
    meanings: ["voice"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "声", hiragana: "こえ", english: "voice", jlpt: "N4" },
      { japanese: "大声", hiragana: "おおごえ", english: "loud voice", jlpt: "N3" },
      { japanese: "声明", hiragana: "せいめい", english: "statement", jlpt: "N2" }
    ],
    sentence: {
      japanese: "大きい声で話さないでください。",
      hiragana: "おおきいこえではなさないでください。",
      romaji: "Ookii koe de hanasanai de kudasai.",
      english: "Please don't speak in a loud voice."
    }
  },
  {
    character: "夕",
    readings: { on: ["セキ"], kun: ["ゆう"] },
    meanings: ["evening"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["時間と夜"],
    words: [
      { japanese: "夕方", hiragana: "ゆうがた", english: "evening", jlpt: "N4" },
      { japanese: "夕食", hiragana: "ゆうしょく", english: "dinner", jlpt: "N4" },
      { japanese: "夕日", hiragana: "ゆうひ", english: "setting sun", jlpt: "N3" }
    ],
    sentence: {
      japanese: "夕方に買い物に行きます。",
      hiragana: "ゆうがたにかいものにいきます。",
      romaji: "Yuugata ni kaimono ni ikimasu.",
      english: "I go shopping in the evening."
    }
  },
  {
    character: "始",
    readings: { on: ["シ"], kun: ["はじ(める)"] },
    meanings: ["begin", "start"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "始める", hiragana: "はじめる", english: "to begin", jlpt: "N5" },
      { japanese: "始まる", hiragana: "はじまる", english: "to start", jlpt: "N5" },
      { japanese: "始発", hiragana: "しはつ", english: "first train", jlpt: "N3" }
    ],
    sentence: {
      japanese: "授業は９時に始まります。",
      hiragana: "じゅぎょうはくじにはじまります。",
      romaji: "Jugyou wa ku-ji ni hajimarimasu.",
      english: "Class begins at 9 o'clock."
    }
  },
  {
    character: "家",
    readings: { on: ["カ"], kun: ["いえ", "や"] },
    meanings: ["house", "family"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家族", "家族と人", "家族と動作"],
    words: [
      { japanese: "家", hiragana: "いえ", english: "house", jlpt: "N5" },
      { japanese: "家族", hiragana: "かぞく", english: "family", jlpt: "N5" },
      { japanese: "家庭", hiragana: "かてい", english: "home, family", jlpt: "N4" }
    ],
    sentence: {
      japanese: "家族で旅行に行きたいです。",
      hiragana: "かぞくでりょこうにいきたいです。",
      romaji: "Kazoku de ryokou ni ikitai desu.",
      english: "I want to go on a trip with my family."
    }
  },
  {
    character: "寝",
    readings: { on: ["シン"], kun: ["ね(る)"] },
    meanings: ["sleep", "lie down"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["夜の活動"],
    words: [
      { japanese: "寝る", hiragana: "ねる", english: "to sleep", jlpt: "N5" },
      { japanese: "寝室", hiragana: "しんしつ", english: "bedroom", jlpt: "N4" },
      { japanese: "寝坊", hiragana: "ねぼう", english: "oversleep", jlpt: "N3" }
    ],
    sentence: {
      japanese: "昨夜は１０時に寝ました。",
      hiragana: "さくやはじゅうじにねました。",
      romaji: "Sakuya wa juu-ji ni nemashita.",
      english: "I went to bed at 10 o'clock last night."
    }
  },
  {
    character: "屋",
    readings: { on: ["オク"], kun: ["や"] },
    meanings: ["roof", "house", "shop"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "部屋", hiragana: "へや", english: "room", jlpt: "N5" },
      { japanese: "屋根", hiragana: "やね", english: "roof", jlpt: "N4" },
      { japanese: "屋上", hiragana: "おくじょう", english: "rooftop", jlpt: "N4" }
    ],
    sentence: {
      japanese: "部屋の窓を開けましょう。",
      hiragana: "へやのまどをあけましょう。",
      romaji: "Heya no mado wo akemashou.",
      english: "Let's open the room's window."
    }
  },
  {
    character: "度",
    readings: { on: ["ド"], kun: ["たび"] },
    meanings: ["degree", "time"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "度", hiragana: "ど", english: "degree, time", jlpt: "N4" },
      { japanese: "温度", hiragana: "おんど", english: "temperature", jlpt: "N4" },
      { japanese: "一度", hiragana: "いちど", english: "once", jlpt: "N4" }
    ],
    sentence: {
      japanese: "今日の温度は２０度です。",
      hiragana: "きょうのおんどはにじゅうどです。",
      romaji: "Kyou no ondo wa nijuu-do desu.",
      english: "Today's temperature is 20 degrees."
    }
  },
  {
    character: "庭",
    readings: { on: ["テイ"], kun: ["にわ"] },
    meanings: ["garden", "yard"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "庭", hiragana: "にわ", english: "garden", jlpt: "N4" },
      { japanese: "家庭", hiragana: "かてい", english: "home, family", jlpt: "N4" },
      { japanese: "庭園", hiragana: "ていえん", english: "garden, park", jlpt: "N3" }
    ],
    sentence: {
      japanese: "庭の花に水をあげます。",
      hiragana: "にわのはなにみずをあげます。",
      romaji: "Niwa no hana ni mizu wo agemasu.",
      english: "I water the flowers in the garden."
    }
  },
  {
    character: "息",
    readings: { on: ["ソク"], kun: ["いき"] },
    meanings: ["breath", "son"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家族", "家族と人"],
    words: [
      { japanese: "息子", hiragana: "むすこ", english: "son", jlpt: "N5" },
      { japanese: "息", hiragana: "いき", english: "breath", jlpt: "N4" },
      { japanese: "休息", hiragana: "きゅうそく", english: "rest", jlpt: "N3" }
    ],
    sentence: {
      japanese: "息子は毎日学校へ行きます。",
      hiragana: "むすこはまいにちがっこうへいきます。",
      romaji: "Musuko wa mainichi gakkou e ikimasu.",
      english: "My son goes to school every day."
    }
  },
  {
    character: "意",
    readings: { on: ["イ"], kun: [""] },
    meanings: ["idea", "mind"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["朝の動作"],
    words: [
      { japanese: "意味", hiragana: "いみ", english: "meaning", jlpt: "N4" },
      { japanese: "意見", hiragana: "いけん", english: "opinion", jlpt: "N4" },
      { japanese: "注意", hiragana: "ちゅうい", english: "attention, caution", jlpt: "N4" }
    ],
    sentence: {
      japanese: "この言葉の意味が分かりません。",
      hiragana: "このことばのいみがわかりません。",
      romaji: "Kono kotoba no imi ga wakarimasen.",
      english: "I don't understand the meaning of this word."
    }
  },
  {
    character: "所",
    readings: { on: ["ショ"], kun: ["ところ"] },
    meanings: ["place", "location"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "所", hiragana: "ところ", english: "place", jlpt: "N5" },
      { japanese: "台所", hiragana: "だいどころ", english: "kitchen", jlpt: "N4" },
      { japanese: "場所", hiragana: "ばしょ", english: "location", jlpt: "N4" }
    ],
    sentence: {
      japanese: "ここは静かな所ですね。",
      hiragana: "ここはしずかなところですね。",
      romaji: "Koko wa shizuka na tokoro desu ne.",
      english: "This is a quiet place, isn't it?"
    }
  },
  {
    character: "持",
    readings: { on: ["ジ"], kun: ["も(つ)"] },
    meanings: ["hold", "have"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "持つ", hiragana: "もつ", english: "to hold", jlpt: "N5" },
      { japanese: "気持ち", hiragana: "きもち", english: "feeling", jlpt: "N4" },
      { japanese: "持って行く", hiragana: "もっていく", english: "to take", jlpt: "N4" }
    ],
    sentence: {
      japanese: "鍵を持って出かけてください。",
      hiragana: "かぎをもってでかけてください。",
      romaji: "Kagi wo motte dekakete kudasai.",
      english: "Please take the key when you go out."
    }
  },
  {
    character: "教",
    readings: { on: ["キョウ"], kun: ["おし(える)"] },
    meanings: ["teach", "religion"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "教える", hiragana: "おしえる", english: "to teach", jlpt: "N5" },
      { japanese: "教室", hiragana: "きょうしつ", english: "classroom", jlpt: "N5" },
      { japanese: "教科書", hiragana: "きょうかしょ", english: "textbook", jlpt: "N4" }
    ],
    sentence: {
      japanese: "先生が漢字を教えてくれました。",
      hiragana: "せんせいがかんじをおしえてくれました。",
      romaji: "Sensei ga kanji wo oshiete kuremashita.",
      english: "The teacher taught me kanji."
    }
  },
  {
    character: "料",
    readings: { on: ["リョウ"], kun: [""] },
    meanings: ["fee", "material", "cooking"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "料理", hiragana: "りょうり", english: "cooking, cuisine", jlpt: "N5" },
      { japanese: "料金", hiragana: "りょうきん", english: "fee, charge", jlpt: "N4" },
      { japanese: "材料", hiragana: "ざいりょう", english: "ingredients", jlpt: "N4" }
    ],
    sentence: {
      japanese: "今晩は魚料理を作ります。",
      hiragana: "こんばんはさかなりょうりをつくります。",
      romaji: "Konban wa sakana ryouri wo tsukurimasu.",
      english: "I'm making fish dishes tonight."
    }
  },
  {
    character: "族",
    readings: { on: ["ゾク"], kun: [""] },
    meanings: ["tribe", "family"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家族", "家族と人", "家族と動作"],
    words: [
      { japanese: "家族", hiragana: "かぞく", english: "family", jlpt: "N5" },
      { japanese: "民族", hiragana: "みんぞく", english: "ethnic group", jlpt: "N3" },
      { japanese: "部族", hiragana: "ぶぞく", english: "tribe", jlpt: "N2" }
    ],
    sentence: {
      japanese: "私の家族は四人です。",
      hiragana: "わたしのかぞくはよにんです。",
      romaji: "Watashi no kazoku wa yo-nin desu.",
      english: "My family is four people."
    }
  },
  {
    character: "机",
    readings: { on: ["キ"], kun: ["つくえ"] },
    meanings: ["desk"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "机", hiragana: "つくえ", english: "desk", jlpt: "N5" },
      { japanese: "机上", hiragana: "きじょう", english: "on the desk", jlpt: "N2" },
      { japanese: "勉強机", hiragana: "べんきょうづくえ", english: "study desk", jlpt: "N4" }
    ],
    sentence: {
      japanese: "机の上を片付けてください。",
      hiragana: "つくえのうえをかたづけてください。",
      romaji: "Tsukue no ue wo katadzukete kudasai.",
      english: "Please tidy up the top of the desk."
    }
  },
  {
    character: "楽",
    readings: { on: ["ラク", "ガク"], kun: ["たの(しい)"] },
    meanings: ["enjoyment", "ease", "music"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "楽しい", hiragana: "たのしい", english: "fun, enjoyable", jlpt: "N5" },
      { japanese: "楽", hiragana: "らく", english: "easy, comfortable", jlpt: "N4" },
      { japanese: "音楽", hiragana: "おんがく", english: "music", jlpt: "N5" }
    ],
    sentence: {
      japanese: "音楽を聴くのが楽しいです。",
      hiragana: "おんがくをきくのがたのしいです。",
      romaji: "Ongaku wo kiku no ga tanoshii desu.",
      english: "Listening to music is fun."
    }
  },
  {
    character: "汁",
    readings: { on: ["ジュウ"], kun: ["しる"] },
    meanings: ["soup", "juice"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["食事", "調味料と食べ物"],
    words: [
      { japanese: "汁", hiragana: "しる", english: "soup, juice", jlpt: "N4" },
      { japanese: "味噌汁", hiragana: "みそしる", english: "miso soup", jlpt: "N5" },
      { japanese: "果汁", hiragana: "かじゅう", english: "fruit juice", jlpt: "N3" }
    ],
    sentence: {
      japanese: "朝は味噌汁を飲みます。",
      hiragana: "あさはみそしるをのみます。",
      romaji: "Asa wa misoshiru wo nomimasu.",
      english: "I drink miso soup in the morning."
    }
  },
  {
    character: "洗",
    readings: { on: ["セン"], kun: ["あら(う)"] },
    meanings: ["wash"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["夜の活動"],
    words: [
      { japanese: "洗う", hiragana: "あらう", english: "to wash", jlpt: "N5" },
      { japanese: "洗濯", hiragana: "せんたく", english: "laundry", jlpt: "N5" },
      { japanese: "洗面所", hiragana: "せんめんじょ", english: "bathroom", jlpt: "N4" }
    ],
    sentence: {
      japanese: "食事の後で皿を洗います。",
      hiragana: "しょくじのあとでさらをあらいます。",
      romaji: "Shokuji no ato de sara wo araimasu.",
      english: "I wash the dishes after meals."
    }
  },
  {
    character: "温",
    readings: { on: ["オン"], kun: ["あたた(かい)"] },
    meanings: ["warm", "temperature"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["よく使う言葉", "描写と動作"],
    words: [
      { japanese: "温かい", hiragana: "あたたかい", english: "warm", jlpt: "N5" },
      { japanese: "温度", hiragana: "おんど", english: "temperature", jlpt: "N4" },
      { japanese: "温泉", hiragana: "おんせん", english: "hot spring", jlpt: "N4" }
    ],
    sentence: {
      japanese: "お風呂の温度がちょうどいいです。",
      hiragana: "おふろのおんどがちょうどいいです。",
      romaji: "Ofuro no ondo ga choudo ii desu.",
      english: "The bath temperature is just right."
    }
  },
  {
    character: "満",
    readings: { on: ["マン"], kun: ["み(ちる)"] },
    meanings: ["full", "satisfied"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["時間と描写"],
    words: [
      { japanese: "満足", hiragana: "まんぞく", english: "satisfaction", jlpt: "N4" },
      { japanese: "満ちる", hiragana: "みちる", english: "to be full", jlpt: "N3" },
      { japanese: "満員", hiragana: "まんいん", english: "full capacity", jlpt: "N3" }
    ],
    sentence: {
      japanese: "結果に満足しています。",
      hiragana: "けっかにまんぞくしています。",
      romaji: "Kekka ni manzoku shite imasu.",
      english: "I'm satisfied with the results."
    }
  },
  {
    character: "牛",
    readings: { on: ["ギュウ"], kun: ["うし"] },
    meanings: ["cow", "beef"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["材料"],
    words: [
      { japanese: "牛", hiragana: "うし", english: "cow", jlpt: "N5" },
      { japanese: "牛肉", hiragana: "ぎゅうにく", english: "beef", jlpt: "N5" },
      { japanese: "牛乳", hiragana: "ぎゅうにゅう", english: "milk", jlpt: "N5" }
    ],
    sentence: {
      japanese: "朝ごはんに牛乳を飲みます。",
      hiragana: "あさごはんにぎゅうにゅうをのみます。",
      romaji: "Asa-gohan ni gyuunyuu wo nomimasu.",
      english: "I drink milk for breakfast."
    }
  },
  {
    character: "理",
    readings: { on: ["リ"], kun: [""] },
    meanings: ["reason", "cooking", "organize"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["料理の動作", "掃除"],
    words: [
      { japanese: "料理", hiragana: "りょうり", english: "cooking, cuisine", jlpt: "N5" },
      { japanese: "理由", hiragana: "りゆう", english: "reason", jlpt: "N4" },
      { japanese: "整理", hiragana: "せいり", english: "organization", jlpt: "N4" }
    ],
    sentence: {
      japanese: "母の料理が一番美味しいです。",
      hiragana: "ははのりょうりがいちばんおいしいです。",
      romaji: "Haha no ryouri ga ichiban oishii desu.",
      english: "My mother's cooking is the most delicious."
    }
  },
  {
    character: "用",
    readings: { on: ["ヨウ"], kun: ["もち(いる)"] },
    meanings: ["use", "business", "prepare"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["朝の動作"],
    words: [
      { japanese: "用事", hiragana: "ようじ", english: "errand, business", jlpt: "N4" },
      { japanese: "使用", hiragana: "しよう", english: "use", jlpt: "N4" },
      { japanese: "用意", hiragana: "ようい", english: "preparation", jlpt: "N4" }
    ],
    sentence: {
      japanese: "明日は用事があります。",
      hiragana: "あしたはようじがあります。",
      romaji: "Ashita wa youji ga arimasu.",
      english: "I have errands tomorrow."
    }
  },
  {
    character: "的",
    readings: { on: ["テキ"], kun: ["まと"] },
    meanings: ["target", "suffix -ic/-al"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "的", hiragana: "てき", english: "-tic, -ical", jlpt: "N4" },
      { japanese: "目的", hiragana: "もくてき", english: "purpose", jlpt: "N4" },
      { japanese: "基本的", hiragana: "きほんてき", english: "basic", jlpt: "N4" }
    ],
    sentence: {
      japanese: "目的地に着きました。",
      hiragana: "もくてきちにつきました。",
      romaji: "Mokutekichi ni tsukimashita.",
      english: "We arrived at our destination."
    }
  },
  {
    character: "着",
    readings: { on: ["チャク"], kun: ["き(る)", "つ(く)"] },
    meanings: ["wear", "arrive", "attach"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["朝の動作", "夜の活動"],
    words: [
      { japanese: "着る", hiragana: "きる", english: "to wear", jlpt: "N5" },
      { japanese: "着く", hiragana: "つく", english: "to arrive", jlpt: "N5" },
      { japanese: "到着", hiragana: "とうちゃく", english: "arrival", jlpt: "N4" }
    ],
    sentence: {
      japanese: "新しい服を着ています。",
      hiragana: "あたらしいふくをきています。",
      romaji: "Atarashii fuku wo kite imasu.",
      english: "I'm wearing new clothes."
    }
  },
  {
    character: "脱",
    readings: { on: ["ダツ"], kun: ["ぬ(ぐ)"] },
    meanings: ["take off", "remove"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["夜の活動"],
    words: [
      { japanese: "脱ぐ", hiragana: "ぬぐ", english: "to take off", jlpt: "N5" },
      { japanese: "脱衣所", hiragana: "だついじょ", english: "changing room", jlpt: "N3" },
      { japanese: "脱出", hiragana: "だっしゅつ", english: "escape", jlpt: "N3" }
    ],
    sentence: {
      japanese: "玄関で靴を脱いでください。",
      hiragana: "げんかんでくつをぬいでください。",
      romaji: "Genkan de kutsu wo nuide kudasai.",
      english: "Please take off your shoes at the entrance."
    }
  },
  {
    character: "茶",
    readings: { on: ["チャ", "サ"], kun: [""] },
    meanings: ["tea"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["食事"],
    words: [
      { japanese: "お茶", hiragana: "おちゃ", english: "tea", jlpt: "N5" },
      { japanese: "茶色", hiragana: "ちゃいろ", english: "brown", jlpt: "N5" },
      { japanese: "紅茶", hiragana: "こうちゃ", english: "black tea", jlpt: "N4" }
    ],
    sentence: {
      japanese: "午後にお茶を飲みましょう。",
      hiragana: "ごごにおちゃをのみましょう。",
      romaji: "Gogo ni ocha wo nomimashou.",
      english: "Let's drink tea in the afternoon."
    }
  },
  {
    character: "菜",
    readings: { on: ["サイ"], kun: ["な"] },
    meanings: ["vegetable", "greens"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["材料"],
    words: [
      { japanese: "野菜", hiragana: "やさい", english: "vegetable", jlpt: "N5" },
      { japanese: "菜食", hiragana: "さいしょく", english: "vegetarian diet", jlpt: "N2" },
      { japanese: "白菜", hiragana: "はくさい", english: "Chinese cabbage", jlpt: "N3" }
    ],
    sentence: {
      japanese: "野菜をたくさん食べてください。",
      hiragana: "やさいをたくさんたべてください。",
      romaji: "Yasai wo takusan tabete kudasai.",
      english: "Please eat lots of vegetables."
    }
  },
  {
    character: "計",
    readings: { on: ["ケイ"], kun: ["はか(る)"] },
    meanings: ["measure", "plan", "clock"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["時間と朝"],
    words: [
      { japanese: "時計", hiragana: "とけい", english: "clock, watch", jlpt: "N5" },
      { japanese: "計画", hiragana: "けいかく", english: "plan", jlpt: "N4" },
      { japanese: "合計", hiragana: "ごうけい", english: "total", jlpt: "N3" }
    ],
    sentence: {
      japanese: "時計が止まっています。",
      hiragana: "とけいがとまっています。",
      romaji: "Tokei ga tomatte imasu.",
      english: "The clock has stopped."
    }
  },
  {
    character: "起",
    readings: { on: ["キ"], kun: ["お(きる)"] },
    meanings: ["wake up", "get up", "occur"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["朝の動作"],
    words: [
      { japanese: "起きる", hiragana: "おきる", english: "to wake up", jlpt: "N5" },
      { japanese: "起こす", hiragana: "おこす", english: "to wake (someone)", jlpt: "N4" },
      { japanese: "起立", hiragana: "きりつ", english: "stand up", jlpt: "N3" }
    ],
    sentence: {
      japanese: "毎朝６時に起きます。",
      hiragana: "まいあさろくじにおきます。",
      romaji: "Maiasa roku-ji ni okimasu.",
      english: "I wake up at 6 o'clock every morning."
    }
  },
  {
    character: "部",
    readings: { on: ["ブ"], kun: ["へ"] },
    meanings: ["section", "department", "room"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "部屋", hiragana: "へや", english: "room", jlpt: "N5" },
      { japanese: "全部", hiragana: "ぜんぶ", english: "all, everything", jlpt: "N4" },
      { japanese: "部分", hiragana: "ぶぶん", english: "part, portion", jlpt: "N4" }
    ],
    sentence: {
      japanese: "この部分が難しいです。",
      hiragana: "このぶぶんがむずかしいです。",
      romaji: "Kono bubun ga muzukashii desu.",
      english: "This part is difficult."
    }
  },
  {
    character: "重",
    readings: { on: ["ジュウ"], kun: ["おも(い)"] },
    meanings: ["heavy", "important"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "重い", hiragana: "おもい", english: "heavy", jlpt: "N5" },
      { japanese: "重要", hiragana: "じゅうよう", english: "important", jlpt: "N4" },
      { japanese: "重さ", hiragana: "おもさ", english: "weight", jlpt: "N4" }
    ],
    sentence: {
      japanese: "この荷物は重いですね。",
      hiragana: "このにもつはおもいですね。",
      romaji: "Kono nimotsu wa omoi desu ne.",
      english: "This luggage is heavy, isn't it?"
    }
  },
  {
    character: "野",
    readings: { on: ["ヤ"], kun: ["の"] },
    meanings: ["field", "wild", "vegetable"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["材料"],
    words: [
      { japanese: "野菜", hiragana: "やさい", english: "vegetable", jlpt: "N5" },
      { japanese: "野球", hiragana: "やきゅう", english: "baseball", jlpt: "N5" },
      { japanese: "平野", hiragana: "へいや", english: "plain, field", jlpt: "N3" }
    ],
    sentence: {
      japanese: "野菜と魚を買いました。",
      hiragana: "やさいとさかなをかいました。",
      romaji: "Yasai to sakana wo kaimashita.",
      english: "I bought vegetables and fish."
    }
  },
  {
    character: "開",
    readings: { on: ["カイ"], kun: ["あ(く)", "ひら(く)"] },
    meanings: ["open"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["朝の動作"],
    words: [
      { japanese: "開く", hiragana: "あく", english: "to open", jlpt: "N5" },
      { japanese: "開ける", hiragana: "あける", english: "to open", jlpt: "N5" },
      { japanese: "開始", hiragana: "かいし", english: "start", jlpt: "N4" }
    ],
    sentence: {
      japanese: "窓を開けてもいいですか。",
      hiragana: "まどをあけてもいいですか。",
      romaji: "Mado wo akete mo ii desu ka.",
      english: "May I open the window?"
    }
  },
  {
    character: "集",
    readings: { on: ["シュウ"], kun: ["あつ(まる)"] },
    meanings: ["gather", "collect"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["朝の動作", "家族と動作"],
    words: [
      { japanese: "集める", hiragana: "あつめる", english: "to collect", jlpt: "N4" },
      { japanese: "集まる", hiragana: "あつまる", english: "to gather", jlpt: "N4" },
      { japanese: "集中", hiragana: "しゅうちゅう", english: "concentration", jlpt: "N3" }
    ],
    sentence: {
      japanese: "友達が家に集まりました。",
      hiragana: "ともだちがいえにあつまりました。",
      romaji: "Tomodachi ga ie ni atsumarimashita.",
      english: "Friends gathered at my house."
    }
  },
  {
    character: "風",
    readings: { on: ["フウ"], kun: ["かぜ"] },
    meanings: ["wind", "style", "bath"],
    jlpt: "N4",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "風", hiragana: "かぜ", english: "wind", jlpt: "N4" },
      { japanese: "風呂", hiragana: "ふろ", english: "bath", jlpt: "N5" },
      { japanese: "台風", hiragana: "たいふう", english: "typhoon", jlpt: "N4" }
    ],
    sentence: {
      japanese: "夜にお風呂に入ります。",
      hiragana: "よるにおふろにはいります。",
      romaji: "Yoru ni ofuro ni hairimasu.",
      english: "I take a bath at night."
    }
  },

  // ===== N3 Kanji =====

  {
    character: "丁",
    readings: { on: ["チョウ"], kun: ["てい"] },
    meanings: ["counter", "kitchen knife"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["調理器具"],
    words: [
      { japanese: "丁寧", hiragana: "ていねい", english: "polite, careful", jlpt: "N4" },
      { japanese: "包丁", hiragana: "ほうちょう", english: "kitchen knife", jlpt: "N3" },
      { japanese: "一丁", hiragana: "いっちょう", english: "one block, one item", jlpt: "N3" }
    ],
    sentence: {
      japanese: "包丁で野菜を切ります。",
      hiragana: "ほうちょうでやさいをきります。",
      romaji: "Houchou de yasai wo kirimasu.",
      english: "I cut vegetables with a kitchen knife."
    }
  },
  {
    character: "付",
    readings: { on: ["フ"], kun: ["つ(く)", "つ(ける)"] },
    meanings: ["attach", "tidy up"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["掃除"],
    words: [
      { japanese: "付ける", hiragana: "つける", english: "to attach", jlpt: "N5" },
      { japanese: "付く", hiragana: "つく", english: "to be attached", jlpt: "N5" },
      { japanese: "受付", hiragana: "うけつけ", english: "reception", jlpt: "N4" }
    ],
    sentence: {
      japanese: "メモを冷蔵庫に付けました。",
      hiragana: "めもをれいぞうこにつけました。",
      romaji: "Memo wo reizouko ni tsukemashita.",
      english: "I attached a memo to the refrigerator."
    }
  },
  {
    character: "伝",
    readings: { on: ["デン"], kun: ["つた(える)"] },
    meanings: ["transmit", "traditional"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "伝える", hiragana: "つたえる", english: "to convey", jlpt: "N4" },
      { japanese: "伝統", hiragana: "でんとう", english: "tradition", jlpt: "N3" },
      { japanese: "伝言", hiragana: "でんごん", english: "message", jlpt: "N3" }
    ],
    sentence: {
      japanese: "母に伝言を伝えてください。",
      hiragana: "ははにでんごんをつたえてください。",
      romaji: "Haha ni dengon wo tsutaete kudasai.",
      english: "Please convey the message to my mother."
    }
  },
  {
    character: "備",
    readings: { on: ["ビ"], kun: ["そな(える)"] },
    meanings: ["prepare", "provide"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["朝の動作", "よく使う言葉"],
    words: [
      { japanese: "準備", hiragana: "じゅんび", english: "preparation", jlpt: "N4" },
      { japanese: "設備", hiragana: "せつび", english: "equipment", jlpt: "N3" },
      { japanese: "予備", hiragana: "よび", english: "reserve, spare", jlpt: "N3" }
    ],
    sentence: {
      japanese: "明日の準備をしています。",
      hiragana: "あしたのじゅんびをしています。",
      romaji: "Ashita no junbi wo shite imasu.",
      english: "I'm preparing for tomorrow."
    }
  },
  {
    character: "冷",
    readings: { on: ["レイ"], kun: ["つめ(たい)", "さ(める)"] },
    meanings: ["cold", "refrigerator"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["家庭用品"],
    words: [
      { japanese: "冷たい", hiragana: "つめたい", english: "cold", jlpt: "N5" },
      { japanese: "冷蔵庫", hiragana: "れいぞうこ", english: "refrigerator", jlpt: "N5" },
      { japanese: "冷凍", hiragana: "れいとう", english: "freezing", jlpt: "N3" }
    ],
    sentence: {
      japanese: "冷蔵庫に食べ物を入れます。",
      hiragana: "れいぞうこにたべものをいれます。",
      romaji: "Reizouko ni tabemono wo iremasu.",
      english: "I put food in the refrigerator."
    }
  },
  {
    character: "初",
    readings: { on: ["ショ"], kun: ["はじ(め)", "はつ"] },
    meanings: ["first", "beginning"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "初めて", hiragana: "はじめて", english: "for the first time", jlpt: "N5" },
      { japanese: "最初", hiragana: "さいしょ", english: "first, beginning", jlpt: "N4" },
      { japanese: "初級", hiragana: "しょきゅう", english: "beginner level", jlpt: "N3" }
    ],
    sentence: {
      japanese: "初めてこの料理を作りました。",
      hiragana: "はじめてこのりょうりをつくりました。",
      romaji: "Hajimete kono ryouri wo tsukurimashita.",
      english: "I made this dish for the first time."
    }
  },
  {
    character: "加",
    readings: { on: ["カ"], kun: ["くわ(える)"] },
    meanings: ["add", "include"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "加える", hiragana: "くわえる", english: "to add", jlpt: "N3" },
      { japanese: "参加", hiragana: "さんか", english: "participation", jlpt: "N4" },
      { japanese: "追加", hiragana: "ついか", english: "addition", jlpt: "N3" }
    ],
    sentence: {
      japanese: "料理に塩を加えます。",
      hiragana: "りょうりにしおをくわえます。",
      romaji: "Ryouri ni shio wo kuwaemasu.",
      english: "I add salt to the dish."
    }
  },
  {
    character: "協",
    readings: { on: ["キョウ"], kun: [""] },
    meanings: ["cooperation"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["よく使う言葉", "家族と動作"],
    words: [
      { japanese: "協力", hiragana: "きょうりょく", english: "cooperation", jlpt: "N3" },
      { japanese: "協会", hiragana: "きょうかい", english: "association", jlpt: "N3" },
      { japanese: "協定", hiragana: "きょうてい", english: "agreement", jlpt: "N2" }
    ],
    sentence: {
      japanese: "家族で協力して掃除します。",
      hiragana: "かぞくできょうりょくしてそうじします。",
      romaji: "Kazoku de kyouryoku shite souji shimasu.",
      english: "The family cooperates to clean."
    }
  },
  {
    character: "器",
    readings: { on: ["キ"], kun: ["うつわ"] },
    meanings: ["vessel", "dish"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["食事"],
    words: [
      { japanese: "器", hiragana: "うつわ", english: "container, dish", jlpt: "N3" },
      { japanese: "食器", hiragana: "しょっき", english: "tableware", jlpt: "N3" },
      { japanese: "機器", hiragana: "きき", english: "equipment", jlpt: "N2" }
    ],
    sentence: {
      japanese: "食器を洗って棚に戻します。",
      hiragana: "しょっきをあらってたなにもどします。",
      romaji: "Shokki wo aratte tana ni modoshimasu.",
      english: "I wash the dishes and put them back on the shelf."
    }
  },
  {
    character: "娘",
    readings: { on: ["ジョウ"], kun: ["むすめ"] },
    meanings: ["daughter"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["家族", "家族と人"],
    words: [
      { japanese: "娘", hiragana: "むすめ", english: "daughter", jlpt: "N5" },
      { japanese: "お嬢さん", hiragana: "おじょうさん", english: "daughter (polite)", jlpt: "N4" },
      { japanese: "娘さん", hiragana: "むすめさん", english: "daughter (polite)", jlpt: "N4" }
    ],
    sentence: {
      japanese: "娘は部屋で宿題をしています。",
      hiragana: "むすめはへやでしゅくだいをしています。",
      romaji: "Musume wa heya de shukudai wo shite imasu.",
      english: "My daughter is doing homework in her room."
    }
  },
  {
    character: "居",
    readings: { on: ["キョ"], kun: ["い(る)"] },
    meanings: ["reside", "living room"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "居る", hiragana: "いる", english: "to be (animate)", jlpt: "N5" },
      { japanese: "居間", hiragana: "いま", english: "living room", jlpt: "N4" },
      { japanese: "居住", hiragana: "きょじゅう", english: "residence", jlpt: "N3" }
    ],
    sentence: {
      japanese: "居間でテレビを見ます。",
      hiragana: "いまでてれびをみます。",
      romaji: "Ima de terebi wo mimasu.",
      english: "I watch TV in the living room."
    }
  },
  {
    character: "弁",
    readings: { on: ["ベン"], kun: [""] },
    meanings: ["valve", "speech", "lunch box"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["食事"],
    words: [
      { japanese: "弁当", hiragana: "べんとう", english: "boxed lunch", jlpt: "N5" },
      { japanese: "弁護士", hiragana: "べんごし", english: "lawyer", jlpt: "N3" },
      { japanese: "答弁", hiragana: "とうべん", english: "answer, reply", jlpt: "N2" }
    ],
    sentence: {
      japanese: "お弁当を作って持って行きます。",
      hiragana: "おべんとうをつくってもっていきます。",
      romaji: "Obentou wo tsukutte motte ikimasu.",
      english: "I make a boxed lunch and take it with me."
    }
  },
  {
    character: "当",
    readings: { on: ["トウ"], kun: ["あ(たる)"] },
    meanings: ["hit", "appropriate", "lunch box", "in charge"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["食事", "家族と動作"],
    words: [
      { japanese: "当たる", hiragana: "あたる", english: "to hit", jlpt: "N4" },
      { japanese: "本当", hiragana: "ほんとう", english: "truth, really", jlpt: "N5" },
      { japanese: "弁当", hiragana: "べんとう", english: "boxed lunch", jlpt: "N5" }
    ],
    sentence: {
      japanese: "本当にきれいな庭ですね。",
      hiragana: "ほんとうにきれいなにわですね。",
      romaji: "Hontou ni kirei na niwa desu ne.",
      english: "It's a really beautiful garden, isn't it?"
    }
  },
  {
    character: "抜",
    readings: { on: ["バツ"], kun: ["ぬ(く)"] },
    meanings: ["pull out", "extract"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["庭と外"],
    words: [
      { japanese: "抜く", hiragana: "ぬく", english: "to pull out", jlpt: "N3" },
      { japanese: "抜ける", hiragana: "ぬける", english: "to come out", jlpt: "N3" },
      { japanese: "選抜", hiragana: "せんばつ", english: "selection", jlpt: "N2" }
    ],
    sentence: {
      japanese: "コンセントを抜いてください。",
      hiragana: "こんせんとをぬいてください。",
      romaji: "Konsento wo nuite kudasai.",
      english: "Please unplug the outlet."
    }
  },
  {
    character: "担",
    readings: { on: ["タン"], kun: ["かつ(ぐ)", "にな(う)"] },
    meanings: ["carry", "in charge"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["家族と動作"],
    words: [
      { japanese: "担当", hiragana: "たんとう", english: "in charge of", jlpt: "N3" },
      { japanese: "担ぐ", hiragana: "かつぐ", english: "to carry on shoulder", jlpt: "N3" },
      { japanese: "負担", hiragana: "ふたん", english: "burden", jlpt: "N3" }
    ],
    sentence: {
      japanese: "今週は私が料理を担当します。",
      hiragana: "こんしゅうはわたしがりょうりをたんとうします。",
      romaji: "Konshuu wa watashi ga ryouri wo tantou shimasu.",
      english: "I'm in charge of cooking this week."
    }
  },
  {
    character: "拭",
    readings: { on: ["ショク"], kun: ["ふ(く)"] },
    meanings: ["wipe", "dry"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["掃除"],
    words: [
      { japanese: "拭く", hiragana: "ふく", english: "to wipe", jlpt: "N3" },
      { japanese: "拭き取る", hiragana: "ふきとる", english: "to wipe off", jlpt: "N3" },
      { japanese: "払拭", hiragana: "ふっしょく", english: "wiping out", jlpt: "N1" }
    ],
    sentence: {
      japanese: "テーブルを布で拭きます。",
      hiragana: "てーぶるをぬのでふきます。",
      romaji: "Teeburu wo nuno de fukimasu.",
      english: "I wipe the table with a cloth."
    }
  },
  {
    character: "捨",
    readings: { on: ["シャ"], kun: ["す(てる)"] },
    meanings: ["throw away", "discard"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["家族と動作"],
    words: [
      { japanese: "捨てる", hiragana: "すてる", english: "to throw away", jlpt: "N5" },
      { japanese: "見捨てる", hiragana: "みすてる", english: "to abandon", jlpt: "N3" },
      { japanese: "使い捨て", hiragana: "つかいすて", english: "disposable", jlpt: "N3" }
    ],
    sentence: {
      japanese: "ゴミを捨てに行きましょう。",
      hiragana: "ごみをすてにいきましょう。",
      romaji: "Gomi wo sute ni ikimashou.",
      english: "Let's go throw away the garbage."
    }
  },
  {
    character: "揚",
    readings: { on: ["ヨウ"], kun: ["あ(げる)", "あ(がる)"] },
    meanings: ["fry", "raise"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "揚げる", hiragana: "あげる", english: "to deep-fry", jlpt: "N3" },
      { japanese: "唐揚げ", hiragana: "からあげ", english: "fried chicken", jlpt: "N3" },
      { japanese: "揚げ物", hiragana: "あげもの", english: "fried food", jlpt: "N3" }
    ],
    sentence: {
      japanese: "夕食に鶏肉を揚げます。",
      hiragana: "ゆうしょくにとりにくをあげます。",
      romaji: "Yuushoku ni toriniku wo agemasu.",
      english: "I'm frying chicken for dinner."
    }
  },
  {
    character: "整",
    readings: { on: ["セイ"], kun: ["ととの(える)"] },
    meanings: ["organize", "arrange"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["掃除"],
    words: [
      { japanese: "整理", hiragana: "せいり", english: "organize", jlpt: "N3" },
      { japanese: "整える", hiragana: "ととのえる", english: "to arrange", jlpt: "N3" },
      { japanese: "整頓", hiragana: "せいとん", english: "tidying up", jlpt: "N3" }
    ],
    sentence: {
      japanese: "部屋を整理整頓しましょう。",
      hiragana: "へやをせいりせいとんしましょう。",
      romaji: "Heya wo seiri seiton shimashou.",
      english: "Let's organize and tidy up the room."
    }
  },
  {
    character: "替",
    readings: { on: ["タイ"], kun: ["か(える)"] },
    meanings: ["exchange", "replace", "change"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["朝の動作", "夜の活動"],
    words: [
      { japanese: "替える", hiragana: "かえる", english: "to replace", jlpt: "N3" },
      { japanese: "両替", hiragana: "りょうがえ", english: "money exchange", jlpt: "N3" },
      { japanese: "交替", hiragana: "こうたい", english: "alternation", jlpt: "N3" }
    ],
    sentence: {
      japanese: "電球を新しいのに替えました。",
      hiragana: "でんきゅうをあたらしいのにかえました。",
      romaji: "Denkyuu wo atarashii no ni kaemashita.",
      english: "I replaced the light bulb with a new one."
    }
  },
  {
    character: "最",
    readings: { on: ["サイ"], kun: ["もっと(も)"] },
    meanings: ["most", "utmost"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "最も", hiragana: "もっとも", english: "most", jlpt: "N3" },
      { japanese: "最初", hiragana: "さいしょ", english: "first", jlpt: "N4" },
      { japanese: "最近", hiragana: "さいきん", english: "recently", jlpt: "N5" }
    ],
    sentence: {
      japanese: "最近忙しくなりました。",
      hiragana: "さいきんいそがしくなりました。",
      romaji: "Saikin isogashiku narimashita.",
      english: "I've become busy recently."
    }
  },
  {
    character: "材",
    readings: { on: ["ザイ"], kun: [""] },
    meanings: ["material", "ingredient"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["材料"],
    words: [
      { japanese: "材料", hiragana: "ざいりょう", english: "ingredients", jlpt: "N4" },
      { japanese: "教材", hiragana: "きょうざい", english: "teaching materials", jlpt: "N3" },
      { japanese: "題材", hiragana: "だいざい", english: "subject matter", jlpt: "N2" }
    ],
    sentence: {
      japanese: "料理の材料を買いました。",
      hiragana: "りょうりのざいりょうをかいました。",
      romaji: "Ryouri no zairyou wo kaimashita.",
      english: "I bought ingredients for cooking."
    }
  },
  {
    character: "柔",
    readings: { on: ["ジュウ"], kun: ["やわ(らかい)"] },
    meanings: ["soft", "tender"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "柔らかい", hiragana: "やわらかい", english: "soft", jlpt: "N4" },
      { japanese: "柔道", hiragana: "じゅうどう", english: "judo", jlpt: "N4" },
      { japanese: "柔軟", hiragana: "じゅうなん", english: "flexible", jlpt: "N3" }
    ],
    sentence: {
      japanese: "この肉は柔らかくて美味しいです。",
      hiragana: "このにくはやわらかくておいしいです。",
      romaji: "Kono niku wa yawarakakute oishii desu.",
      english: "This meat is soft and delicious."
    }
  },
  {
    character: "機",
    readings: { on: ["キ"], kun: ["はた"] },
    meanings: ["machine"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["掃除"],
    words: [
      { japanese: "機械", hiragana: "きかい", english: "machine", jlpt: "N4" },
      { japanese: "飛行機", hiragana: "ひこうき", english: "airplane", jlpt: "N5" },
      { japanese: "機会", hiragana: "きかい", english: "opportunity", jlpt: "N3" }
    ],
    sentence: {
      japanese: "洗濯機が壊れてしまいました。",
      hiragana: "せんたくきがこわれてしまいました。",
      romaji: "Sentakuki ga kowarete shimaimashita.",
      english: "The washing machine broke."
    }
  },
  {
    character: "汚",
    readings: { on: ["オ"], kun: ["きたな(い)", "よご(れる)"] },
    meanings: ["dirty", "polluted"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["家庭用品"],
    words: [
      { japanese: "汚い", hiragana: "きたない", english: "dirty", jlpt: "N5" },
      { japanese: "汚れる", hiragana: "よごれる", english: "to get dirty", jlpt: "N3" },
      { japanese: "汚す", hiragana: "よごす", english: "to make dirty", jlpt: "N3" }
    ],
    sentence: {
      japanese: "部屋が汚れているので掃除します。",
      hiragana: "へやがよごれているのでそうじします。",
      romaji: "Heya ga yogorete iru node souji shimasu.",
      english: "I'll clean because the room is dirty."
    }
  },
  {
    character: "油",
    readings: { on: ["ユ"], kun: ["あぶら"] },
    meanings: ["oil", "grease"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["材料", "調味料と食べ物", "家庭用品"],
    words: [
      { japanese: "油", hiragana: "あぶら", english: "oil", jlpt: "N4" },
      { japanese: "石油", hiragana: "せきゆ", english: "petroleum", jlpt: "N3" },
      { japanese: "醤油", hiragana: "しょうゆ", english: "soy sauce", jlpt: "N5" }
    ],
    sentence: {
      japanese: "フライパンに油を入れます。",
      hiragana: "ふらいぱんにあぶらをいれます。",
      romaji: "Furaipan ni abura wo iremasu.",
      english: "I put oil in the frying pan."
    }
  },
  {
    character: "準",
    readings: { on: ["ジュン"], kun: [""] },
    meanings: ["standard", "prepare"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["朝の動作", "よく使う言葉"],
    words: [
      { japanese: "準備", hiragana: "じゅんび", english: "preparation", jlpt: "N4" },
      { japanese: "基準", hiragana: "きじゅん", english: "standard", jlpt: "N3" },
      { japanese: "水準", hiragana: "すいじゅん", english: "level, standard", jlpt: "N3" }
    ],
    sentence: {
      japanese: "朝食の準備ができました。",
      hiragana: "ちょうしょくのじゅんびができました。",
      romaji: "Choushoku no junbi ga dekimashita.",
      english: "Breakfast preparation is done."
    }
  },
  {
    character: "溶",
    readings: { on: ["ヨウ"], kun: ["と(ける)", "と(かす)"] },
    meanings: ["dissolve", "melt"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "溶ける", hiragana: "とける", english: "to melt, dissolve", jlpt: "N3" },
      { japanese: "溶かす", hiragana: "とかす", english: "to melt (something)", jlpt: "N3" },
      { japanese: "溶液", hiragana: "ようえき", english: "solution (chemistry)", jlpt: "N2" }
    ],
    sentence: {
      japanese: "砂糖が水に溶けました。",
      hiragana: "さとうがみずにとけました。",
      romaji: "Satou ga mizu ni tokemashita.",
      english: "The sugar dissolved in the water."
    }
  },
  {
    character: "炒",
    readings: { on: ["ショウ"], kun: ["いた(める)"] },
    meanings: ["stir-fry"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "炒める", hiragana: "いためる", english: "to stir-fry", jlpt: "N3" },
      { japanese: "炒め物", hiragana: "いためもの", english: "stir-fried dish", jlpt: "N3" },
      { japanese: "炒飯", hiragana: "チャーハン", english: "fried rice", jlpt: "N3" }
    ],
    sentence: {
      japanese: "野菜を炒めて食べます。",
      hiragana: "やさいをいためてたべます。",
      romaji: "Yasai wo itamete tabemasu.",
      english: "I stir-fry vegetables and eat them."
    }
  },
  {
    character: "焼",
    readings: { on: ["ショウ"], kun: ["や(く)"] },
    meanings: ["bake", "grill"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["食事"],
    words: [
      { japanese: "焼く", hiragana: "やく", english: "to bake, grill", jlpt: "N5" },
      { japanese: "焼ける", hiragana: "やける", english: "to be baked", jlpt: "N4" },
      { japanese: "焼き鳥", hiragana: "やきとり", english: "grilled chicken", jlpt: "N4" }
    ],
    sentence: {
      japanese: "パンを焼いて朝食にします。",
      hiragana: "ぱんをやいてちょうしょくにします。",
      romaji: "Pan wo yaite choushoku ni shimasu.",
      english: "I toast bread for breakfast."
    }
  },
  {
    character: "片",
    readings: { on: ["ヘン"], kun: ["かた"] },
    meanings: ["one-sided", "片付ける"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["掃除"],
    words: [
      { japanese: "片方", hiragana: "かたほう", english: "one side", jlpt: "N4" },
      { japanese: "片付ける", hiragana: "かたづける", english: "to tidy up", jlpt: "N5" },
      { japanese: "片道", hiragana: "かたみち", english: "one way", jlpt: "N4" }
    ],
    sentence: {
      japanese: "食事の後で片付けます。",
      hiragana: "しょくじのあとでかたづけます。",
      romaji: "Shokuji no ato de katadzukemasu.",
      english: "I tidy up after meals."
    }
  },
  {
    character: "皮",
    readings: { on: ["ヒ"], kun: ["かわ"] },
    meanings: ["skin", "peel"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["材料"],
    words: [
      { japanese: "皮", hiragana: "かわ", english: "skin, peel", jlpt: "N3" },
      { japanese: "革", hiragana: "かわ", english: "leather", jlpt: "N3" },
      { japanese: "皮膚", hiragana: "ひふ", english: "skin (body)", jlpt: "N3" }
    ],
    sentence: {
      japanese: "リンゴの皮をむいてください。",
      hiragana: "りんごのかわをむいてください。",
      romaji: "Ringo no kawa wo muite kudasai.",
      english: "Please peel the apple skin."
    }
  },
  {
    character: "磨",
    readings: { on: ["マ"], kun: ["みが(く)"] },
    meanings: ["polish", "brush"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["夜の活動", "掃除"],
    words: [
      { japanese: "磨く", hiragana: "みがく", english: "to polish, brush", jlpt: "N3" },
      { japanese: "研磨", hiragana: "けんま", english: "polishing", jlpt: "N2" },
      { japanese: "歯磨き", hiragana: "はみがき", english: "tooth brushing", jlpt: "N4" }
    ],
    sentence: {
      japanese: "毎晩歯を磨きます。",
      hiragana: "まいばんはをみがきます。",
      romaji: "Maiban ha wo migakimasu.",
      english: "I brush my teeth every night."
    }
  },
  {
    character: "笑",
    readings: { on: ["ショウ"], kun: ["わら(う)"] },
    meanings: ["laugh", "smile"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "笑う", hiragana: "わらう", english: "to laugh", jlpt: "N5" },
      { japanese: "笑顔", hiragana: "えがお", english: "smiling face", jlpt: "N3" },
      { japanese: "微笑む", hiragana: "ほほえむ", english: "to smile", jlpt: "N3" }
    ],
    sentence: {
      japanese: "家族で笑いながら食事をします。",
      hiragana: "かぞくでわらいながらしょくじをします。",
      romaji: "Kazoku de warai nagara shokuji wo shimasu.",
      english: "We eat meals while laughing with family."
    }
  },
  {
    character: "箱",
    readings: { on: ["ソウ"], kun: ["はこ"] },
    meanings: ["box"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["家庭用品"],
    words: [
      { japanese: "箱", hiragana: "はこ", english: "box", jlpt: "N5" },
      { japanese: "郵便箱", hiragana: "ゆうびんばこ", english: "mailbox", jlpt: "N4" },
      { japanese: "ゴミ箱", hiragana: "ごみばこ", english: "trash can", jlpt: "N4" }
    ],
    sentence: {
      japanese: "箱の中に本を入れました。",
      hiragana: "はこのなかにほんをいれました。",
      romaji: "Hako no naka ni hon wo iremashita.",
      english: "I put books in the box."
    }
  },
  {
    character: "粉",
    readings: { on: ["フン"], kun: ["こな", "こ"] },
    meanings: ["flour", "powder"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["材料"],
    words: [
      { japanese: "粉", hiragana: "こな", english: "powder, flour", jlpt: "N3" },
      { japanese: "小麦粉", hiragana: "こむぎこ", english: "flour", jlpt: "N3" },
      { japanese: "粉末", hiragana: "ふんまつ", english: "powder", jlpt: "N2" }
    ],
    sentence: {
      japanese: "小麦粉でパンを作ります。",
      hiragana: "こむぎこでぱんをつくります。",
      romaji: "Komugiko de pan wo tsukurimasu.",
      english: "I make bread with flour."
    }
  },
  {
    character: "統",
    readings: { on: ["トウ"], kun: ["す(べる)"] },
    meanings: ["tradition", "unite"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "統一", hiragana: "とういつ", english: "unification", jlpt: "N3" },
      { japanese: "伝統", hiragana: "でんとう", english: "tradition", jlpt: "N3" },
      { japanese: "統計", hiragana: "とうけい", english: "statistics", jlpt: "N2" }
    ],
    sentence: {
      japanese: "我が家の伝統料理です。",
      hiragana: "わがやのでんとうりょうりです。",
      romaji: "Wagaya no dentou ryouri desu.",
      english: "It's our family's traditional dish."
    }
  },
  {
    character: "肉",
    readings: { on: ["ニク"], kun: [""] },
    meanings: ["meat", "flesh"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["材料"],
    words: [
      { japanese: "肉", hiragana: "にく", english: "meat", jlpt: "N5" },
      { japanese: "牛肉", hiragana: "ぎゅうにく", english: "beef", jlpt: "N5" },
      { japanese: "肉体", hiragana: "にくたい", english: "body, flesh", jlpt: "N3" }
    ],
    sentence: {
      japanese: "今日は肉を買って帰ります。",
      hiragana: "きょうはにくをかってかえります。",
      romaji: "Kyou wa niku wo katte kaerimasu.",
      english: "I'll buy meat and go home today."
    }
  },
  {
    character: "良",
    readings: { on: ["リョウ"], kun: ["よ(い)"] },
    meanings: ["good", "excellent"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "良い", hiragana: "よい", english: "good", jlpt: "N5" },
      { japanese: "良く", hiragana: "よく", english: "well, often", jlpt: "N5" },
      { japanese: "改良", hiragana: "かいりょう", english: "improvement", jlpt: "N3" }
    ],
    sentence: {
      japanese: "良い天気なので洗濯します。",
      hiragana: "よいてんきなのでせんたくします。",
      romaji: "Yoi tenki nanode sentaku shimasu.",
      english: "I'll do laundry because the weather is good."
    }
  },
  {
    character: "草",
    readings: { on: ["ソウ"], kun: ["くさ"] },
    meanings: ["grass", "weed"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["庭と外"],
    words: [
      { japanese: "草", hiragana: "くさ", english: "grass", jlpt: "N4" },
      { japanese: "雑草", hiragana: "ざっそう", english: "weed", jlpt: "N2" },
      { japanese: "草花", hiragana: "くさばな", english: "flowering plant", jlpt: "N3" }
    ],
    sentence: {
      japanese: "庭の草を抜きました。",
      hiragana: "にわのくさをぬきました。",
      romaji: "Niwa no kusa wo nukimashita.",
      english: "I pulled the grass in the garden."
    }
  },
  {
    character: "落",
    readings: { on: ["ラク"], kun: ["お(ちる)", "お(とす)"] },
    meanings: ["fall", "drop"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["庭と外"],
    words: [
      { japanese: "落ちる", hiragana: "おちる", english: "to fall", jlpt: "N4" },
      { japanese: "落とす", hiragana: "おとす", english: "to drop", jlpt: "N4" },
      { japanese: "落ち着く", hiragana: "おちつく", english: "to calm down", jlpt: "N3" }
    ],
    sentence: {
      japanese: "葉が地面に落ちました。",
      hiragana: "はがじめんにおちました。",
      romaji: "Ha ga jimen ni ochimashita.",
      english: "The leaves fell to the ground."
    }
  },
  {
    character: "葉",
    readings: { on: ["ヨウ"], kun: ["は"] },
    meanings: ["leaf"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["庭と外"],
    words: [
      { japanese: "葉", hiragana: "は", english: "leaf", jlpt: "N3" },
      { japanese: "言葉", hiragana: "ことば", english: "word, language", jlpt: "N5" },
      { japanese: "葉っぱ", hiragana: "はっぱ", english: "leaf (casual)", jlpt: "N3" }
    ],
    sentence: {
      japanese: "木の葉が色づいています。",
      hiragana: "きのはがいろづいています。",
      romaji: "Ki no ha ga irozuite imasu.",
      english: "The tree leaves are changing color."
    }
  },
  {
    character: "薄",
    readings: { on: ["ハク"], kun: ["うす(い)"] },
    meanings: ["thin", "weak"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "薄い", hiragana: "うすい", english: "thin", jlpt: "N4" },
      { japanese: "薄暗い", hiragana: "うすぐらい", english: "dim, gloomy", jlpt: "N3" },
      { japanese: "薄れる", hiragana: "うすれる", english: "to fade", jlpt: "N3" }
    ],
    sentence: {
      japanese: "この紙は薄いので注意してください。",
      hiragana: "このかみはうすいのでちゅういしてください。",
      romaji: "Kono kami wa usui node chuui shite kudasai.",
      english: "Please be careful because this paper is thin."
    }
  },
  {
    character: "衣",
    readings: { on: ["イ"], kun: ["ころも"] },
    meanings: ["clothing", "batter"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["材料"],
    words: [
      { japanese: "衣服", hiragana: "いふく", english: "clothing", jlpt: "N3" },
      { japanese: "衣類", hiragana: "いるい", english: "clothes", jlpt: "N3" },
      { japanese: "浴衣", hiragana: "ゆかた", english: "yukata", jlpt: "N4" }
    ],
    sentence: {
      japanese: "衣類を洗濯機に入れます。",
      hiragana: "いるいをせんたくきにいれます。",
      romaji: "Irui wo sentakuki ni iremasu.",
      english: "I put clothes in the washing machine."
    }
  },
  {
    character: "袋",
    readings: { on: ["タイ"], kun: ["ふくろ"] },
    meanings: ["bag", "sack"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["家庭用品"],
    words: [
      { japanese: "袋", hiragana: "ふくろ", english: "bag", jlpt: "N4" },
      { japanese: "ビニール袋", hiragana: "びにーるぶくろ", english: "plastic bag", jlpt: "N4" },
      { japanese: "紙袋", hiragana: "かみぶくろ", english: "paper bag", jlpt: "N4" }
    ],
    sentence: {
      japanese: "ゴミ袋を買いに行きます。",
      hiragana: "ごみぶくろをかいにいきます。",
      romaji: "Gomi bukuro wo kai ni ikimasu.",
      english: "I'm going to buy garbage bags."
    }
  },
  {
    character: "説",
    readings: { on: ["セツ"], kun: ["と(く)"] },
    meanings: ["explain", "theory"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "説明", hiragana: "せつめい", english: "explanation", jlpt: "N4" },
      { japanese: "小説", hiragana: "しょうせつ", english: "novel", jlpt: "N4" },
      { japanese: "伝説", hiragana: "でんせつ", english: "legend", jlpt: "N3" }
    ],
    sentence: {
      japanese: "使い方を説明してください。",
      hiragana: "つかいかたをせつめいしてください。",
      romaji: "Tsukaikata wo setsumei shite kudasai.",
      english: "Please explain how to use it."
    }
  },
  {
    character: "軽",
    readings: { on: ["ケイ"], kun: ["かる(い)", "かろ(やか)"] },
    meanings: ["light", "easy"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "軽い", hiragana: "かるい", english: "light (weight)", jlpt: "N4" },
      { japanese: "軽く", hiragana: "かるく", english: "lightly", jlpt: "N3" },
      { japanese: "手軽", hiragana: "てがる", english: "easy, simple", jlpt: "N3" }
    ],
    sentence: {
      japanese: "この箱は軽いので持ちやすいです。",
      hiragana: "このはこはかるいのでもちやすいです。",
      romaji: "Kono hako wa karui node mochiyasui desu.",
      english: "This box is light so it's easy to carry."
    }
  },
  {
    character: "適",
    readings: { on: ["テキ"], kun: [""] },
    meanings: ["suitable", "appropriate"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "適当", hiragana: "てきとう", english: "suitable, random", jlpt: "N3" },
      { japanese: "適切", hiragana: "てきせつ", english: "appropriate", jlpt: "N3" },
      { japanese: "適用", hiragana: "てきよう", english: "application", jlpt: "N2" }
    ],
    sentence: {
      japanese: "適当な温度で調理します。",
      hiragana: "てきとうなおんどでちょうりします。",
      romaji: "Tekitou na ondo de chouri shimasu.",
      english: "I cook at a suitable temperature."
    }
  },
  {
    character: "関",
    readings: { on: ["カン"], kun: ["せき"] },
    meanings: ["connection", "barrier", "gate"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "関係", hiragana: "かんけい", english: "relationship", jlpt: "N4" },
      { japanese: "関心", hiragana: "かんしん", english: "interest, concern", jlpt: "N3" },
      { japanese: "関する", hiragana: "かんする", english: "to concern", jlpt: "N4" }
    ],
    sentence: {
      japanese: "玄関の鍵を閉めてください。",
      hiragana: "げんかんのかぎをしめてください。",
      romaji: "Genkan no kagi wo shimete kudasai.",
      english: "Please lock the entrance."
    }
  },
  {
    character: "除",
    readings: { on: ["ジョ"], kun: ["のぞ(く)"] },
    meanings: ["exclude", "remove"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["掃除"],
    words: [
      { japanese: "除く", hiragana: "のぞく", english: "to exclude", jlpt: "N3" },
      { japanese: "掃除", hiragana: "そうじ", english: "cleaning", jlpt: "N5" },
      { japanese: "除去", hiragana: "じょきょ", english: "removal", jlpt: "N2" }
    ],
    sentence: {
      japanese: "毎日掃除機をかけます。",
      hiragana: "まいにちそうじきをかけます。",
      romaji: "Mainichi soujiki wo kakemasu.",
      english: "I vacuum every day."
    }
  },
  {
    character: "雑",
    readings: { on: ["ザツ"], kun: ["まじ(る)"] },
    meanings: ["miscellaneous", "mixed"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["庭と外"],
    words: [
      { japanese: "雑誌", hiragana: "ざっし", english: "magazine", jlpt: "N5" },
      { japanese: "雑音", hiragana: "ざつおん", english: "noise", jlpt: "N3" },
      { japanese: "複雑", hiragana: "ふくざつ", english: "complex", jlpt: "N3" }
    ],
    sentence: {
      japanese: "雑誌を読んでリラックスします。",
      hiragana: "ざっしをよんでりらっくすします。",
      romaji: "Zasshi wo yonde rirakkusu shimasu.",
      english: "I relax by reading magazines."
    }
  },
  {
    character: "静",
    readings: { on: ["セイ"], kun: ["しず(か)"] },
    meanings: ["quiet", "calm"],
    jlpt: "N3",
    topics: ["home-life"],
    categories: ["よく使う言葉"],
    words: [
      { japanese: "静か", hiragana: "しずか", english: "quiet", jlpt: "N5" },
      { japanese: "静まる", hiragana: "しずまる", english: "to become quiet", jlpt: "N3" },
      { japanese: "冷静", hiragana: "れいせい", english: "calm, composed", jlpt: "N3" }
    ],
    sentence: {
      japanese: "夜は静かに過ごします。",
      hiragana: "よるはしずかにすごします。",
      romaji: "Yoru wa shizuka ni sugoshimasu.",
      english: "I spend the evening quietly."
    }
  },

  // ===== N2 Kanji =====

  {
    character: "剥",
    readings: { on: ["ハク"], kun: ["む(く)"] },
    meanings: ["peel", "strip"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "剥がす", hiragana: "はがす", english: "to peel off", jlpt: "N3" },
      { japanese: "剥く", hiragana: "むく", english: "to peel", jlpt: "N3" },
      { japanese: "剥がれる", hiragana: "はがれる", english: "to come off", jlpt: "N3" }
    ],
    sentence: {
      japanese: "バナナの皮を剥いて食べました。",
      hiragana: "ばななのかわをむいてたべました。",
      romaji: "Banana no kawa wo muite tabemashita.",
      english: "I peeled the banana and ate it."
    }
  },
  {
    character: "包",
    readings: { on: ["ホウ"], kun: ["つつ(む)"] },
    meanings: ["wrap", "envelop", "包丁"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["よく使う言葉", "調理器具"],
    words: [
      { japanese: "包む", hiragana: "つつむ", english: "to wrap", jlpt: "N4" },
      { japanese: "包丁", hiragana: "ほうちょう", english: "kitchen knife", jlpt: "N3" },
      { japanese: "小包", hiragana: "こづつみ", english: "parcel", jlpt: "N3" }
    ],
    sentence: {
      japanese: "包丁を使って肉を切ります。",
      hiragana: "ほうちょうをつかってにくをきります。",
      romaji: "Houchou wo tsukatte niku wo kirimasu.",
      english: "I cut meat using a kitchen knife."
    }
  },
  {
    character: "卓",
    readings: { on: ["タク"], kun: [""] },
    meanings: ["table", "desk"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["食事", "調理器具"],
    words: [
      { japanese: "食卓", hiragana: "しょくたく", english: "dining table", jlpt: "N3" },
      { japanese: "卓上", hiragana: "たくじょう", english: "on the desk", jlpt: "N2" },
      { japanese: "円卓", hiragana: "えんたく", english: "round table", jlpt: "N2" }
    ],
    sentence: {
      japanese: "食卓の上を拭いてください。",
      hiragana: "しょくたくのうえをふいてください。",
      romaji: "Shokutaku no ue wo fuite kudasai.",
      english: "Please wipe the dining table."
    }
  },
  {
    character: "卵",
    readings: { on: ["ラン"], kun: ["たまご"] },
    meanings: ["egg"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["食事"],
    words: [
      { japanese: "卵", hiragana: "たまご", english: "egg", jlpt: "N5" },
      { japanese: "目玉焼き", hiragana: "めだまやき", english: "fried egg", jlpt: "N4" },
      { japanese: "卵焼き", hiragana: "たまごやき", english: "omelet", jlpt: "N4" }
    ],
    sentence: {
      japanese: "朝ごはんに卵を食べます。",
      hiragana: "あさごはんにたまごをたべます。",
      romaji: "Asa-gohan ni tamago wo tabemasu.",
      english: "I eat eggs for breakfast."
    }
  },
  {
    character: "呂",
    readings: { on: ["ロ"], kun: [""] },
    meanings: ["spine", "backbone", "bath"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "風呂", hiragana: "ふろ", english: "bath", jlpt: "N5" },
      { japanese: "お風呂", hiragana: "おふろ", english: "bath (polite)", jlpt: "N5" },
      { japanese: "風呂場", hiragana: "ふろば", english: "bathroom", jlpt: "N4" }
    ],
    sentence: {
      japanese: "毎日お風呂に入ります。",
      hiragana: "まいにちおふろにはいります。",
      romaji: "Mainichi ofuro ni hairimasu.",
      english: "I take a bath every day."
    }
  },
  {
    character: "噌",
    readings: { on: ["ソ"], kun: [""] },
    meanings: ["miso"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["調味料と食べ物"],
    words: [
      { japanese: "味噌", hiragana: "みそ", english: "miso", jlpt: "N4" },
      { japanese: "味噌汁", hiragana: "みそしる", english: "miso soup", jlpt: "N5" },
      { japanese: "味噌煮", hiragana: "みそに", english: "miso-simmered", jlpt: "N3" }
    ],
    sentence: {
      japanese: "味噌汁を作りましょう。",
      hiragana: "みそしるをつくりましょう。",
      romaji: "Misoshiru wo tsukurimashou.",
      english: "Let's make miso soup."
    }
  },
  {
    character: "壇",
    readings: { on: ["ダン"], kun: ["-"] },
    meanings: ["platform", "flower bed"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["庭と外"],
    words: [
      { japanese: "花壇", hiragana: "かだん", english: "flower bed", jlpt: "N2" },
      { japanese: "仏壇", hiragana: "ぶつだん", english: "Buddhist altar", jlpt: "N2" },
      { japanese: "壇上", hiragana: "だんじょう", english: "on the platform", jlpt: "N2" }
    ],
    sentence: {
      japanese: "庭に花壇を作りました。",
      hiragana: "にわにかだんをつくりました。",
      romaji: "Niwa ni kadan wo tsukurimashita.",
      english: "I made a flower bed in the garden."
    }
  },
  {
    character: "嬉",
    readings: { on: ["キ"], kun: ["うれ(しい)"] },
    meanings: ["happy", "glad"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["時間と描写"],
    words: [
      { japanese: "嬉しい", hiragana: "うれしい", english: "happy, glad", jlpt: "N5" },
      { japanese: "嬉々", hiragana: "きき", english: "gleefully", jlpt: "N1" },
      { japanese: "悲喜", hiragana: "ひき", english: "joy and sorrow", jlpt: "N2" }
    ],
    sentence: {
      japanese: "家族が集まって嬉しいです。",
      hiragana: "かぞくがあつまってうれしいです。",
      romaji: "Kazoku ga atsumatte ureshii desu.",
      english: "I'm happy that the family is gathering."
    }
  },
  {
    character: "履",
    readings: { on: ["リ"], kun: ["は(く)"] },
    meanings: ["wear (footwear)"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["朝の動作"],
    words: [
      { japanese: "履く", hiragana: "はく", english: "to wear (shoes)", jlpt: "N5" },
      { japanese: "履物", hiragana: "はきもの", english: "footwear", jlpt: "N3" },
      { japanese: "履歴", hiragana: "りれき", english: "personal history", jlpt: "N2" }
    ],
    sentence: {
      japanese: "靴を履いて出かけます。",
      hiragana: "くつをはいてでかけます。",
      romaji: "Kutsu wo haite dekakemasu.",
      english: "I put on shoes and go out."
    }
  },
  {
    character: "床",
    readings: { on: ["ショウ"], kun: ["ゆか", "とこ"] },
    meanings: ["floor", "bed"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "床", hiragana: "ゆか", english: "floor", jlpt: "N4" },
      { japanese: "床屋", hiragana: "とこや", english: "barber", jlpt: "N4" },
      { japanese: "起床", hiragana: "きしょう", english: "getting up", jlpt: "N3" }
    ],
    sentence: {
      japanese: "床を掃除機できれいにします。",
      hiragana: "ゆかをそうじきできれいにします。",
      romaji: "Yuka wo soujiki de kirei ni shimasu.",
      english: "I clean the floor with a vacuum cleaner."
    }
  },
  {
    character: "廊",
    readings: { on: ["ロウ"], kun: [""] },
    meanings: ["corridor", "hallway"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "廊下", hiragana: "ろうか", english: "corridor", jlpt: "N4" },
      { japanese: "回廊", hiragana: "かいろう", english: "corridor, cloister", jlpt: "N2" },
      { japanese: "渡り廊下", hiragana: "わたりろうか", english: "connecting corridor", jlpt: "N2" }
    ],
    sentence: {
      japanese: "廊下を静かに歩いてください。",
      hiragana: "ろうかをしずかにあるいてください。",
      romaji: "Rouka wo shizuka ni aruite kudasai.",
      english: "Please walk quietly in the corridor."
    }
  },
  {
    character: "慎",
    readings: { on: ["シン"], kun: ["つつし(む)"] },
    meanings: ["careful", "prudent"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "慎重", hiragana: "しんちょう", english: "careful, cautious", jlpt: "N3" },
      { japanese: "慎む", hiragana: "つつしむ", english: "to be careful", jlpt: "N2" },
      { japanese: "謹慎", hiragana: "きんしん", english: "self-restraint", jlpt: "N1" }
    ],
    sentence: {
      japanese: "慎重に料理を運びます。",
      hiragana: "しんちょうにりょうりをはこびます。",
      romaji: "Shinchou ni ryouri wo hakobimasu.",
      english: "I carefully carry the food."
    }
  },
  {
    character: "掃",
    readings: { on: ["ソウ"], kun: ["は(く)"] },
    meanings: ["sweep", "clean"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["掃除"],
    words: [
      { japanese: "掃除", hiragana: "そうじ", english: "cleaning", jlpt: "N5" },
      { japanese: "掃く", hiragana: "はく", english: "to sweep", jlpt: "N4" },
      { japanese: "掃除機", hiragana: "そうじき", english: "vacuum cleaner", jlpt: "N4" }
    ],
    sentence: {
      japanese: "毎週末部屋を掃除します。",
      hiragana: "まいしゅうまつへやをそうじします。",
      romaji: "Maishuumatsu heya wo souji shimasu.",
      english: "I clean my room every weekend."
    }
  },
  {
    character: "棚",
    readings: { on: ["-"], kun: ["たな"] },
    meanings: ["shelf", "rack"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["家庭用品"],
    words: [
      { japanese: "棚", hiragana: "たな", english: "shelf", jlpt: "N4" },
      { japanese: "本棚", hiragana: "ほんだな", english: "bookshelf", jlpt: "N4" },
      { japanese: "食器棚", hiragana: "しょっきだな", english: "cupboard", jlpt: "N3" }
    ],
    sentence: {
      japanese: "食器を棚に並べます。",
      hiragana: "しょっきをたなにならべます。",
      romaji: "Shokki wo tana ni narabemasu.",
      english: "I arrange the dishes on the shelf."
    }
  },
  {
    character: "清",
    readings: { on: ["セイ"], kun: ["きよ(い)"] },
    meanings: ["pure", "clean"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["時間と描写"],
    words: [
      { japanese: "清潔", hiragana: "せいけつ", english: "clean", jlpt: "N3" },
      { japanese: "清い", hiragana: "きよい", english: "pure, clean", jlpt: "N2" },
      { japanese: "清掃", hiragana: "せいそう", english: "cleaning", jlpt: "N2" }
    ],
    sentence: {
      japanese: "清潔なキッチンを保ちます。",
      hiragana: "せいけつなきっちんをたもちます。",
      romaji: "Seiketsu na kicchin wo tamochimasu.",
      english: "I keep a clean kitchen."
    }
  },
  {
    character: "潔",
    readings: { on: ["ケツ"], kun: ["いさぎよ(い)"] },
    meanings: ["pure", "clean"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["時間と描写"],
    words: [
      { japanese: "清潔", hiragana: "せいけつ", english: "clean", jlpt: "N3" },
      { japanese: "潔い", hiragana: "いさぎよい", english: "admirable, graceful", jlpt: "N2" },
      { japanese: "潔癖", hiragana: "けっぺき", english: "fastidiousness", jlpt: "N1" }
    ],
    sentence: {
      japanese: "部屋を清潔に保っています。",
      hiragana: "へやをせいけつにたもっています。",
      romaji: "Heya wo seiketsu ni tamotte imasu.",
      english: "I keep the room clean."
    }
  },
  {
    character: "炊",
    readings: { on: ["スイ"], kun: ["た(く)"] },
    meanings: ["cook rice", "boil"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["朝の動作"],
    words: [
      { japanese: "炊く", hiragana: "たく", english: "to cook rice", jlpt: "N4" },
      { japanese: "炊飯器", hiragana: "すいはんき", english: "rice cooker", jlpt: "N4" },
      { japanese: "炊事", hiragana: "すいじ", english: "cooking", jlpt: "N2" }
    ],
    sentence: {
      japanese: "炊飯器でご飯を炊きます。",
      hiragana: "すいはんきでごはんをたきます。",
      romaji: "Suihanki de gohan wo takimasu.",
      english: "I cook rice with a rice cooker."
    }
  },
  {
    character: "煮",
    readings: { on: ["シャ"], kun: ["に(る)"] },
    meanings: ["boil", "simmer"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "煮る", hiragana: "にる", english: "to boil, simmer", jlpt: "N4" },
      { japanese: "煮物", hiragana: "にもの", english: "cooked dish", jlpt: "N3" },
      { japanese: "煮える", hiragana: "にえる", english: "to be cooked", jlpt: "N3" }
    ],
    sentence: {
      japanese: "野菜を煮て柔らかくします。",
      hiragana: "やさいをにてやわらかくします。",
      romaji: "Yasai wo nite yawarakaku shimasu.",
      english: "I boil vegetables to make them soft."
    }
  },
  {
    character: "玄",
    readings: { on: ["ゲン"], kun: [""] },
    meanings: ["mysterious", "entrance"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "玄関", hiragana: "げんかん", english: "entrance", jlpt: "N5" },
      { japanese: "玄米", hiragana: "げんまい", english: "brown rice", jlpt: "N3" },
      { japanese: "玄人", hiragana: "くろうと", english: "expert", jlpt: "N2" }
    ],
    sentence: {
      japanese: "玄関で靴を脱いでください。",
      hiragana: "げんかんでくつをぬいでください。",
      romaji: "Genkan de kutsu wo nuide kudasai.",
      english: "Please take off your shoes at the entrance."
    }
  },
  {
    character: "玉",
    readings: { on: ["ギョク"], kun: ["たま"] },
    meanings: ["ball", "jewel", "onion"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["材料"],
    words: [
      { japanese: "玉", hiragana: "たま", english: "ball, sphere", jlpt: "N4" },
      { japanese: "玉ねぎ", hiragana: "たまねぎ", english: "onion", jlpt: "N4" },
      { japanese: "目玉", hiragana: "めだま", english: "eyeball", jlpt: "N3" }
    ],
    sentence: {
      japanese: "玉ねぎを切ると涙が出ます。",
      hiragana: "たまねぎをきるとなみだがでます。",
      romaji: "Tamanegi wo kiru to namida ga demasu.",
      english: "Tears come out when I cut onions."
    }
  },
  {
    character: "疲",
    readings: { on: ["ヒ"], kun: ["つか(れる)"] },
    meanings: ["tired", "fatigued"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["時間と描写"],
    words: [
      { japanese: "疲れる", hiragana: "つかれる", english: "to get tired", jlpt: "N5" },
      { japanese: "疲労", hiragana: "ひろう", english: "fatigue", jlpt: "N2" },
      { japanese: "お疲れ様", hiragana: "おつかれさま", english: "good job (polite)", jlpt: "N4" }
    ],
    sentence: {
      japanese: "家事をして疲れました。",
      hiragana: "かじをしてつかれました。",
      romaji: "Kaji wo shite tsukaremashita.",
      english: "I got tired from doing housework."
    }
  },
  {
    character: "砂",
    readings: { on: ["サ"], kun: ["すな"] },
    meanings: ["sand", "sugar"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["調味料と食べ物"],
    words: [
      { japanese: "砂", hiragana: "すな", english: "sand", jlpt: "N4" },
      { japanese: "砂糖", hiragana: "さとう", english: "sugar", jlpt: "N5" },
      { japanese: "砂漠", hiragana: "さばく", english: "desert", jlpt: "N3" }
    ],
    sentence: {
      japanese: "コーヒーに砂糖を入れますか。",
      hiragana: "こーひーにさとうをいれますか。",
      romaji: "Koohii ni satou wo iremasu ka.",
      english: "Do you put sugar in your coffee?"
    }
  },
  {
    character: "窓",
    readings: { on: ["ソウ"], kun: ["まど"] },
    meanings: ["window"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "窓", hiragana: "まど", english: "window", jlpt: "N5" },
      { japanese: "窓口", hiragana: "まどぐち", english: "counter window", jlpt: "N4" },
      { japanese: "窓ガラス", hiragana: "まどがらす", english: "window glass", jlpt: "N3" }
    ],
    sentence: {
      japanese: "窓を開けて部屋を換気します。",
      hiragana: "まどをあけてへやをかんきします。",
      romaji: "Mado wo akete heya wo kanki shimasu.",
      english: "I open the window to ventilate the room."
    }
  },
  {
    character: "糖",
    readings: { on: ["トウ"], kun: [""] },
    meanings: ["sugar"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["調味料と食べ物"],
    words: [
      { japanese: "砂糖", hiragana: "さとう", english: "sugar", jlpt: "N5" },
      { japanese: "糖分", hiragana: "とうぶん", english: "sugar content", jlpt: "N2" },
      { japanese: "血糖", hiragana: "けっとう", english: "blood sugar", jlpt: "N2" }
    ],
    sentence: {
      japanese: "砂糖を少し加えてください。",
      hiragana: "さとうをすこしくわえてください。",
      romaji: "Satou wo sukoshi kuwaete kudasai.",
      english: "Please add a little sugar."
    }
  },
  {
    character: "蓋",
    readings: { on: ["ガイ"], kun: ["ふた"] },
    meanings: ["lid", "cover"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["調理器具"],
    words: [
      { japanese: "蓋", hiragana: "ふた", english: "lid, cover", jlpt: "N3" },
      { japanese: "蓋を開ける", hiragana: "ふたをあける", english: "to open the lid", jlpt: "N3" },
      { japanese: "蓋を閉める", hiragana: "ふたをしめる", english: "to close the lid", jlpt: "N3" }
    ],
    sentence: {
      japanese: "鍋の蓋を開けて確認します。",
      hiragana: "なべのふたをあけてかくにんします。",
      romaji: "Nabe no futa wo akete kakunin shimasu.",
      english: "I open the pot lid to check."
    }
  },
  {
    character: "蔵",
    readings: { on: ["ゾウ"], kun: ["くら"] },
    meanings: ["storehouse", "refrigerator"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["家庭用品"],
    words: [
      { japanese: "冷蔵庫", hiragana: "れいぞうこ", english: "refrigerator", jlpt: "N5" },
      { japanese: "蔵", hiragana: "くら", english: "warehouse", jlpt: "N2" },
      { japanese: "貯蔵", hiragana: "ちょぞう", english: "storage", jlpt: "N2" }
    ],
    sentence: {
      japanese: "食材を冷蔵庫に入れました。",
      hiragana: "しょくざいをれいぞうこにいれました。",
      romaji: "Shokuzai wo reizouko ni iremashita.",
      english: "I put the ingredients in the refrigerator."
    }
  },
  {
    character: "褒",
    readings: { on: ["ホウ"], kun: ["ほ(める)"] },
    meanings: ["praise", "admire"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["描写と動作"],
    words: [
      { japanese: "褒める", hiragana: "ほめる", english: "to praise", jlpt: "N4" },
      { japanese: "褒美", hiragana: "ほうび", english: "reward", jlpt: "N2" },
      { japanese: "お褒めの言葉", hiragana: "おほめのことば", english: "words of praise", jlpt: "N2" }
    ],
    sentence: {
      japanese: "母の料理をいつも褒めます。",
      hiragana: "ははのりょうりをいつもほめます。",
      romaji: "Haha no ryouri wo itsumo homemasu.",
      english: "I always praise my mother's cooking."
    }
  },
  {
    character: "込",
    readings: { on: ["-"], kun: ["こ(む)"] },
    meanings: ["crowded", "include"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["料理の動作"],
    words: [
      { japanese: "込む", hiragana: "こむ", english: "to be crowded", jlpt: "N4" },
      { japanese: "申し込む", hiragana: "もうしこむ", english: "to apply", jlpt: "N4" },
      { japanese: "飛び込む", hiragana: "とびこむ", english: "to jump in", jlpt: "N3" }
    ],
    sentence: {
      japanese: "部屋に荷物を運び込みました。",
      hiragana: "へやににもつをはこびこみました。",
      romaji: "Heya ni nimotsu wo hakobi-komimashita.",
      english: "I carried the luggage into the room."
    }
  },
  {
    character: "迎",
    readings: { on: ["ゲイ"], kun: ["むか(える)"] },
    meanings: ["welcome", "greet"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["夜の活動"],
    words: [
      { japanese: "迎える", hiragana: "むかえる", english: "to welcome", jlpt: "N4" },
      { japanese: "出迎え", hiragana: "でむかえ", english: "meeting, reception", jlpt: "N3" },
      { japanese: "お迎え", hiragana: "おむかえ", english: "pick up (polite)", jlpt: "N4" }
    ],
    sentence: {
      japanese: "玄関で家族を迎えます。",
      hiragana: "げんかんでかぞくをむかえます。",
      romaji: "Genkan de kazoku wo mukaemasu.",
      english: "I welcome my family at the entrance."
    }
  },
  {
    character: "醤",
    readings: { on: ["ショウ"], kun: [""] },
    meanings: ["soy sauce"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["調味料と食べ物"],
    words: [
      { japanese: "醤油", hiragana: "しょうゆ", english: "soy sauce", jlpt: "N5" },
      { japanese: "醤油差し", hiragana: "しょうゆさし", english: "soy sauce dispenser", jlpt: "N3" },
      { japanese: "醤油味", hiragana: "しょうゆあじ", english: "soy sauce flavor", jlpt: "N3" }
    ],
    sentence: {
      japanese: "料理に醤油をかけます。",
      hiragana: "りょうりにしょうゆをかけます。",
      romaji: "Ryouri ni shouyu wo kakemasu.",
      english: "I pour soy sauce on the food."
    }
  },
  {
    character: "鍋",
    readings: { on: ["-"], kun: ["なべ"] },
    meanings: ["pot", "pan"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["調理器具"],
    words: [
      { japanese: "鍋", hiragana: "なべ", english: "pot, pan", jlpt: "N4" },
      { japanese: "鍋料理", hiragana: "なべりょうり", english: "hot pot dish", jlpt: "N3" },
      { japanese: "フライパン", hiragana: "ふらいぱん", english: "frying pan", jlpt: "N4" }
    ],
    sentence: {
      japanese: "鍋で野菜を煮ています。",
      hiragana: "なべでやさいをにています。",
      romaji: "Nabe de yasai wo nite imasu.",
      english: "I'm boiling vegetables in a pot."
    }
  },
  {
    character: "階",
    readings: { on: ["カイ"], kun: [""] },
    meanings: ["floor", "story", "stairs"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["家と部屋"],
    words: [
      { japanese: "階段", hiragana: "かいだん", english: "stairs", jlpt: "N5" },
      { japanese: "一階", hiragana: "いっかい", english: "first floor", jlpt: "N5" },
      { japanese: "二階", hiragana: "にかい", english: "second floor", jlpt: "N5" }
    ],
    sentence: {
      japanese: "二階の部屋で寝ます。",
      hiragana: "にかいのへやでねます。",
      romaji: "Nikai no heya de nemasu.",
      english: "I sleep in the room on the second floor."
    }
  },
  {
    character: "頓",
    readings: { on: ["トン"], kun: [""] },
    meanings: ["arrange", "suddenly"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["掃除"],
    words: [
      { japanese: "整頓", hiragana: "せいとん", english: "tidying up", jlpt: "N3" },
      { japanese: "急に", hiragana: "きゅうに", english: "suddenly", jlpt: "N4" },
      { japanese: "困頓", hiragana: "こんとん", english: "poverty", jlpt: "N1" }
    ],
    sentence: {
      japanese: "部屋を整理整頓しました。",
      hiragana: "へやをせいりせいとんしました。",
      romaji: "Heya wo seiri seiton shimashita.",
      english: "I organized and tidied up the room."
    }
  },
  {
    character: "飯",
    readings: { on: ["ハン"], kun: ["めし"] },
    meanings: ["meal", "cooked rice"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["食事", "調味料と食べ物"],
    words: [
      { japanese: "ご飯", hiragana: "ごはん", english: "rice, meal", jlpt: "N5" },
      { japanese: "朝ご飯", hiragana: "あさごはん", english: "breakfast", jlpt: "N5" },
      { japanese: "炊飯", hiragana: "すいはん", english: "rice cooking", jlpt: "N3" }
    ],
    sentence: {
      japanese: "ご飯が炊けました。",
      hiragana: "ごはんがたけました。",
      romaji: "Gohan ga takemashita.",
      english: "The rice is cooked."
    }
  },
  {
    character: "魚",
    readings: { on: ["ギョ"], kun: ["さかな"] },
    meanings: ["fish"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["食事"],
    words: [
      { japanese: "魚", hiragana: "さかな", english: "fish", jlpt: "N5" },
      { japanese: "金魚", hiragana: "きんぎょ", english: "goldfish", jlpt: "N4" },
      { japanese: "魚屋", hiragana: "さかなや", english: "fish shop", jlpt: "N4" }
    ],
    sentence: {
      japanese: "今日は魚を焼いて食べます。",
      hiragana: "きょうはさかなをやいてたべます。",
      romaji: "Kyou wa sakana wo yaite tabemasu.",
      english: "I'm grilling fish and eating it today."
    }
  },
  {
    character: "鳴",
    readings: { on: ["メイ"], kun: ["な(る)", "な(く)"] },
    meanings: ["ring", "sound", "cry"],
    jlpt: "N2",
    topics: ["home-life"],
    categories: ["時間と朝"],
    words: [
      { japanese: "鳴く", hiragana: "なく", english: "to cry (animal)", jlpt: "N4" },
      { japanese: "鳴る", hiragana: "なる", english: "to sound, ring", jlpt: "N5" },
      { japanese: "鳴らす", hiragana: "ならす", english: "to ring", jlpt: "N3" }
    ],
    sentence: {
      japanese: "タイマーが鳴ったので料理ができました。",
      hiragana: "たいまーがなったのでりょうりができました。",
      romaji: "Taimaa ga natta node ryouri ga dekimashita.",
      english: "The timer rang so the food is done."
    }
  }
];

// Export for browser use (global variable)
// Use with: initializeSchemaWithKanji(window.homeLifeKanji) from storage.js
if (typeof window !== 'undefined') {
  window.homeLifeKanji = homeLifeKanji;
}

// Export for Node.js / CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = homeLifeKanji;
}