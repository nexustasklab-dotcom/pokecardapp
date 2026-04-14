import streamlit as st
import database as db
import scraper
from master_data import PACKS

st.set_page_config(page_title="PokeCard Asset", layout="wide", initial_sidebar_state="collapsed")

# ライトモード固定 + モバイル最適化
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
    background-color: #ffffff !important;
    color: #111111 !important;
    color-scheme: light !important;
}
.main .block-container { padding: 0.5rem; max-width: 460px; margin: 0 auto; }
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

/* デフォルトの文字色を黒に（サマリーカード内は個別に白指定するので影響なし） */
.stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    color: #111111 !important;
}

/* number_input をコンパクトに */
[data-testid="stNumberInput"] {
    margin-bottom: 2px !important;
}
[data-testid="stNumberInput"] input {
    padding: 2px 2px !important;
    font-size: 13px !important;
    text-align: center !important;
    color: #111 !important;
    background: #fff !important;
    height: 30px !important;
}
[data-testid="stNumberInput"] button {
    padding: 0 !important;
    min-width: 22px !important;
    width: 22px !important;
    height: 30px !important;
}

/* ボタン全般 */
.stButton > button {
    padding: 4px 8px !important;
    min-height: 32px !important;
    font-size: 13px !important;
    background: #ffffff !important;
    color: #111 !important;
    border: 1px solid #d1d5db !important;
}
.stButton > button:hover {
    background: #f9fafb !important;
    color: #111 !important;
}

/* プライマリボタン（更新/追加） */
.stButton > button[kind="primary"] {
    min-height: 42px !important;
    font-size: 15px !important;
    background: #dc2626 !important;
    color: #ffffff !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: #b91c1c !important;
    color: #ffffff !important;
}

/* テキスト入力 */
[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #111 !important;
    border: 1px solid #d1d5db !important;
}

/* radio */
[data-testid="stRadio"] label {
    color: #111 !important;
}
</style>
""", unsafe_allow_html=True)

db.init_db()

# 起動時に一度だけ、master_data.pyの日本語名で既存holdingsを同期する
if "name_synced" not in st.session_state:
    PACK_BY_SNKR = {str(p.get("snkrdunk_id")): p for p in PACKS if p.get("snkrdunk_id")}
    for h in db.get_all_holdings():
        sid = str(h.get("snkrdunk_id") or "")
        if sid in PACK_BY_SNKR:
            jp_name = PACK_BY_SNKR[sid]["name"]
            if h.get("pack_name") != jp_name:
                db.rename_holding(h["id"], jp_name)
    st.session_state.name_synced = True

if "updating" not in st.session_state:
    st.session_state.updating = False
if "adding" not in st.session_state:
    st.session_state.adding = False

st.markdown("<div style='background:#E63946;color:#ffffff;padding:10px;text-align:center;font-weight:700;font-size:15px;border-radius:10px;margin-bottom:10px;'>PokeCard Asset</div>", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    if st.button("最新相場に更新", type="primary", use_container_width=True, key="update_btn"):
        st.session_state.updating = True
with col2:
    if st.button("保存", use_container_width=True, key="save_btn"):
        holdings = db.get_all_holdings()
        t_s = sum((h.get("snkrdunk_price", 0) or 0) * h["qty"] for h in holdings)
        t_m = sum((h.get("morimori_price", 0) or 0) * h["qty"] for h in holdings if h.get("shrink"))
        db.save_snapshot(t_s, t_m)
        st.success("💾")

# 更新処理 — 画像だけ上書き、パック名は日本語維持
if st.session_state.updating:
    holdings = db.get_all_holdings()
    progress = st.progress(0, text="更新中...")
    for i, h in enumerate(holdings):
        if h.get("snkrdunk_id"):
            prices = scraper.fetch_prices(
                h["snkrdunk_id"],
                h.get("morimori_url"),
                h.get("mobile_ichiban_url"),
            )
            db.update_prices(
                h["id"],
                prices.get("snkrdunk"),
                prices.get("morimori"),
                img_url=prices.get("snkrdunk_image"),
                pack_name=None,  # 日本語名を維持
            )
        progress.progress((i + 1) / max(len(holdings), 1))

    updated = db.get_all_holdings()
    t_s = sum((h.get("snkrdunk_price", 0) or 0) * h["qty"] for h in updated)
    t_m = sum((h.get("morimori_price", 0) or 0) * h["qty"] for h in updated if h.get("shrink"))
    db.save_snapshot(t_s, t_m)

    st.session_state.updating = False
    st.rerun()

holdings = db.get_all_holdings()
total_snkr = sum((h.get("snkrdunk_price", 0) or 0) * h["qty"] for h in holdings)
total_mori = sum((h.get("morimori_price", 0) or 0) * h["qty"] for h in holdings if h.get("shrink"))

snapshots = db.get_snapshots(limit=2)
prev_diff_snkr = 0
first_diff_snkr = 0

if len(snapshots) >= 2:
    prev_snkr = snapshots[1].get("total_snkrdunk", 0)
    prev_diff_snkr = total_snkr - prev_snkr

first = db.get_first_snapshot()
if first:
    first_diff_snkr = total_snkr - first.get("total_snkrdunk", 0)

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
        return "#16a34a"  # green
    elif amount < 0:
        return "#dc2626"  # red
    return "#6b7280"

# サマリーカード（上段：白背景赤字の赤カード／下段：白背景の前回比・累計）
st.markdown(f"""
<div style="background:linear-gradient(135deg,#dc2626,#b91c1c);padding:16px;border-radius:16px;margin:10px 0 8px 0;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
    <div>
      <div style="font-size:11px;color:#ffffff;opacity:0.85;">総資産</div>
      <div style="font-size:22px;font-weight:800;color:#ffffff;">{fmt(total_snkr)}</div>
    </div>
    <div>
      <div style="font-size:11px;color:#ffffff;opacity:0.85;">買取金額</div>
      <div style="font-size:22px;font-weight:800;color:#ffffff;">{fmt(total_mori)}</div>
    </div>
  </div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 10px 0;">
  <div style="background:#ffffff;border:1px solid #e5e7eb;padding:10px;border-radius:10px;">
    <div style="font-size:10px;color:#6b7280;">前回比</div>
    <div style="font-size:15px;font-weight:800;color:{diff_color(prev_diff_snkr)};">{diff_str(prev_diff_snkr)}</div>
  </div>
  <div style="background:#ffffff;border:1px solid #e5e7eb;padding:10px;border-radius:10px;">
    <div style="font-size:10px;color:#6b7280;">累計増減</div>
    <div style="font-size:15px;font-weight:800;color:{diff_color(first_diff_snkr)};">{diff_str(first_diff_snkr)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin:4px 0;font-size:11px;color:#6b7280;font-weight:600;'>保有BOX一覧</div>", unsafe_allow_html=True)

PLACEHOLDER_IMG = "https://cdn.snkrdunk.com/upload_bg_removed/20250813062440-0.webp"

def split_pack_name(pack_name: str) -> tuple[str, str]:
    """「拡張パック「ニンジャスピナー」」→ ("拡張パック", "ニンジャスピナー")"""
    if not pack_name:
        return ("", "")
    if "「" in pack_name and "」" in pack_name:
        prefix = pack_name.split("「")[0].strip()
        main = pack_name.split("「")[1].split("」")[0]
        # 「（シュリンクなし）」などの接尾辞
        suffix = pack_name.split("」", 1)[1].strip()
        if suffix:
            main = f"{main} {suffix}"
        return (prefix, main)
    return ("", pack_name)

if holdings:
    for h in holdings:
        snkr_price = h.get("snkrdunk_price") or 0
        mori_price = h.get("morimori_price") or 0
        qty = h["qty"]
        shrink = h.get("shrink", False)

        prefix, main_name = split_pack_name(h["pack_name"] or "")
        img_src = h.get("img_url") or PLACEHOLDER_IMG

        col_main, col_ops = st.columns([4, 1])

        with col_main:
            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:10px;margin:4px 0;">
              <div style="display:flex;gap:10px;align-items:center;">
                <img src="{img_src}" style="width:72px;height:72px;border-radius:8px;object-fit:cover;background:#f3f4f6;flex-shrink:0;">
                <div style="flex:1;min-width:0;">
                  <div style="font-size:10px;color:#6b7280;line-height:1.2;">{prefix}</div>
                  <div style="font-size:14px;font-weight:700;color:#111;line-height:1.25;margin:2px 0 4px 0;word-break:break-word;">{main_name}</div>
                  <span style="font-size:9px;background:{'#dcfce7' if shrink else '#fff7ed'};color:{'#166534' if shrink else '#c2410c'};padding:2px 6px;border-radius:10px;">シュリンク{'有' if shrink else '無'}</span>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                  <div style="font-size:13px;font-weight:800;color:#111;">{fmt(snkr_price)}</div>
                  <div style="font-size:11px;font-weight:600;color:#6b7280;">{fmt(mori_price) if shrink and mori_price else "ー"}</div>
                </div>
              </div>
              <div style="border-top:1px solid #f3f4f6;margin-top:8px;padding-top:6px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:10px;color:#6b7280;">小計（× {qty}）</span>
                <div style="display:flex;gap:10px;">
                  <div style="font-size:13px;font-weight:700;color:#111;">{fmt(snkr_price * qty)}</div>
                  <div style="font-size:11px;font-weight:600;color:#6b7280;">{fmt(mori_price * qty) if shrink and mori_price else "ー"}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with col_ops:
            new_qty = st.number_input("数量", min_value=1, max_value=99, value=qty, key=f"qty_{h['id']}", label_visibility="collapsed")
            if new_qty != qty:
                db.update_qty(h["id"], new_qty)
                st.rerun()

            if st.button("🗑", key=f"del_{h['id']}", help="削除", use_container_width=True):
                db.delete_holding(h["id"])
                st.rerun()

st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
if st.button("＋ BOXを追加する", use_container_width=True, key="add_btn"):
    st.session_state.adding = True
    st.rerun()

# BOX追加フロー
if st.session_state.adding:
    if "selected_pack" not in st.session_state:
        st.session_state.selected_pack = None

    if st.session_state.selected_pack is None:
        st.markdown("<div style='font-size:14px;font-weight:700;color:#111;margin:10px 0 4px 0;'>パックを選択</div>", unsafe_allow_html=True)
        search = st.text_input("検索", placeholder="パック名で検索", label_visibility="collapsed")

        filtered = [p for p in PACKS if not search or search.lower() in p["name"].lower()][:30]

        for pack in filtered:
            prefix, main_name = split_pack_name(pack["name"])
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(
                    f"<div style='padding:8px 0;border-bottom:1px solid #f3f4f6;'>"
                    f"<div style='font-size:10px;color:#6b7280;'>{prefix}</div>"
                    f"<div style='font-size:14px;font-weight:700;color:#111;line-height:1.2;'>{main_name}</div>"
                    f"<div style='font-size:10px;color:#9ca3af;margin-top:2px;'>{pack['released_at']}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with col_btn:
                if st.button("選択", key=f"select_{pack['id']}", use_container_width=True):
                    st.session_state.selected_pack = pack
                    st.rerun()

        if st.button("キャンセル", key="cancel_add", use_container_width=True):
            st.session_state.adding = False
            st.rerun()

    else:
        pack = st.session_state.selected_pack
        prefix, main_name = split_pack_name(pack["name"])
        st.markdown(
            f"<div style='padding:12px;background:#f9fafb;border-radius:10px;margin:8px 0;'>"
            f"<div style='font-size:11px;color:#6b7280;'>{prefix}</div>"
            f"<div style='font-size:16px;font-weight:800;color:#111;'>{main_name}</div>"
            f"<div style='font-size:11px;color:#9ca3af;margin-top:2px;'>{pack['released_at']}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

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
            if st.button("← 戻る", use_container_width=True, key="back_add"):
                st.session_state.selected_pack = None
                st.rerun()
        with col2:
            if st.button("✅ 追加", type="primary", use_container_width=True, key="confirm_add"):
                db.add_holding(
                    pack_id=str(pack["id"]),
                    pack_name=pack["name"],
                    img_url=PLACEHOLDER_IMG,
                    shrink=has_shrink,
                    snkrdunk_id=pack.get("snkrdunk_id"),
                    morimori_url=pack.get("morimori_url") if has_shrink else None,
                    mobile_ichiban_url=pack.get("mobile_ichiban_url"),
                )
                st.session_state.adding = False
                st.session_state.selected_pack = None
                st.rerun()
