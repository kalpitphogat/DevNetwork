"""
Neon PostgreSQL Connector — for persisting completed briefings.

Saves completed runs, source metadata, and landscape data.
Gracefully falls back to in-memory dictionary if DATABASE_URL is not set.
"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

_in_memory_db = {}


def _db_url() -> str:
    """Read DATABASE_URL at call time so late-loaded .env values are picked up."""
    return os.getenv("DATABASE_URL", "")


def init_db():
    """Create tables if they don't exist in PostgreSQL."""
    if not _db_url():
        print("[Neon DB] No DATABASE_URL set. Running in stateless mock mode (In-Memory).")
        return False

    conn = None
    try:
        conn = psycopg2.connect(_db_url())
        cur = conn.cursor()
        
        # Create briefings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS briefings (
                id SERIAL PRIMARY KEY,
                run_id VARCHAR(100) UNIQUE NOT NULL,
                your_company VARCHAR(100) NOT NULL,
                competitors JSONB NOT NULL,
                briefing_data JSONB NOT NULL,
                confidence_score VARCHAR(10) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        print("[Neon DB] PostgreSQL connection successful. Table 'briefings' initialized.")
        return True
    except Exception as e:
        print(f"[Neon DB] Failed to connect or initialize PostgreSQL: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def save_briefing(run_id: str, your_company: str, competitors: list, briefing_data: dict, confidence_score: str):
    """Save a briefing run to PostgreSQL or in-memory fallback."""
    if not _db_url():
        _in_memory_db[run_id] = {
            "run_id": run_id,
            "your_company": your_company,
            "competitors": competitors,
            "briefing_data": briefing_data,
            "confidence_score": confidence_score
        }
        print(f"[Neon DB] Saved run {run_id} to In-Memory fallback.")
        return True

    conn = None
    try:
        conn = psycopg2.connect(_db_url())
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO briefings (run_id, your_company, competitors, briefing_data, confidence_score)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE 
            SET briefing_data = EXCLUDED.briefing_data, confidence_score = EXCLUDED.confidence_score;
            """,
            (run_id, your_company, json.dumps(competitors), json.dumps(briefing_data), confidence_score)
        )
        conn.commit()
        print(f"[Neon DB] Saved run {run_id} to Neon PostgreSQL.")
        return True
    except Exception as e:
        print(f"[Neon DB] Failed to save briefing to PostgreSQL: {e}")
        if conn:
            conn.rollback()
        # Fallback to memory
        _in_memory_db[run_id] = {
            "run_id": run_id,
            "your_company": your_company,
            "competitors": competitors,
            "briefing_data": briefing_data,
            "confidence_score": confidence_score
        }
        return False
    finally:
        if conn:
            conn.close()


def get_recent_briefings(limit: int = 10) -> list:
    """Retrieve the most recent completed briefing runs."""
    if not _db_url():
        return [
            {
                "run_id": rid,
                "your_company": v["your_company"],
                "competitors": v["competitors"],
                "confidence_score": v["confidence_score"],
            }
            for rid, v in list(_in_memory_db.items())[-limit:]
        ]

    conn = None
    try:
        conn = psycopg2.connect(_db_url(), cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT run_id, your_company, competitors, confidence_score, created_at
            FROM briefings
            ORDER BY created_at DESC
            LIMIT %s;
            """,
            (limit,)
        )
        rows = cur.fetchall()
        return [
            {
                "run_id": row["run_id"],
                "your_company": row["your_company"],
                "competitors": row["competitors"] if isinstance(row["competitors"], list)
                               else json.loads(row["competitors"]),
                "confidence_score": row["confidence_score"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    except Exception as e:
        print(f"[Neon DB] Failed to fetch recent briefings: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_briefing(run_id: str) -> dict:
    """Retrieve briefing data by run_id."""
    if not _db_url():
        return _in_memory_db.get(run_id)

    conn = None
    try:
        conn = psycopg2.connect(_db_url(), cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("SELECT * FROM briefings WHERE run_id = %s;", (run_id,))
        row = cur.fetchone()
        if row:
            # Parse json fields back to dicts
            return {
                "run_id": row["run_id"],
                "your_company": row["your_company"],
                "competitors": json.loads(row["competitors"]) if isinstance(row["competitors"], str) else row["competitors"],
                "briefing_data": json.loads(row["briefing_data"]) if isinstance(row["briefing_data"], str) else row["briefing_data"],
                "confidence_score": row["confidence_score"]
            }
        return None
    except Exception as e:
        print(f"[Neon DB] Failed to query briefing: {e}")
        return _in_memory_db.get(run_id)
    finally:
        if conn:
            conn.close()
