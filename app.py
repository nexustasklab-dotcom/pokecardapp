import re
import streamlit as st
import database as db
import scraper
from master_data import PACKS

st.set_page_config(page_title="PokeCard Asset", layout="centered", initial_sidebar_state="collapsed")

# iPhone 15 Plus 幅(430px)準拠CSS - 複数セレクタで強制
st.markdown("""
<style>
/* 新しいStreamlit対応 */
[data-testid="stMainBlockContainer"],
section.main > div.block-container,
.main .block-container,
.block-container {
    max-width: 430px !important;
    padding-top: 0.5rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
[data-testid="stAppViewContainer"] {
    background: #fafafa;
}
[data-testid="stAppViewContainer"] > .main,
section.main {
    max-width: 430px !important;
    margin: 0 auto !important;
}
#MainMenu { visibility: hidden; }
header { visibility: hidden; height: 0 !important; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stHeader"] { display: none; }

/* ボタンの余白を詰める */
.stButton > button {
    padding: 0.25rem 0.5rem;
}

/* 数量±ボタン */
div[data-testid="column"] .stButton > button {
    min-height: 32px;
}
</style>
""", unsafe_allow_html=True)

# 初期化
db.init_db()
if "updating" not in st.session_state:
    st.session_state.updating = False
if "adding" not in st.session_state:
    st.session_state.adding = False
if "fixing_images" not in st.session_state:
    st.session_state.fixing_images = False

# ヘッダー
st.markdown("<div style='background:#E63946;color:white;padding:8px;text-align:center;font-weight:600;border-radius:8px;margin-bottom:8px;'>PokeCard Asset</div>", unsafe_allow_html=True)


def is_broken_img(url: str | None) -> bool:
    if not url or not isinstance(url, str):
        return True
    url = url.strip()
    if url == "" or url.lower() in ("none", "null"):
        return True
    if not (url.startswith("http://") or url.startswith("https://")):
        return True
    return False


def proxied_img(url: str) -> str:
    """
    画像URLを weserv.nl 経由にしてホットリンク防止(Referer)を回避する。
    URLからスキーマを取り除いて渡す必要がある。
    """
    if is_broken_img(url):
        return ""
    # https:// or http:// を取り除く
    stripped = re.sub(r"^https?://", "", url)
    return f"https://images.weserv.nl/?url={stripped}&w=112&h=112&fit=cover"


# 最終更新日時取得
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
    update_btn_label = f"最新相場に更新（最終: {last_updated_disp}）"
else:
    update_btn_label = "最新相場に更新（未更新）"

def estimate_mori(h):
    snkr = h.get("snkrdunk_price") or 0
    mori = h.get("morimori_price") or 0
    if h.get("shrink"):
        return mori
    else:
        return mori if mori else max(snkr - 3000, 0)

# ボタン
col1, col2 = st.columns([4, 1])
with col1:
    if st.button(update_btn_label, type="primary", use_container_width=True, key="update_btn"):
        st.session_state.updating = True
with col2:
    if st.button("保存", use_container_width=True, key="save_btn"):
        holdings = db.get_all_holdings()
        t_s = sum((h.get("snkrdunk_price", 0) or 0) * h["qty"] for h in holdings)
        t_m = sum(estimate_mori(h) * h["qty"] for h in holdings)
        db.save_snapshot(t_s, t_m)
        st.success("💾")

# 画像再取得ボタン
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

# 価格更新処理
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

# サマリー表示
st.markdown(f"""
<div style="background:linear-gradient(135deg,#dc2626,#b91c1c);color:white;padding:16px;border-radius:16px;margin:10px 0;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
    <div>
      <div style="font-size:12px;opacity:0.8;">総資産</div>
      <div style="font-size:24px;font-weight:700;">{fmt(total_snkr)}</div>
    </div>
    <div>
      <div style="font-size:12px;opacity:0.8;">買取金額</div>
      <div style="font-size:24px;font-weight:700;">{fmt(total_mori)}</div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px;">
    <div style="background:rgba(255,255,255,0.15);padding:8px;border-radius:8px;">
      <div style="font-size:10px;">前回比</div>
      <div style="font-size:14px;font-weight:700;">{diff_str(prev_diff_snkr)}</div>
    </div>
    <div style="background:rgba(255,255,255,0.15);padding:8px;border-radius:8px;">
      <div style="font-size:10px;">累計増減</div>
      <div style="font-size:14px;font-weight:700;">{diff_str(first_diff_snkr)}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# BOX一覧
st.markdown("<div style='margin:0 4px;font-size:11px;color:#666;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'>保有BOX一覧</div>", unsafe_allow_html=True)

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

        pack_name = h["pack_name"]
        if "「" in pack_name and "」" in pack_name:
            prefix = pack_name.split("「")[0].strip()
            main_name = pack_name.split("「")[1].split("」")[0]
            display_name = f"{prefix} {main_name}"
        else:
            display_name = pack_name

        mori_display = fmt(mori_price) if mori_price else "ー"
        if mori_is_estimated and mori_price:
            mori_display = f"{mori_display}<span style='font-size:9px;color:#9ca3af;'>(仮)</span>"

        mori_subtotal_display = fmt(mori_price * qty) if mori_price else "ー"
        if mori_is_estimated and mori_price:
            mori_subtotal_display = f"{mori_subtotal_display}<span style='font-size:9px;color:#9ca3af;'>(仮)</span>"

        # 画像URL: 壊れていればプレースホルダー、それ以外はプロキシ経由
        raw_img = h.get("img_url") or ""
        if is_broken_img(raw_img):
            img_src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='56' height='56'><rect width='56' height='56' fill='%23f3f4f6'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-size='9' fill='%239ca3af'>no img</text></svg>"
        else:
            img_src = proxied_img(raw_img)

        # BOXカード本体
        st.markdown(f"""
        <div style="background:white;border:0.5px solid #e5e7eb;border-radius:12px;padding:12px;margin:4px 0;">
          <div style="display:flex;gap:10px;align-items:center;">
            <img src="{img_src}" style="width:56px;height:56px;border-radius:8px;object-fit:cover;background:#f3f4f6;flex-shrink:0;">
            <div style="flex:1;min-width:0;">
              <div style="font-size:11.5px;font-weight:600;margin-bottom:4px;line-height:1.3;">{display_name}</div>
              <span style="font-size:10px;background:{'#dcfce7;color:#166534' if shrink else '#fff7ed;color:#c2410c'};padding:2px 6px;border-radius:12px;">シュリンク{'有' if shrink else '無'}</span>
            </div>
            <div style="text-align:right;flex-shrink:0;">
              <div style="font-size:12px;font-weight:700;">{fmt(snkr_price)}</div>
              <div style="font-size:12px;font-weight:700;">{mori_display}</div>
            </div>
          </div>
          <div style="border-top:1px solid #f3f4f6;margin-top:8px;padding-top:6px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:10px;color:#6b7280;">小計（× {qty}）</span>
            <div style="text-align:right;">
              <div style="font-size:12px;font-weight:600;">{fmt(snkr_price * qty)}</div>
              <div style="font-size:12px;font-weight:600;">{mori_subtotal_display}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # 数量調整 ± ボタン + 削除
        c_minus, c_qty, c_plus, c_spacer, c_del = st.columns([1, 1, 1, 3, 1])
        with c_minus:
            if st.button("－", key=f"minus_{h['id']}", use_container_width=True):
                db.update_qty_delta(h["id"], -1)
                st.rerun()
        with c_qty:
            st.markdown(
                f"<div style='text-align:center;font-weight:700;font-size:16px;line-height:32px;'>{qty}</div>",
                unsafe_allow_html=True
            )
        with c_plus:
            if st.button("＋", key=f"plus_{h['id']}", use_container_width=True):
                db.update_qty_delta(h["id"], 1)
                st.rerun()
        with c_del:
            if st.button("🗑", key=f"del_{h['id']}", use_container_width=True, help="削除"):
                db.delete_holding(h["id"])
                st.rerun()

# BOX追加ボタン
if st.button("＋ BOXを追加する", use_container_width=True, key="add_btn"):
    st.session_state.adding = True

# BOX追加フロー
if st.session_state.adding:
    if "selected_pack" not in st.session_state:
        st.session_state.selected_pack = None

    if st.session_state.selected_pack is None:
        st.markdown("**パックを選択**")
        search = st.text_input("検索", placeholder="パック名で検索")

        filtered = [p for p in PACKS if not search or search.lower() in p["name"].lower()][:20]

        for pack in filtered:
            col_img, col_info, col_btn = st.columns([1, 4, 1])
            with col_img:
                st.image(pack["img"], width=52)
            with col_info:
                st.markdown(f"**{pack['name']}**  \n{pack['released_at']}")
            with col_btn:
                if st.button("選択", key=f"select_{pack['id']}"):
                    st.session_state.selected_pack = pack
                    st.rerun()

        if st.button("キャンセル"):
            st.session_state.adding = False
            st.rerun()

    else:
        pack = st.session_state.selected_pack
        col_img, col_info = st.columns([1, 4])
        with col_img:
            st.image(pack["img"], width=52)
        with col_info:
            st.markdown(f"**{pack['name']}**  \n{pack['released_at']}")

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
