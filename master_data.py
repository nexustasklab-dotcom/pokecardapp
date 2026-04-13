# master_data.py
# 全パック一覧（発売日新しい順）

PACKS = [
    # ── 2026 ──────────────────────────────────────────────────────
    {
        "id": "762693", "name": "拡張パック「ニンジャスピナー」", "released_at": "2026-03-13",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/244b2a87-ebe1-41bb-a812-6daa8aaddc80.webp",
        "snkrdunk_id": "762693", 
        "morimori_url": "https://www.morimori-kaitori.jp/category/2401/product/318774",
        "mobile_ichiban_url": "https://www.mobile-ichiban.com/Prod/3/04#id=3",
        "shrink_fixed": True,
    },
    {
        "id": "762695", "name": "拡張パック「ニンジャスピナー」（シュリンクなし）", "released_at": "2026-03-13",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/5955b7f5-5b90-43e6-a4fb-6a33e2cdc27f.webp",
        "snkrdunk_id": "762695", 
        "morimori_url": None, 
        "mobile_ichiban_url": "https://www.mobile-ichiban.com/Prod/3/04#id=3",
        "shrink_fixed": False,
    },
    {
        "id": "743533", "name": "拡張パック「ムニキスゼロ」", "released_at": "2026-01-23",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20260126035830-0.webp",
        "snkrdunk_id": "743533", 
        "morimori_url": "https://www.morimori-kaitori.jp/category/24/product/318658",
        "mobile_ichiban_url": "https://www.mobile-ichiban.com/Prod/3/04#id=2",
        "shrink_fixed": True,
    },
    {
        "id": "743535", "name": "拡張パック「ムニキスゼロ」（シュリンクなし）", "released_at": "2026-01-23",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20260126035830-0.webp",
        "snkrdunk_id": "743535", 
        "morimori_url": None, 
        "mobile_ichiban_url": "https://www.mobile-ichiban.com/Prod/3/04#id=2",
        "shrink_fixed": False,
    },
    # ── 2025 ──────────────────────────────────────────────────────
    {
        "id": "721913", "name": "ハイクラスパック「MEGAドリームex」", "released_at": "2025-11-28",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20251128091038-0.webp",
        "snkrdunk_id": "721913", 
        "morimori_url": "https://www.morimori-kaitori.jp/category/2401/product/307325",
        "mobile_ichiban_url": None,
        "shrink_fixed": True,
    },
    {
        "id": "721915", "name": "ハイクラスパック「MEGAドリームex」（シュリンクなし）", "released_at": "2025-11-28",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20251202022316-0.webp",
        "snkrdunk_id": "721915", 
        "morimori_url": None, 
        "mobile_ichiban_url": None,
        "shrink_fixed": False,
    },
    {
        "id": "687430", "name": "拡張パック「インフェルノX」", "released_at": "2025-09-26",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20250926055512-0.webp",
        "snkrdunk_id": "687430", 
        "morimori_url": "https://www.morimori-kaitori.jp/category/2401001/product/291313", 
        "mobile_ichiban_url": None,
        "shrink_fixed": None,
    },
    {
        "id": "628146", "name": "拡張パック「メガブレイブ」", "released_at": "2025-08-01",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20250805020822-2.webp",
        "snkrdunk_id": "628146", 
        "morimori_url": "https://www.morimori-kaitori.jp/category/2401001/product/281624", 
        "mobile_ichiban_url": None,
        "shrink_fixed": None,
    },
    {
        "id": "628148", "name": "拡張パック「メガシンフォニア」", "released_at": "2025-08-01",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20250805020822-5.webp",
        "snkrdunk_id": "628148", 
        "morimori_url": "https://www.morimori-kaitori.jp/category/2401/product/299488", 
        "mobile_ichiban_url": None,
        "shrink_fixed": None,
    },
    # ── 2024 ──────────────────────────────────────────────────────
    {
        "id": "424297", "name": "ハイクラスパック「テラスタルフェスex」", "released_at": "2024-12-06",
        "img": "https://via.placeholder.com/300x300?text=テラスタルフェスex",
        "snkrdunk_id": "424297", 
        "morimori_url": None, 
        "mobile_ichiban_url": None,
        "shrink_fixed": None,
    },
    {
        "id": "618443", "name": "スペシャルBOX「ポケモンセンターヒロシマ」", "released_at": "2024-12-06",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20251016093844-0.webp",
        "snkrdunk_id": "618443", 
        "morimori_url": "https://www.morimori-kaitori.jp/category/2401/product/299678", 
        "mobile_ichiban_url": None,
        "shrink_fixed": None,
    },
    # ── 2022 ──────────────────────────────────────────────────────
    {
        "id": "509419", "name": "ハイクラスパック「VSTARユニバース」", "released_at": "2022-12-02",
        "img": "https://cdn.snkrdunk.com/upload_bg_removed/20221205073249-0.webp",
        "snkrdunk_id": "509419", 
        "morimori_url": None, 
        "mobile_ichiban_url": "https://www.mobile-ichiban.com/Prod/3/04",
        "shrink_fixed": None,
    },
    # ── その他パック ─────────────────────────────────────────────
    {"id": "cr_493", "name": "スペシャルカードセット メガエルレイドex", "released_at": "2026-01-23",
     "img": "https://files.cardrush.media/pokemon/packs/493.webp", 
     "snkrdunk_id": None, "morimori_url": None, "mobile_ichiban_url": None, "shrink_fixed": None},
]

PACK_BY_ID = {str(p["id"]): p for p in PACKS}
