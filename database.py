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

def add_holding(pack_id, pack_name: str, img_url: str, shrink: bool,
                snkrdunk_id: str | None, morimori_url: str | None,
                mobile_ichiban_url: str | None = None) -> int:
    """BOXを1件追加。同一pack_id + shrinkが既にあればqtyを+1して返す。"""
    try:
        pack_id_int = int(pack_id)
    except (ValueError, TypeError):
        pack_id_int = pack_id

    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id, qty FROM holdings WHERE pack_id=? AND shrink=?",
            (pack_id_int, int(shrink))
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
            (pack_id_int, pack_name, img_url, int(shrink),
             snkrdunk_id, morimori_url, mobile_ichiban_url)
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


def update_qty_delta(holding_id: int, delta: int):
    """数量を delta だけ増減（最低1）"""
    with get_conn() as conn:
        conn.execute(
            "UPDATE holdings SET qty = MAX(1, qty + ?) WHERE id=?",
            (delta, holding_id)
        )


def update_prices(holding_id: int, snkrdunk_price: int | None, morimori_price: int | None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute(
            """UPDATE holdings
               SET snkrdunk_price=?, morimori_price=?, updated_at=?
               WHERE id=?""",
            (snkrdunk_price, morimori_price, now, holding_id)
        )


def update_img_url(holding_id: int, img_url: str):
    """画像URLを更新する。"""
    with get_conn() as conn:
        conn.execute(
            "UPDATE holdings SET img_url=? WHERE id=?",
            (img_url, holding_id)
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
    """スナップショットを新しい順で返す。limit指定可。"""
    with get_conn() as conn:
        if limit is not None:
            rows = conn.execute(
                "SELECT * FROM snapshots ORDER BY recorded_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM snapshots ORDER BY recorded_at DESC"
            ).fetchall()

        result = []
        for r in rows:
            d = dict(r)
            d["snkrdunk_total"] = d.get("total_snkrdunk", 0)
            d["morimori_total"] = d.get("total_morimori", 0)
            result.append(d)
        return result


def get_prev_snapshot() -> dict | None:
    snaps = get_snapshots(limit=2)
    return snaps[1] if len(snaps) >= 2 else None


def get_first_snapshot() -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM snapshots ORDER BY recorded_at ASC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["snkrdunk_total"] = d.get("total_snkrdunk", 0)
        d["morimori_total"] = d.get("total_morimori", 0)
        return d
