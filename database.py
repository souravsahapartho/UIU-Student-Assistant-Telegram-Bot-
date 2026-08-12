import sqlite3
from typing import List, Any, Optional
import logging

DB_NAME = "uiu_assistant.db"

logger = logging.getLogger(__name__)


def get_connection():
    conn = sqlite3.connect(DB_NAME)
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
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notifications_enabled INTEGER DEFAULT 1
        )
    """)

    try:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN notifications_enabled " "INTEGER DEFAULT 1"
        )
    except sqlite3.OperationalError:
        pass

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
            title TEXT UNIQUE,
            link TEXT,
            published_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_all_subscribers() -> List[int]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT telegram_id
        FROM users
        WHERE notifications_enabled = 1
        """)

    rows = cursor.fetchall()
    conn.close()

    return [row["telegram_id"] for row in rows]


def add_notice_if_new(
    title: str,
    link: str,
    published_date: str,
) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO notices (
                title,
                link,
                published_date
            )
            VALUES (?, ?, ?)
            """,
            (
                title,
                link,
                published_date,
            ),
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_recent_notices(
    limit: int = 5,
) -> List[sqlite3.Row]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM notices
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_notification_status(
    telegram_id: int,
) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT notifications_enabled
        FROM users
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return bool(row["notifications_enabled"])

    return True


def toggle_notification(
    telegram_id: int,
) -> bool:
    current_status = get_notification_status(telegram_id)

    new_status = 0 if current_status else 1

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET notifications_enabled = ?
        WHERE telegram_id = ?
        """,
        (
            new_status,
            telegram_id,
        ),
    )

    conn.commit()
    conn.close()

    return bool(new_status)


def get_setting(
    key: str,
    default: Any,
) -> Any:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT value
        FROM settings
        WHERE key = ?
        """,
        (key,),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        try:
            val = float(row["value"])

            if val.is_integer():
                return int(val)

            return val

        except ValueError:
            return row["value"]

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
