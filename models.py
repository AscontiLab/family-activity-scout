"""SQLite Datenbank-Schema und CRUD-Funktionen."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from config import DB_PATH, ALL_TAGS

# ---------------------------------------------------------------------------
# Connection Helper
# ---------------------------------------------------------------------------

@contextmanager
def _connect(db_path: Path = DB_PATH):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def init_db(db_path: Path = DB_PATH) -> None:
    """Erstellt alle Tabellen und Default-Daten."""
    with _connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS activities (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                source      TEXT    NOT NULL,
                source_url  TEXT,
                source_id   TEXT,
                title       TEXT    NOT NULL,
                description TEXT,
                location_name TEXT,
                address     TEXT,
                lat         REAL,
                lon         REAL,
                date_start  TEXT,
                date_end    TEXT,
                time_info   TEXT,
                is_recurring INTEGER DEFAULT 0,
                is_permanent INTEGER DEFAULT 0,
                is_special  INTEGER DEFAULT 0,
                tags        TEXT    DEFAULT '[]',
                age_min     INTEGER DEFAULT 0,
                age_max     INTEGER DEFAULT 99,
                price_info  TEXT,
                image_url   TEXT,
                scraped_at  TEXT    NOT NULL,
                active      INTEGER DEFAULT 1,
                UNIQUE(source, source_id)
            );

            CREATE TABLE IF NOT EXISTS preferences (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                tag    TEXT    UNIQUE NOT NULL,
                weight REAL   DEFAULT 1.0
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER NOT NULL REFERENCES activities(id),
                rating      INTEGER NOT NULL,
                rated_at    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS done_tracker (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER NOT NULL REFERENCES activities(id),
                done_at     TEXT    NOT NULL,
                notes       TEXT
            );
        """)

        # Default-Preferences einfuegen
        for tag in ALL_TAGS:
            conn.execute(
                "INSERT OR IGNORE INTO preferences (tag, weight) VALUES (?, 1.0)",
                (tag,),
            )


# ---------------------------------------------------------------------------
# Activities CRUD
# ---------------------------------------------------------------------------

def upsert_activity(data: dict, db_path: Path = DB_PATH) -> int:
    """Fuegt eine Aktivitaet ein oder aktualisiert sie (Deduplizierung via source+source_id)."""
    now = datetime.now(timezone.utc).isoformat()
    tags_json = json.dumps(data.get("tags", []), ensure_ascii=False)

    with _connect(db_path) as conn:
        conn.execute("""
            INSERT INTO activities (
                source, source_url, source_id, title, description,
                location_name, address, lat, lon,
                date_start, date_end, time_info,
                is_recurring, is_permanent, is_special,
                tags, age_min, age_max, price_info, image_url, scraped_at, active
            ) VALUES (
                :source, :source_url, :source_id, :title, :description,
                :location_name, :address, :lat, :lon,
                :date_start, :date_end, :time_info,
                :is_recurring, :is_permanent, :is_special,
                :tags, :age_min, :age_max, :price_info, :image_url, :scraped_at, 1
            )
            ON CONFLICT(source, source_id) DO UPDATE SET
                title = excluded.title,
                description = excluded.description,
                location_name = excluded.location_name,
                address = excluded.address,
                lat = excluded.lat,
                lon = excluded.lon,
                date_start = excluded.date_start,
                date_end = excluded.date_end,
                time_info = excluded.time_info,
                is_special = excluded.is_special,
                tags = excluded.tags,
                price_info = excluded.price_info,
                image_url = excluded.image_url,
                scraped_at = excluded.scraped_at,
                active = 1
        """, {
            "source": data["source"],
            "source_url": data.get("source_url"),
            "source_id": data.get("source_id"),
            "title": data["title"],
            "description": data.get("description"),
            "location_name": data.get("location_name"),
            "address": data.get("address"),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "date_start": data.get("date_start"),
            "date_end": data.get("date_end"),
            "time_info": data.get("time_info"),
            "is_recurring": data.get("is_recurring", 0),
            "is_permanent": data.get("is_permanent", 0),
            "is_special": data.get("is_special", 0),
            "tags": tags_json,
            "age_min": data.get("age_min", 0),
            "age_max": data.get("age_max", 99),
            "price_info": data.get("price_info"),
            "image_url": data.get("image_url"),
            "scraped_at": now,
        })
        row = conn.execute("SELECT last_insert_rowid()").fetchone()
        return row[0]


def get_active_activities(db_path: Path = DB_PATH) -> list[dict]:
    """Gibt alle aktiven Aktivitaeten zurueck."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM activities WHERE active = 1 ORDER BY date_start ASC NULLS LAST"
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        result.append(d)
    return result


def get_activity_by_id(activity_id: int, db_path: Path = DB_PATH) -> dict | None:
    """Gibt eine einzelne Aktivitaet zurueck."""
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM activities WHERE id = ?", (activity_id,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["tags"] = json.loads(d["tags"]) if d["tags"] else []
    return d


def deactivate_expired(db_path: Path = DB_PATH) -> int:
    """Setzt abgelaufene Events auf active=0.

    - Events mit date_end < heute → deaktivieren
    - Events ohne Datum die aelter als 14 Tage sind → deaktivieren
    - Permanente Attraktionen bleiben immer aktiv
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
    with _connect(db_path) as conn:
        # Events mit abgelaufenem Enddatum
        c1 = conn.execute(
            "UPDATE activities SET active = 0 "
            "WHERE date_end IS NOT NULL AND date_end < ? AND active = 1",
            (today,),
        ).rowcount
        # Events ohne Datum, aelter als 14 Tage, nicht permanent
        c2 = conn.execute(
            "UPDATE activities SET active = 0 "
            "WHERE date_end IS NULL AND date_start IS NULL "
            "AND is_permanent = 0 AND scraped_at < ? AND active = 1",
            (cutoff,),
        ).rowcount
        return c1 + c2


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------

def get_preferences(db_path: Path = DB_PATH) -> dict[str, float]:
    """Gibt Tag-Weights als Dict zurueck."""
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT tag, weight FROM preferences").fetchall()
    return {r["tag"]: r["weight"] for r in rows}


def update_preferences(weights: dict[str, float], db_path: Path = DB_PATH) -> None:
    """Aktualisiert Tag-Weights."""
    with _connect(db_path) as conn:
        for tag, weight in weights.items():
            conn.execute(
                "UPDATE preferences SET weight = ? WHERE tag = ?",
                (max(0.1, min(3.0, weight)), tag),
            )


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

def add_feedback(activity_id: int, rating: int, db_path: Path = DB_PATH) -> None:
    """Speichert Feedback (+1 oder -1) und passt Tag-Weights an."""
    now = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO feedback (activity_id, rating, rated_at) VALUES (?, ?, ?)",
            (activity_id, rating, now),
        )

        # Tag-Weights anpassen
        row = conn.execute("SELECT tags FROM activities WHERE id = ?", (activity_id,)).fetchone()
        if row and row["tags"]:
            tags = json.loads(row["tags"])
            delta = 0.15 if rating > 0 else -0.10
            for tag in tags:
                conn.execute(
                    "UPDATE preferences SET weight = MIN(3.0, MAX(0.1, weight + ?)) WHERE tag = ?",
                    (delta, tag),
                )


def get_feedback_for_activity(activity_id: int, db_path: Path = DB_PATH) -> list[dict]:
    """Gibt Feedback-Historie fuer eine Aktivitaet."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM feedback WHERE activity_id = ? ORDER BY rated_at DESC",
            (activity_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Done Tracker
# ---------------------------------------------------------------------------

def mark_done(activity_id: int, notes: str = "", db_path: Path = DB_PATH) -> None:
    """Markiert eine Aktivitaet als gemacht."""
    now = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO done_tracker (activity_id, done_at, notes) VALUES (?, ?, ?)",
            (activity_id, now, notes),
        )


def get_done_ids(db_path: Path = DB_PATH) -> set[int]:
    """Gibt IDs aller bereits gemachten Aktivitaeten zurueck."""
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT DISTINCT activity_id FROM done_tracker").fetchall()
    return {r["activity_id"] for r in rows}
