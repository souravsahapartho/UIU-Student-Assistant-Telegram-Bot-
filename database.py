import sqlite3
from typing import Dict, List, Any, Optional

DB_NAME = "uiu_assistant.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            first_name TEXT,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Settings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Notices Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def log_user_activity(telegram_id: int, first_name: str, username: Optional[str]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (telegram_id, first_name, username) 
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET 
        first_name=excluded.first_name, 
        username=excluded.username,
        last_active=CURRENT_TIMESTAMP
    """,
        (telegram_id, first_name, username),
    )
    conn.commit()
    conn.close()


def get_setting(key: str, default: Any) -> Any:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()

    if row:
        try:
            # Try to convert to float if it looks like a number
            val = float(row["value"])
            return int(val) if val.is_integer() else val
        except ValueError:
            return row["value"]
    return default


def update_setting(key: str, value: Any):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO settings (key, value) 
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET 
        value=excluded.value,
        updated_at=CURRENT_TIMESTAMP
    """,
        (key, str(value)),
    )
    conn.commit()
    conn.close()
