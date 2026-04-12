# app.py
import streamlit as st
from datetime import datetime

import database as db
import scraper
from master_data import PACKS

# ─── 初期設定 ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="PokeCard Asset",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="collapsed",
)

db.init_db()

# ─── カスタムCSS（iPhone最適化）─────────────────────────────────
st.markdown("""
<style>
/* 全体フォント・余白 */
html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif; }
.block-container { padding: 0.5rem 0.8rem 2rem; max-width: 430px; margin: 0 auto; }
/* ヘッダー非表示 */
header[data-testid="stHeader"] { display: none; }
/* ボタン */
div.stButton > button {
    width: 100%; border-radius: 10px; font-weight: 600;
    padding: 0.55rem 0; font-size: 0.9rem;
}
/* カード */
.box-card {
    background: white; border-radius: 14px;
    border: 1px solid #e5e7eb; margin-bottom: 10px;
    overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.box-card-inner { display: grid; grid-template-columns: 56px 1fr 1fr 52px; gap: 8px; padding: 10px 10px 8px; align-items: center; }
.box-img { width: 56px; height: 56px; border-radius: 8px; object-fit: cover; }
.box-name { font-size: 11.5px; font-weight: 600; color: #111; line-height: 1.3; margin-bottom: 4px; }
.badge { display:inline-block; font-size:10px; padding:2px 7px; border-radius:20px; font-weight:600; }
.badge-shrink { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
.badge-noshrink { background:#fff7ed; color:#c2410c; border:1px solid #fed7aa; }
.price-block { font-size: 11px; }
.price-val { font-size:12.5px; font-weight:700; color:#111; text-align:center; }
.price-label { font-size:10px; color:#6b7280; }
.price-na { font-size:12.5px; color:#9ca3af; text-align:center; }
.box-footer { background:#f9fafb; border-top:1px solid #e5e7eb; padding:5px 12px; display:flex; justify-content:space-between; align-items:center; }
.footer-label { font-size:10.5px; color:#6b7280; }
.footer-val { font-size:12px; font-weight:600; color:#111; }
/* サマリー */
.summary-wrap { background: linear-gradient(135deg, #dc2626, #b91c1c); border-radius: 16px; padding: 14px 14px 12px; margin-bottom: 12px; color:white; }
.summary-title { font-size:12px; opacity:0.8; margin-bottom:2px; }
.summary-val { font-size:22px; font-weight:700; }
.diff-row { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:10px; }
.diff-card { background:rgba(255,255,255,0.15); border-radius:10px; padding:7px 10px; }
.diff-label { font-size:10px; opacity:0.75; }
.diff-val { font-size:14px; font-weight:700; }
.plus { color: #bbf7d0; }
.minus { color: #fca5a5; }
.zero { color: white; }
/* セクションラベル */
.section-label { font-size:11px; color:#6b7280; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin: 4px 2px 6px; }
/* モーダル風セレクター */
.pack-item { display:flex; align-items:center; gap:10px; padding:9px 0; border-bottom:1px solid #f3f4f6; cursor:pointer; }
.pack-thumb { width:44px; height:44px; border-radius:8px; object-fit:cover; }
.pack-name { font-size:12.5px; font-weight:600; color:#111; }
.pack-date { font-size:10.5px; color:#6b7280; }
</style>
""", unsafe_allow_html=True)


# ─── セッションステート初期化 ─────────────────────────────────────
if "adding" not in st.session_state:
    st.session_state.adding = False        # BOX追加モード
if "selected_pack" not in st.session_state:
    st.session_state.selected_pack = None  # 選択中パック
if "updating" not in st.session_state:
    st.session_state.updating = False


# ─── ヘルパー関数 ─────────────────────────────────────────────────
def fmt(v: int | None) -> str:
    return f"¥{v:,}" if v is not None else "ー"

def diff_class(v: int) -> str:
    return "plus" if v > 0 else "minus" if v < 0 else "zero"

def diff_str(v: int) -> str:
    return f"+¥{v:,}" if v > 0 else f"¥{v:,}" if v < 0 else "¥0"


# ─── サマリー計算 ─────────────────────────────────────────────────
holdings = db.get_all_holdings()
total_snkr = sum((h["snkrdunk_price"] or 0) * h["qty"] for h in holdings)
total_mori = sum((h["morimori_price"] or 0) * h["qty"] for h in holdings if h["shrink"])

prev = db.get_prev_snapshot()
first = db.get_first_snapshot()
snapshots = db.get_snapshots()
latest_snap = snapshots[0] if snapshots else None

prev_diff_snkr = total_snkr - (prev["total_snkrdunk"] if prev else total_snkr)
first_diff_snkr = total_snkr - (first["total_snkrdunk"] if first else total_snkr)

last_updated = ""
if holdings and any(h["updated_at"] for h in holdings):
    times = [h["updated_at"] for h in holdings if h["updated_at"]]
    last_updated = max(times)[:16] if times else ""


# ─── 更新ボタン（最上部） ──────────────────────────────────────────────
label = f"最新相場に更新（最終: {last_updated}）" if last_updated else "最新相場に更新"
if st.button(label, type="primary", use_container_width=True, key="update_button_top"):
    st.session_state.updating = True

if st.session_state.updating:
    holdings_fresh = db.get_all_holdings()
    progress = st.progress(0, text="価格を取得中...")
    for i, h in enumerate(holdings_fresh):
        prices = scraper.fetch_prices(h["snkrdunk_id"], h["morimori_url"] if h["shrink"] else None)
        db.update_prices(h["id"], prices["snkrdunk"], prices["morimori"])
        progress.progress((i + 1) / max(len(holdings_fresh), 1), text=f"{h['pack_name']} を更新中...")

    # 更新後の合計でスナップショット保存
    updated = db.get_all_holdings()
    t_s = sum((h["snkrdunk_price"] or 0) * h["qty"] for h in updated)
    t_m = sum((h["morimori_price"] or 0) * h["qty"] for h in updated if h["shrink"])
    db.save_snapshot(t_s, t_m)
    st.session_state.updating = False
    st.rerun()


# ─── UI: サマリーエリア ────────────────────────────────────────────
st.markdown(f"""
<div class="summary-wrap">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:4px;">
    <div>
      <div class="summary-title">総資産</div>
      <div class="summary-val">{fmt(total_snkr)}</div>
    </div>
    <div>
      <div class="summary-title">買取金額</div>
      <div class="summary-val">{fmt(total_mori)}</div>
    </div>
  </div>
  <div class="diff-row">
    <div class="diff-card">
      <div class="diff-label">前回比</div>
      <div class="diff-val {diff_class(prev_diff_snkr)}">{diff_str(prev_diff_snkr)}</div>
    </div>
    <div class="diff-card">
      <div class="diff-label">累計増減</div>
      <div class="diff-val {diff_class(first_diff_snkr)}">{diff_str(first_diff_snkr)}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── 更新ボタン ──────────────────────────────────────────────────
label = f"最新相場に更新（最終: {last_updated}）" if last_updated else "最新相場に更新"
if st.button(label, type="primary", use_container_width=True):
    st.session_state.updating = True

if st.session_state.updating:
    holdings_fresh = db.get_all_holdings()
    progress = st.progress(0, text="価格を取得中...")
    for i, h in enumerate(holdings_fresh):
        prices = scraper.fetch_prices(h["snkrdunk_id"], h["morimori_url"] if h["shrink"] else None)
        db.update_prices(h["id"], prices["snkrdunk"], prices["morimori"])
        progress.progress((i + 1) / max(len(holdings_fresh), 1), text=f"{h['pack_name']} を更新中...")

    # 更新後の合計でスナップショット保存
    updated = db.get_all_holdings()
    t_s = sum((h["snkrdunk_price"] or 0) * h["qty"] for h in updated)
    t_m = sum((h["morimori_price"] or 0) * h["qty"] for h in updated if h["shrink"])
    db.save_snapshot(t_s, t_m)
    st.session_state.updating = False
    st.rerun()


# ─── BOX追加モード ────────────────────────────────────────────────
if st.session_state.adding:
    st.markdown("---")

    if st.session_state.selected_pack is None:
        # ① パック選択画面
        st.markdown('<div class="section-label">BOXを選択</div>', unsafe_allow_html=True)
        query = st.text_input("🔍 パック名で検索", placeholder="例: 151、テラスタル", label_visibility="collapsed")
        filtered = [p for p in PACKS if query.lower() in p["name"].lower()] if query else PACKS

        for pack in filtered:
            col_img, col_info, col_btn = st.columns([1, 4, 1.5])
            with col_img:
                st.image(pack["img"], width=44)
            with col_info:
                st.markdown(f"**{pack['name']}**  \n<span style='font-size:11px;color:#6b7280'>{pack['released_at']}</span>", unsafe_allow_html=True)
            with col_btn:
                if st.button("選択", key=f"sel_{pack['id']}"):
                    st.session_state.selected_pack = pack
                    st.rerun()

        if st.button("キャンセル", use_container_width=True):
            st.session_state.adding = False
            st.rerun()

    else:
        # ② シュリンク選択 or 確認画面
        pack = st.session_state.selected_pack
        col_img, col_info = st.columns([1, 4])
        with col_img:
            st.image(pack["img"], width=52)
        with col_info:
            st.markdown(f"**{pack['name']}**  \n<span style='font-size:11px;color:#6b7280'>{pack['released_at']}</span>", unsafe_allow_html=True)

        shrink_fixed = pack.get("shrink_fixed")  # True/False/None

        if shrink_fixed is True:
            # シュリンク有固定（スニダン側でシュリンク有専用IDのもの）
            st.success("📦 このエントリはシュリンク有で登録されます")
            has_shrink = True
        elif shrink_fixed is False:
            # シュリンク無固定
            st.warning("🗂 このエントリはシュリンク無で登録されます（森森買取対象外）")
            has_shrink = False
        else:
            # 選択式
            st.markdown("**シュリンクの状態を選択**")
            shrink_choice = st.radio(
                "シュリンク",
                ["📦 シュリンク有（新品未開封）", "🗂 シュリンク無（森森買取対象外）"],
                label_visibility="collapsed",
            )
            has_shrink = shrink_choice.startswith("📦")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← 戻る", use_container_width=True):
                st.session_state.selected_pack = None
                st.rerun()
        with col2:
            if st.button("✅ 追加する", type="primary", use_container_width=True):
                db.add_holding(
                    pack_id=str(pack["id"]),
                    pack_name=pack["name"],
                    img_url=pack["img"],
                    shrink=has_shrink,
                    snkrdunk_id=pack.get("snkrdunk_id"),
                    morimori_url=pack.get("morimori_url") if has_shrink else None,
                )
                st.session_state.adding = False
                st.session_state.selected_pack = None
                st.rerun()


# ─── BOXリスト ────────────────────────────────────────────────────
else:
    st.markdown('<div class="section-label">保有BOX一覧</div>', unsafe_allow_html=True)

    holdings = db.get_all_holdings()
    if not holdings:
        st.info("BOXがまだ登録されていません。下の「＋ BOXを追加する」から登録してください。")

    for h in holdings:
        snkr_price = h["snkrdunk_price"]
        mori_price = h["morimori_price"]
        qty = h["qty"]
        subtotal = (snkr_price or 0) * qty
        shrink = bool(h["shrink"])

        # パック名を分割（拡張パック「〇〇」 → 拡張パック + 〇〇）
        pack_name = h['pack_name']
        if "「" in pack_name and "」" in pack_name:
            prefix = pack_name.split("「")[0].strip()  # "拡張パック"
            main_name = pack_name.split("「")[1].split("」")[0]  # "ニンジャスピナー"
            name_display = f"{prefix}<br>{main_name}"
        else:
            name_display = pack_name

        badge = '<span class="badge badge-shrink">シュリンク有</span>' if shrink else '<span class="badge badge-noshrink">シュリンク無</span>'
        
        # 価格を横並びで表示
        price_html = f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;">
          <div class="price-val">{fmt(snkr_price)}</div>
          <div class="price-val">{fmt(mori_price) if shrink else "ー"}</div>
        </div>
        """

        # 小計も同じレイアウトで（各列の合計を表示）
        subtotal_snkr = (snkr_price or 0) * qty
        subtotal_mori = (mori_price or 0) * qty if shrink else 0
        footer_html = f"""
        <div style="display:flex;align-items:center;width:100%;">
          <span class="footer-label" style="width:56px;">小計（× {qty}）</span>
          <div style="flex:1;"></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;width:120px;">
            <div class="footer-val">{fmt(subtotal_snkr)}</div>
            <div class="footer-val">{fmt(subtotal_mori) if shrink else "ー"}</div>
          </div>
          <div style="width:66px;"></div>
        </div>
        """

        st.markdown(f"""
        <div class="box-card">
          <div style="display:grid;grid-template-columns:56px 1fr 1fr auto;gap:8px;padding:10px;align-items:center;">
            <img src="{h['img_url']}" style="width:56px;height:56px;border-radius:8px;object-fit:cover;" onerror="this.src='https://via.placeholder.com/56'">
            <div>
              <div class="box-name">{name_display}</div>
              {badge}
            </div>
            <div class="price-block">
              {price_html}
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:8px;">
              <input type="number" value="{qty}" min="1" max="99" style="width:50px;height:36px;text-align:center;border-radius:8px;border:0.5px solid var(--color-border-secondary);background:var(--color-background-secondary);font-size:14px;" onchange="updateQuantity({h['id']}, this.value)">
              <button onclick="deleteHolding({h['id']})" style="background:none;border:none;color:var(--color-text-tertiary);font-size:16px;cursor:pointer;padding:4px;">🗑</button>
            </div>
          </div>
          <div class="box-footer">
            {footer_html}
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── BOX追加ボタン（リストの下）────────────────────────────
    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
    if st.button("＋ BOXを追加する", use_container_width=True):
        st.session_state.adding = True
        st.session_state.selected_pack = None
        st.rerun()
