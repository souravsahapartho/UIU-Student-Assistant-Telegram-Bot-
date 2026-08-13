import sqlite3
from typing import Any, Optional

DB_NAME = "uiu_assistant.db"


def get_connection():
    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_calendars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            content_hash TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    conn.commit()
    conn.close()


def log_user_activity(
    telegram_id: int,
    first_name: str,
    username: Optional[str],
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (
            telegram_id,
            first_name,
            username
        )
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            first_name=excluded.first_name,
            username=excluded.username,
            last_active=CURRENT_TIMESTAMP
        """,
        (
            telegram_id,
            first_name,
            username,
        ),
    )

    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT telegram_id
        FROM users
        WHERE telegram_id IS NOT NULL
        """)

    rows = cursor.fetchall()
    conn.close()

    return [row["telegram_id"] for row in rows]


def get_setting(
    key: str,
    default: Any = None,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value FROM settings WHERE key = ?",
        (key,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        value = row["value"]

        try:
            number = float(value)

            if number.is_integer():
                return int(number)

            return number

        except ValueError:
            return value

    return default


def update_setting(
    key: str,
    value: Any,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO settings (
            key,
            value
        )
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET
            value=excluded.value,
            updated_at=CURRENT_TIMESTAMP
        """,
        (
            key,
            str(value),
        ),
    )

    conn.commit()
    conn.close()


def get_calendar_by_url(url: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM academic_calendars
        WHERE url = ?
        """,
        (url,),
    )

    row = cursor.fetchone()
    conn.close()

    return row


def save_calendar(
    title: str,
    url: str,
    content_hash: str,
    content: str,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO academic_calendars (
            title,
            url,
            content_hash,
            content
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            title=excluded.title,
            content_hash=excluded.content_hash,
            content=excluded.content,
            updated_at=CURRENT_TIMESTAMP
        """,
        (
            title,
            url,
            content_hash,
            content,
        ),
    )

    conn.commit()
    conn.close()


def get_calendars():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM academic_calendars
        ORDER BY id DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    return rows
