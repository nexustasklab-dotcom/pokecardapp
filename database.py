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
        CREATE TABLE IF NOT EXISTS holdings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pack_id     INTEGER NOT NULL,
            pack_name   TEXT    NOT NULL,
            img_url     TEXT    NOT NULL,
            shrink      INTEGER NOT NULL,
            qty         INTEGER NOT NULL DEFAULT 1,
            snkrdunk_id TEXT,
            morimori_url TEXT,
            mobile_ichiban_url TEXT,
            snkrdunk_price INTEGER,
            morimori_price INTEGER,
            mobile_ichiban_price INTEGER,
            updated_at  TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS snapshots (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            total_snkrdunk  INTEGER NOT NULL,
            total_morimori  INTEGER NOT NULL,
            recorded_at     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
        """)


# ─── holdings CRUD ────────────────────────────────────────────────

def add_holding(pack_id: int, pack_name: str, img_url: str, shrink: bool,
                snkrdunk_id: str | None, morimori_url: str | None,
                mobile_ichiban_url: str | None = None) -> int:
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
               (pack_id, pack_name, img_url, shrink, qty, snkrdunk_id, morimori_url, mobile_ichiban_url)
               VALUES (?, ?, ?, ?, 1, ?, ?, ?)""",
            (pack_id, pack_name, img_url, int(shrink), snkrdunk_id, morimori_url, mobile_ichiban_url)
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


def update_prices(holding_id: int, snkrdunk_price: int | None,
                  morimori_price: int | None,
                  img_url: str | None = None,
                  pack_name: str | None = None):
    """
    価格を更新する。img_url / pack_name が渡されたら一緒に上書きする。
    （スニダンから取得した正しい画像と商品名で更新する用途）
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        if img_url and pack_name:
            conn.execute(
                """UPDATE holdings
                   SET snkrdunk_price=?, morimori_price=?, img_url=?, pack_name=?, updated_at=?
                   WHERE id=?""",
                (snkrdunk_price, morimori_price, img_url, pack_name, now, holding_id)
            )
        elif img_url:
            conn.execute(
                """UPDATE holdings
                   SET snkrdunk_price=?, morimori_price=?, img_url=?, updated_at=?
                   WHERE id=?""",
                (snkrdunk_price, morimori_price, img_url, now, holding_id)
            )
        else:
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


def get_snapshots(limit: int | None = None) -> list[dict]:
    with get_conn() as conn:
        sql = "SELECT * FROM snapshots ORDER BY recorded_at DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]


def get_prev_snapshot() -> dict | None:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM snapshots ORDER BY recorded_at DESC LIMIT 2"
        ).fetchall()
        return dict(rows[1]) if len(rows) >= 2 else None


def get_first_snapshot() -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM snapshots ORDER BY recorded_at ASC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
