# database.py
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "pokecardapp.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初回起動時にテーブルを作成する。"""
    with get_conn() as conn:
        conn.executescript("""
        -- 保有BOX一覧
        CREATE TABLE IF NOT EXISTS holdings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pack_id     INTEGER NOT NULL,        -- cardrush pack ID
            pack_name   TEXT    NOT NULL,
            img_url     TEXT    NOT NULL,
            shrink      INTEGER NOT NULL,        -- 1=あり, 0=なし
            qty         INTEGER NOT NULL DEFAULT 1,
            snkrdunk_id TEXT,                   -- スニダン apparel ID
            morimori_url TEXT,                  -- 森森 商品URL（shrink=0はNULL）
            snkrdunk_price INTEGER,             -- 最新スニダン相場（1個）
            morimori_price INTEGER,             -- 最新森森買取（1個）
            updated_at  TEXT,                   -- 最終価格更新日時
            created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );

        -- 資産スナップショット（「更新」ボタン押下ごとに記録）
        CREATE TABLE IF NOT EXISTS snapshots (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            total_snkrdunk  INTEGER NOT NULL,   -- その時点の総スニダン相場合計
            total_morimori  INTEGER NOT NULL,   -- その時点の総森森買取合計
            recorded_at     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
        """)


# ─── holdings CRUD ────────────────────────────────────────────────

def add_holding(pack_id: int, pack_name: str, img_url: str, shrink: bool,
                snkrdunk_id: str | None, morimori_url: str | None) -> int:
    """BOXを1件追加。同一pack_id + shrinkが既にあればqtyを+1して返す。"""
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id, qty FROM holdings WHERE pack_id=? AND shrink=?",
            (pack_id, int(shrink))
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE holdings SET qty=qty+1 WHERE id=?", (existing["id"],)
            )
            return existing["id"]
        cur = conn.execute(
            """INSERT INTO holdings
               (pack_id, pack_name, img_url, shrink, qty, snkrdunk_id, morimori_url)
               VALUES (?, ?, ?, ?, 1, ?, ?)""",
            (pack_id, pack_name, img_url, int(shrink), snkrdunk_id, morimori_url)
        )
        return cur.lastrowid


def get_all_holdings() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM holdings ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def update_qty(holding_id: int, qty: int):
    with get_conn() as conn:
        conn.execute("UPDATE holdings SET qty=? WHERE id=?", (qty, holding_id))


def update_prices(holding_id: int, snkrdunk_price: int | None, morimori_price: int | None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute(
            """UPDATE holdings
               SET snkrdunk_price=?, morimori_price=?, updated_at=?
               WHERE id=?""",
            (snkrdunk_price, morimori_price, now, holding_id)
        )


def delete_holding(holding_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM holdings WHERE id=?", (holding_id,))


# ─── snapshots ─────────────────────────────────────────────────────

def save_snapshot(total_snkrdunk: int, total_morimori: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO snapshots (total_snkrdunk, total_morimori) VALUES (?, ?)",
            (total_snkrdunk, total_morimori)
        )


def get_snapshots() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM snapshots ORDER BY recorded_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_prev_snapshot() -> dict | None:
    """前回（最新の1つ前）のスナップショットを返す。"""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM snapshots ORDER BY recorded_at DESC LIMIT 2"
        ).fetchall()
        # rows[0]=最新, rows[1]=前回
        return dict(rows[1]) if len(rows) >= 2 else None


def get_first_snapshot() -> dict | None:
    """初回（最古）のスナップショットを返す。"""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM snapshots ORDER BY recorded_at ASC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
