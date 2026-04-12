# master_data.py
# 全パック一覧（発売日新しい順）
#
# img:          スニダンの背景除去済み商品画像
# snkrdunk_id:  スニダンの apparel ID（設定済みのみ自動取得）
# morimori_url: 森森買取の商品URL（シュリンクなし・対象外は None）
# shrink_fixed: True=シュリンク有固定, False=シュリンク無固定, None=追加時に選択

PACKS = [
    # ── 2026 ──────────────────────────────────────────────────────
    {
        "id": "762693", "name": "拡張パック「ニンジャスピナー」", "released_at": "2026-03-13",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/244b2a87-ebe1-41bb-a812-6daa8aaddc80.webp",
        "snkrdunk_id": "762693", "morimori_url": None, "shrink_fixed": True,
    },
    {
        "id": "762695", "name": "拡張パック「ニンジャスピナー」（シュリンクなし）", "released_at": "2026-03-13",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/5955b7f5-5b90-43e6-a4fb-6a33e2cdc27f.webp",
        "snkrdunk_id": "762695", "morimori_url": None, "shrink_fixed": False,
    },
    {
        "id": "743533", "name": "拡張パック「ムニキスゼロ」", "released_at": "2026-01-23",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20260126035830-0.webp",
        "snkrdunk_id": "743533", "morimori_url": None, "shrink_fixed": True,
    },
    {
        "id": "743535", "name": "拡張パック「ムニキスゼロ」（シュリンクなし）", "released_at": "2026-01-23",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20260126035830-0.webp",
        "snkrdunk_id": "743535", "morimori_url": None, "shrink_fixed": False,
    },
    # ── 2025 ──────────────────────────────────────────────────────
    {
        "id": "724998", "name": "スタートデッキ100「バトルコレクション」", "released_at": "2025-12-19",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20251223071721-0.webp",
        "snkrdunk_id": "724998", "morimori_url": None, "shrink_fixed": None,
    },
    {
        "id": "735757", "name": "スタートデッキ100「バトルコレクション コロちゃおver」", "released_at": "2025-12-19",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20251223072117-0.webp",
        "snkrdunk_id": "735757", "morimori_url": None, "shrink_fixed": None,
    },
    {
        "id": "721913", "name": "ハイクラスパック「MEGAドリームex」", "released_at": "2025-11-28",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20251128091038-0.webp",
        "snkrdunk_id": "721913", "morimori_url": "https://www.morimori-kaitori.jp/category/2401/product/307325",
        "shrink_fixed": True,
    },
    {
        "id": "721915", "name": "ハイクラスパック「MEGAドリームex」（シュリンクなし）", "released_at": "2025-11-28",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20251202022316-0.webp",
        "snkrdunk_id": "721915", "morimori_url": None, "shrink_fixed": False,
    },
    {
        "id": "687430", "name": "拡張パック「インフェルノX」", "released_at": "2025-09-26",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20250926055512-0.webp",
        "snkrdunk_id": "687430", "morimori_url": None, "shrink_fixed": None,
    },
    {
        "id": "674432", "name": "スターターセットMEGA「メガゲンガーex」", "released_at": "2025-09-05",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20251022075124-0.webp",
        "snkrdunk_id": "674432", "morimori_url": None, "shrink_fixed": None,
    },
    {
        "id": "628146", "name": "拡張パック「メガブレイブ」", "released_at": "2025-08-01",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20250805020822-2.webp",
        "snkrdunk_id": "628146", "morimori_url": None, "shrink_fixed": None,
    },
    {
        "id": "628148", "name": "拡張パック「メガシンフォニア」", "released_at": "2025-08-01",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20250805020822-5.webp",
        "snkrdunk_id": "628148", "morimori_url": None, "shrink_fixed": None,
    },
    {
        "id": "424297", "name": "プレミアムトレーナーボックスMEGA", "released_at": "2025-08-01",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20250813062440-0.webp",
        "snkrdunk_id": "424297", "morimori_url": None, "shrink_fixed": None,
    },
    # ── 2024 ──────────────────────────────────────────────────────
    {
        "id": "628148tf", "name": "ハイクラスパック「テラスタルフェスex」", "released_at": "2024-12-06",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20241209033558-0.webp",
        "snkrdunk_id": "628148", "morimori_url": None, "shrink_fixed": None,
    },
    {
        "id": "674432eb", "name": "拡張パック「超電ブレイカー」", "released_at": "2024-10-18",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20241018091824-0.webp",
        "snkrdunk_id": "674432", "morimori_url": None, "shrink_fixed": None,
    },
    # ── 2023 ──────────────────────────────────────────────────────
    {
        "id": "703025", "name": "強化拡張パック「ポケモンカード151」", "released_at": "2023-06-16",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20230620070952-0.webp",
        "snkrdunk_id": "703025", "morimori_url": None, "shrink_fixed": None,
    },
    # ── 2022 ──────────────────────────────────────────────────────
    {
        "id": "509419", "name": "ハイクラスパック「VSTARユニバース」", "released_at": "2022-12-02",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20221205073249-0.webp",
        "snkrdunk_id": "509419", "morimori_url": None, "shrink_fixed": None,
    },
    # ── cardrushのみ（スニダンURL未設定）─────────────────────────
    {"id": "cr_493", "name": "スペシャルカードセット メガエルレイドex", "released_at": "2026-01-23",
     "img": "https://files.cardrush.media/pokemon/packs/493.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_491", "name": "スタートデッキ100 バトルコレクション コロちゃおVer.", "released_at": "2025-12-19",
     "img": "https://files.cardrush.media/pokemon/packs/491.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_488", "name": "拡張パック「インフェルノX」", "released_at": "2025-09-26",
     "img": "https://files.cardrush.media/pokemon/packs/488.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_486", "name": "スターターセットMEGA メガディアンシーex", "released_at": "2025-09-05",
     "img": "https://files.cardrush.media/pokemon/packs/486.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_487", "name": "スターターセットMEGA メガゲンガーex", "released_at": "2025-09-05",
     "img": "https://files.cardrush.media/pokemon/packs/487.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_483", "name": "拡張パック「メガブレイブ」", "released_at": "2025-08-01",
     "img": "https://files.cardrush.media/pokemon/packs/483.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_482", "name": "拡張パック「メガシンフォニア」", "released_at": "2025-08-01",
     "img": "https://files.cardrush.media/pokemon/packs/482.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_475", "name": "デッキビルドBOX バトルパートナーズ", "released_at": "2025-01-24",
     "img": "https://files.cardrush.media/pokemon/packs/475.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_467", "name": "拡張パック「バトルパートナーズ」", "released_at": "2025-01-24",
     "img": "https://files.cardrush.media/pokemon/packs/467.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_474", "name": "拡張パック「ホワイトフレア」", "released_at": "2025-06-06",
     "img": "https://files.cardrush.media/pokemon/packs/474.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_473", "name": "拡張パック「ブラックボルト」", "released_at": "2025-06-06",
     "img": "https://files.cardrush.media/pokemon/packs/473.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_471", "name": "拡張パック「ロケット団の栄光」", "released_at": "2025-04-18",
     "img": "https://files.cardrush.media/pokemon/packs/471.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_470", "name": "強化拡張パック「熱風のアリーナ」", "released_at": "2025-03-14",
     "img": "https://files.cardrush.media/pokemon/packs/470.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_465", "name": "ハイクラスパック「テラスタルフェスex」", "released_at": "2024-12-06",
     "img": "https://files.cardrush.media/pokemon/packs/465.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_464", "name": "拡張パック「超電ブレイカー」", "released_at": "2024-10-18",
     "img": "https://files.cardrush.media/pokemon/packs/464.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_461", "name": "強化拡張パック「楽園ドラゴーナ」", "released_at": "2024-09-13",
     "img": "https://files.cardrush.media/pokemon/packs/461.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_459", "name": "拡張パック「ステラミラクル」", "released_at": "2024-07-19",
     "img": "https://files.cardrush.media/pokemon/packs/459.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_476", "name": "デッキビルドBOX ステラミラクル", "released_at": "2024-07-19",
     "img": "https://files.cardrush.media/pokemon/packs/476.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_458", "name": "強化拡張パック「ナイトワンダラー」", "released_at": "2024-06-07",
     "img": "https://files.cardrush.media/pokemon/packs/458.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_478", "name": "バトルマスターデッキ パオジアンex", "released_at": "2024-05-17",
     "img": "https://files.cardrush.media/pokemon/packs/478.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_477", "name": "バトルマスターデッキ テラスタル リザードンex", "released_at": "2024-05-17",
     "img": "https://files.cardrush.media/pokemon/packs/477.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_457", "name": "拡張パック「変幻の仮面」", "released_at": "2024-04-26",
     "img": "https://files.cardrush.media/pokemon/packs/457.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_456", "name": "強化拡張パック「クリムゾンヘイズ」", "released_at": "2024-03-22",
     "img": "https://files.cardrush.media/pokemon/packs/456.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_451", "name": "拡張パック「サイバージャッジ」", "released_at": "2024-01-26",
     "img": "https://files.cardrush.media/pokemon/packs/451.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_452", "name": "拡張パック「ワイルドフォース」", "released_at": "2024-01-26",
     "img": "https://files.cardrush.media/pokemon/packs/452.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_450", "name": "ハイクラスパック「シャイニートレジャーex」", "released_at": "2023-12-01",
     "img": "https://files.cardrush.media/pokemon/packs/450.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_479", "name": "ポケモンカードゲームClassic フシギバナ&ルギアexデッキ", "released_at": "2023-10-27",
     "img": "https://files.cardrush.media/pokemon/packs/479.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_480", "name": "ポケモンカードゲームClassic リザードン&ホウオウexデッキ", "released_at": "2023-10-27",
     "img": "https://files.cardrush.media/pokemon/packs/480.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_481", "name": "ポケモンカードゲームClassic カメックス&スイクンexデッキ", "released_at": "2023-10-27",
     "img": "https://files.cardrush.media/pokemon/packs/481.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_447", "name": "拡張パック「古代の咆哮」", "released_at": "2023-10-27",
     "img": "https://files.cardrush.media/pokemon/packs/447.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_446", "name": "拡張パック「未来の一閃」", "released_at": "2023-10-27",
     "img": "https://files.cardrush.media/pokemon/packs/446.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_443", "name": "強化拡張パック「レイジングサーフ」", "released_at": "2023-09-22",
     "img": "https://files.cardrush.media/pokemon/packs/443.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_440", "name": "拡張パック「黒炎の支配者」", "released_at": "2023-07-28",
     "img": "https://files.cardrush.media/pokemon/packs/440.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_438", "name": "強化拡張パック「ポケモンカード151」", "released_at": "2023-06-16",
     "img": "https://files.cardrush.media/pokemon/packs/438.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_433", "name": "拡張パック「クレイバースト」", "released_at": "2023-04-14",
     "img": "https://files.cardrush.media/pokemon/packs/433.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_420", "name": "ハイクラスパック「VSTARユニバース」", "released_at": "2022-12-02",
     "img": "https://files.cardrush.media/pokemon/packs/420.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
    {"id": "cr_419", "name": "スペシャルデッキセット リザードンVSTAR vs レックウザVMAX", "released_at": "2022-11-04",
     "img": "https://files.cardrush.media/pokemon/packs/419.webp", "snkrdunk_id": None, "morimori_url": None, "shrink_fixed": None},
]

PACK_BY_ID = {str(p["id"]): p for p in PACKS}
