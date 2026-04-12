import re
import streamlit as st
import database as db
import scraper
from master_data import PACKS

st.set_page_config(page_title="PokeCard Asset", layout="centered", initial_sidebar_state="collapsed")

# 最小限のCSS：幅制御とUI要素の非表示のみ。columns には触らない
st.markdown("""
<style>
html, body {
    overflow-x: hidden !important;
    max-width: 100vw !important;
}
* { box-sizing: border-box !important; }

[data-testid="stAppViewContainer"] {
    background: #fafafa;
    overflow-x: hidden !important;
    max-width: 100vw !important;
}
[data-testid="stMainBlockContainer"],
.main .block-container,
.block-container {
    max-width: 430px !important;
    width: 100% !important;
    padding-top: 0.5rem !important;
    padding-bottom: 1rem !important;
    padding-left: 8px !important;
    padding-right: 8px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    overflow-x: hidden !important;
}
#MainMenu { visibility: hidden; }
header { visibility: hidden; height: 0 !important; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stHeader"] { display: none; }

/* 画像はみ出し防止 */
img { max-width: 100% !important; height: auto; }

/* ボタンのフォントサイズだけ調整 */
.stButton > button {
    font-size: 13px !important;
    padding: 0.3rem 0.5rem !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* モバイルでも columns を縦積みにせず横並び維持 */
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    min-width: 0 !important;
    overflow: hidden !important;
}

/* expander のスタイル調整 */
div[data-testid="stExpander"] {
    border: none !important;
    margin-top: -4px !important;
    margin-bottom: 8px !important;
}
div[data-testid="stExpander"] summary {
    font-size: 12px !important;
    padding: 4px 8px !important;
}
</style>
""", unsafe_allow_html=True)

db.init_db()
if "updating" not in st.session_state:
    st.session_state.updating = False
if "adding" not in st.session_state:
    st.session_state.adding = False
if "fixing_images" not in st.session_state:
    st.session_state.fixing_images = False

st.markdown("<div style='background:#E63946;color:white;padding:8px;text-align:center;font-weight:600;border-radius:8px;margin-bottom:8px;'>PokeCard Asset</div>", unsafe_allow_html=True)


def is_broken_img(url):
    if not url or not isinstance(url, str):
        return True
    url = url.strip()
    if url == "" or url.lower() in ("none", "null"):
        return True
    if not (url.startswith("http://") or url.startswith("https://")):
        return True
    return False


def proxied_img(url):
    if is_broken_img(url):
        return ""
    stripped = re.sub(r"^https?://", "", url)
    return f"https://images.weserv.nl/?url={stripped}&w=140&h=140&fit=cover"


def split_pack_name(pack_name):
    if "「" in pack_name and "」" in pack_name:
        prefix = pack_name.split("「")[0].strip()
        main_name = pack_name.split("「")[1].split("」")[0]
        return prefix, main_name
    parts = pack_name.split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", pack_name


# 最終更新日時
holdings_for_meta = db.get_all_holdings()
last_updated = None
for h in holdings_for_meta:
    u = h.get("updated_at")
    if u and (last_updated is None or u > last_updated):
        last_updated = u

if last_updated:
    try:
        last_updated_disp = last_updated[5:16].replace("-", "/")
    except Exception:
        last_updated_disp = last_updated
    update_btn_label = f"更新（{last_updated_disp}）"
else:
    update_btn_label = "最新相場に更新"


def estimate_mori(h):
    snkr = h.get("snkrdunk_price") or 0
    mori = h.get("morimori_price") or 0
    if h.get("shrink"):
        return mori
    else:
        return mori if mori else max(snkr - 3000, 0)


# ヘッダーボタン: 2:1 比率で保存も見える幅に
col1, col2 = st.columns([2, 1])
with col1:
    if st.button(update_btn_label, type="primary", use_container_width=True, key="update_btn"):
        st.session_state.updating = True
with col2:
    if st.button("💾 保存", use_container_width=True, key="save_btn"):
        holdings = db.get_all_holdings()
        t_s = sum((h.get("snkrdunk_price", 0) or 0) * h["qty"] for h in holdings)
        t_m = sum(estimate_mori(h) * h["qty"] for h in holdings)
        db.save_snapshot(t_s, t_m)
        st.success("保存しました")

# 画像再取得
holdings_check = db.get_all_holdings()
broken_count = sum(1 for h in holdings_check if is_broken_img(h.get("img_url")) and h.get("snkrdunk_id"))
if broken_count > 0:
    if st.button("🖼 画像を再取得", use_container_width=True, key="fix_img_btn"):
        st.session_state.fixing_images = True

if st.session_state.fixing_images:
    holdings = db.get_all_holdings()
    targets = [h for h in holdings if is_broken_img(h.get("img_url")) and h.get("snkrdunk_id")]
    progress = st.progress(0, text=f"画像取得中... 0/{len(targets)}")
    success = 0
    for i, h in enumerate(targets):
        try:
            img_url = scraper.get_snkrdunk_image(h["snkrdunk_id"])
            if img_url:
                db.update_img_url(h["id"], img_url)
                success += 1
        except Exception:
            pass
        progress.progress((i + 1) / max(len(targets), 1), text=f"画像取得中... {i+1}/{len(targets)}")
    st.session_state.fixing_images = False
    st.success(f"✅ {success}/{len(targets)}件取得")
    st.rerun()

# 価格更新
if st.session_state.updating:
    holdings = db.get_all_holdings()
    progress = st.progress(0, text="更新中...")
    for i, h in enumerate(holdings):
        if h.get("snkrdunk_id"):
            prices = scraper.fetch_prices(h["snkrdunk_id"], h.get("morimori_url"), h.get("mobile_ichiban_url"))
            db.update_prices(h["id"], prices.get("snkrdunk"), prices.get("morimori"))
            if is_broken_img(h.get("img_url")):
                try:
                    img_url = scraper.get_snkrdunk_image(h["snkrdunk_id"])
                    if img_url:
                        db.update_img_url(h["id"], img_url)
                except Exception:
                    pass
        progress.progress((i + 1) / max(len(holdings), 1))

    updated = db.get_all_holdings()
    t_s = sum((h.get("snkrdunk_price", 0) or 0) * h["qty"] for h in updated)
    t_m = sum(estimate_mori(h) * h["qty"] for h in updated)
    db.save_snapshot(t_s, t_m)

    st.session_state.updating = False
    st.rerun()

# サマリー計算
holdings = db.get_all_holdings()
total_snkr = sum((h.get("snkrdunk_price", 0) or 0) * h["qty"] for h in holdings)
total_mori = sum(estimate_mori(h) * h["qty"] for h in holdings)

snapshots = db.get_snapshots(limit=2)
first_snap = db.get_first_snapshot()

prev_diff_snkr = 0
first_diff_snkr = 0
if len(snapshots) >= 2:
    prev_snkr = snapshots[1].get("snkrdunk_total", 0) or 0
    prev_diff_snkr = total_snkr - prev_snkr
if first_snap:
    first_snkr = first_snap.get("snkrdunk_total", 0) or 0
    first_diff_snkr = total_snkr - first_snkr


def fmt(amount):
    return f"¥{amount:,}" if amount else "¥0"


def diff_str(amount):
    if amount > 0:
        return f"+{fmt(amount)}"
    elif amount < 0:
        return fmt(amount)
    return "¥0"


def diff_color(amount):
    if amount > 0:
        return "#16a34a"
    elif amount < 0:
        return "#dc2626"
    return "#6b7280"


summary_html = (
    '<div style="background:linear-gradient(135deg,#dc2626,#b91c1c);color:white;padding:12px 14px;border-radius:14px;margin:8px 0;">'
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">'
    f'<div><div style="font-size:11px;opacity:0.85;">総資産</div><div style="font-size:22px;font-weight:700;line-height:1.2;">{fmt(total_snkr)}</div></div>'
    f'<div><div style="font-size:11px;opacity:0.85;">買取金額</div><div style="font-size:22px;font-weight:700;line-height:1.2;">{fmt(total_mori)}</div></div>'
    '</div>'
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px;">'
    f'<div style="background:white;padding:6px 8px;border-radius:6px;"><div style="font-size:9px;color:#6b7280;">前回比</div><div style="font-size:13px;font-weight:700;color:{diff_color(prev_diff_snkr)};">{diff_str(prev_diff_snkr)}</div></div>'
    f'<div style="background:white;padding:6px 8px;border-radius:6px;"><div style="font-size:9px;color:#6b7280;">累計増減</div><div style="font-size:13px;font-weight:700;color:{diff_color(first_diff_snkr)};">{diff_str(first_diff_snkr)}</div></div>'
    '</div>'
    '</div>'
)
st.markdown(summary_html, unsafe_allow_html=True)

st.markdown("<div style='margin:6px 4px 4px;font-size:11px;color:#666;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'>保有BOX一覧</div>", unsafe_allow_html=True)

if holdings:
    for h in holdings:
        snkr_price = h.get("snkrdunk_price") or 0
        mori_raw = h.get("morimori_price") or 0
        qty = h["qty"]
        shrink = h.get("shrink", False)

        if shrink:
            mori_price = mori_raw
            mori_is_estimated = False
        else:
            if mori_raw:
                mori_price = mori_raw
                mori_is_estimated = False
            else:
                mori_price = max(snkr_price - 3000, 0)
                mori_is_estimated = True

        prefix, main_name = split_pack_name(h["pack_name"])

        mori_unit = fmt(mori_price) if mori_price else "ー"
        mori_sub = fmt(mori_price * qty) if mori_price else "ー"
        mark = '<span style="font-size:9px;color:#9ca3af;">(仮)</span>' if (mori_is_estimated and mori_price) else ""

        raw_img = h.get("img_url") or ""
        if is_broken_img(raw_img):
            img_src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64'><rect width='64' height='64' fill='%23f3f4f6'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-size='9' fill='%239ca3af'>no img</text></svg>"
        else:
            img_src = proxied_img(raw_img)

        if prefix:
            name_html = f'<div style="font-size:10px;color:#6b7280;line-height:1.2;">{prefix}</div><div style="font-size:13px;font-weight:700;line-height:1.25;color:#111827;">{main_name}</div>'
        else:
            name_html = f'<div style="font-size:13px;font-weight:700;line-height:1.25;color:#111827;">{main_name}</div>'

        shrink_badge = f'<span style="display:inline-block;margin-top:4px;font-size:10px;background:{"#dcfce7;color:#166534" if shrink else "#fff7ed;color:#c2410c"};padding:2px 8px;border-radius:12px;">シュリンク{"有" if shrink else "無"}</span>'

        price_table = (
            '<div style="margin-top:10px;padding-top:8px;border-top:1px solid #f3f4f6;">'
            '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;align-items:baseline;">'
            '<div></div>'
            '<div style="font-size:9px;color:#9ca3af;text-align:right;">市場価格</div>'
            '<div style="font-size:9px;color:#9ca3af;text-align:right;">買取金額</div>'
            '<div style="font-size:10px;color:#6b7280;">単価</div>'
            f'<div style="font-size:14px;font-weight:700;color:#111827;text-align:right;">{fmt(snkr_price)}</div>'
            f'<div style="font-size:14px;font-weight:700;color:#111827;text-align:right;">{mori_unit}{mark}</div>'
            f'<div style="font-size:10px;color:#6b7280;">小計（×{qty}）</div>'
            f'<div style="font-size:17px;font-weight:800;color:#dc2626;text-align:right;">{fmt(snkr_price * qty)}</div>'
            f'<div style="font-size:15px;font-weight:700;color:#dc2626;text-align:right;">{mori_sub}{mark}</div>'
            '</div>'
            '</div>'
        )

        # 数量バッジ（カード右上）
        qty_badge = f'<div style="position:absolute;top:10px;right:12px;background:#dc2626;color:white;font-size:13px;font-weight:700;padding:3px 10px;border-radius:12px;min-width:32px;text-align:center;">×{qty}</div>'

        card_html = (
            '<div style="position:relative;background:white;border:1px solid #e5e7eb;border-radius:14px;padding:12px;margin:6px 0;box-shadow:0 1px 2px rgba(0,0,0,0.03);">'
            f'{qty_badge}'
            '<div style="display:flex;gap:12px;align-items:center;padding-right:48px;">'
            f'<img src="{img_src}" style="width:64px;height:64px;border-radius:10px;object-fit:cover;background:#f3f4f6;flex-shrink:0;">'
            f'<div style="flex:1;min-width:0;">{name_html}{shrink_badge}</div>'
            '</div>'
            f'{price_table}'
            '</div>'
        )

        st.markdown(card_html, unsafe_allow_html=True)

        # 編集はアコーディオン展開（モバイルでも横幅問題が起きない）
        with st.expander("⚙ 編集", expanded=False):
            new_qty = st.number_input(
                "数量",
                min_value=1,
                max_value=99,
                value=qty,
                step=1,
                key=f"qty_input_{h['id']}"
            )
            if new_qty != qty:
                db.update_qty(h["id"], new_qty)
                st.rerun()

            if st.button("🗑 このBOXを削除", key=f"del_{h['id']}", use_container_width=True):
                db.delete_holding(h["id"])
                st.rerun()

if st.button("＋ BOXを追加する", use_container_width=True, key="add_btn"):
    st.session_state.adding = True

if st.session_state.adding:
    if "selected_pack" not in st.session_state:
        st.session_state.selected_pack = None

    if st.session_state.selected_pack is None:
        st.markdown("**パックを選択**")
        search = st.text_input("検索", placeholder="パック名で検索", label_visibility="collapsed")

        filtered = [p for p in PACKS if not search or search.lower() in p["name"].lower()][:20]

        for pack in filtered:
            # 画像 + 名前 + ボタンを1つのHTMLカードに
            pack_img = proxied_img(pack["img"]) if not is_broken_img(pack["img"]) else pack["img"]
            pack_card = (
                '<div style="display:flex;gap:10px;align-items:center;background:white;border:1px solid #e5e7eb;border-radius:10px;padding:8px;margin:4px 0;">'
                f'<img src="{pack_img}" style="width:48px;height:48px;border-radius:6px;object-fit:cover;flex-shrink:0;">'
                f'<div style="flex:1;min-width:0;"><div style="font-size:12px;font-weight:600;line-height:1.3;color:#111827;">{pack["name"]}</div><div style="font-size:10px;color:#6b7280;margin-top:2px;">{pack["released_at"]}</div></div>'
                '</div>'
            )
            st.markdown(pack_card, unsafe_allow_html=True)
            if st.button(f"このパックを選択", key=f"select_{pack['id']}", use_container_width=True):
                st.session_state.selected_pack = pack
                st.rerun()

        if st.button("キャンセル", use_container_width=True):
            st.session_state.adding = False
            st.rerun()

    else:
        pack = st.session_state.selected_pack
        pack_img = proxied_img(pack["img"]) if not is_broken_img(pack["img"]) else pack["img"]
        pack_html = (
            '<div style="display:flex;gap:12px;align-items:center;background:white;border:1px solid #e5e7eb;border-radius:10px;padding:10px;margin:8px 0;">'
            f'<img src="{pack_img}" style="width:56px;height:56px;border-radius:8px;object-fit:cover;flex-shrink:0;">'
            f'<div style="flex:1;min-width:0;"><div style="font-size:13px;font-weight:700;line-height:1.3;">{pack["name"]}</div><div style="font-size:10px;color:#6b7280;margin-top:2px;">{pack["released_at"]}</div></div>'
            '</div>'
        )
        st.markdown(pack_html, unsafe_allow_html=True)

        shrink_fixed = pack.get("shrink_fixed")

        if shrink_fixed is True:
            st.success("📦 シュリンク有で登録")
            has_shrink = True
        elif shrink_fixed is False:
            st.warning("🗂 シュリンク無で登録")
            has_shrink = False
        else:
            shrink_choice = st.radio("シュリンク", ["📦 シュリンク有", "🗂 シュリンク無"], label_visibility="collapsed")
            has_shrink = shrink_choice.startswith("📦")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 戻る", use_container_width=True):
                st.session_state.selected_pack = None
                st.rerun()
        with col2:
            if st.button("✅ 追加", type="primary", use_container_width=True):
                img_url = pack["img"]
                if is_broken_img(img_url) and pack.get("snkrdunk_id"):
                    try:
                        fetched = scraper.get_snkrdunk_image(pack["snkrdunk_id"])
                        if fetched:
                            img_url = fetched
                    except Exception:
                        pass

                db.add_holding(
                    pack_id=pack["id"],
                    pack_name=pack["name"],
                    img_url=img_url or "",
                    shrink=has_shrink,
                    snkrdunk_id=pack.get("snkrdunk_id"),
                    morimori_url=pack.get("morimori_url") if has_shrink else None,
                    mobile_ichiban_url=pack.get("mobile_ichiban_url"),
                )
                st.session_state.adding = False
                st.session_state.selected_pack = None
                st.rerun()
