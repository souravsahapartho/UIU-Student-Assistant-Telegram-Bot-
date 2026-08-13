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
            title TEXT NOT NULL,
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_settings (
            telegram_id INTEGER PRIMARY KEY,
            enabled INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    conn.commit()
    conn.close()


def log_user_activity(
    telegram_id: int,
    first_name: str,
    username: Optional[str] = None,
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
            first_name = excluded.first_name,
            username = excluded.username,
            last_active = CURRENT_TIMESTAMP
        """,
        (
            telegram_id,
            first_name,
            username,
        ),
    )

    cursor.execute(
        """
        INSERT INTO notification_settings (
            telegram_id,
            enabled
        )
        VALUES (?, 1)
        ON CONFLICT(telegram_id) DO NOTHING
        """,
        (telegram_id,),
    )

    conn.commit()
    conn.close()


def get_user(
    telegram_id: int,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    row = cursor.fetchone()
    conn.close()

    return row


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT telegram_id
        FROM users
        WHERE telegram_id IS NOT NULL
        ORDER BY id ASC
        """)

    rows = cursor.fetchall()
    conn.close()

    return [row["telegram_id"] for row in rows]


def get_user_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM users
        """)

    row = cursor.fetchone()
    conn.close()

    return row["count"]


def get_setting(
    key: str,
    default: Any = None,
):
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

    if row is None:
        return default

    value = row["value"]

    try:
        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except (ValueError, TypeError):
        return value


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
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            key,
            str(value),
        ),
    )

    conn.commit()
    conn.close()


def get_recent_notices(
    limit: int = 10,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            description,
            url,
            created_at
        FROM notices
        ORDER BY datetime(created_at) DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def add_notice(
    title: str,
    description: str = "",
    url: str = "",
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notices (
            title,
            description,
            url
        )
        VALUES (?, ?, ?)
        """,
        (
            title,
            description,
            url,
        ),
    )

    conn.commit()

    notice_id = cursor.lastrowid

    conn.close()

    return notice_id


def get_notice_by_url(
    url: str,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM notices
        WHERE url = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (url,),
    )

    row = cursor.fetchone()
    conn.close()

    return row


def get_notice(
    notice_id: int,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM notices
        WHERE id = ?
        """,
        (notice_id,),
    )

    row = cursor.fetchone()
    conn.close()

    return row


def delete_notice(
    notice_id: int,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM notices
        WHERE id = ?
        """,
        (notice_id,),
    )

    conn.commit()

    deleted = cursor.rowcount > 0

    conn.close()

    return deleted


def get_notification_status(
    telegram_id: int,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT enabled
        FROM notification_settings
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            """
            INSERT INTO notification_settings (
                telegram_id,
                enabled
            )
            VALUES (?, 1)
            """,
            (telegram_id,),
        )

        conn.commit()
        conn.close()

        return True

    conn.close()

    return bool(row["enabled"])


def set_notification_status(
    telegram_id: int,
    enabled: bool,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notification_settings (
            telegram_id,
            enabled
        )
        VALUES (?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            enabled = excluded.enabled,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            telegram_id,
            1 if enabled else 0,
        ),
    )

    conn.commit()
    conn.close()


def toggle_notification(
    telegram_id: int,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT enabled
        FROM notification_settings
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    row = cursor.fetchone()

    if row is None:

        new_status = 1

        cursor.execute(
            """
            INSERT INTO notification_settings (
                telegram_id,
                enabled
            )
            VALUES (?, ?)
            """,
            (
                telegram_id,
                new_status,
            ),
        )

    else:

        current_status = bool(row["enabled"])

        new_status = 0 if current_status else 1

        cursor.execute(
            """
            UPDATE notification_settings
            SET
                enabled = ?,
                updated_at = CURRENT_TIMESTAMP
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


def get_notification_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.telegram_id
        FROM users u
        LEFT JOIN notification_settings n
            ON u.telegram_id = n.telegram_id
        WHERE COALESCE(n.enabled, 1) = 1
        AND u.telegram_id IS NOT NULL
        ORDER BY u.id ASC
        """)

    rows = cursor.fetchall()
    conn.close()

    return [row["telegram_id"] for row in rows]


def get_calendar_by_url(
    url: str,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM academic_calendars
        WHERE url = ?
        LIMIT 1
        """,
        (url,),
    )

    row = cursor.fetchone()
    conn.close()

    return row


def get_calendar_by_id(
    calendar_id: int,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM academic_calendars
        WHERE id = ?
        """,
        (calendar_id,),
    )

    row = cursor.fetchone()
    conn.close()

    return row


def save_calendar(
    title: str,
    url: str,
    content_hash: str,
    content: str = "",
):
    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute(
        """
        SELECT id
        FROM academic_calendars
        WHERE url = ?
        """,
        (url,),
    ).fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE academic_calendars
            SET
                title = ?,
                content_hash = ?,
                content = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE url = ?
            """,
            (
                title,
                content_hash,
                content,
                url,
            ),
        )

        calendar_id = existing["id"]

    else:

        cursor.execute(
            """
            INSERT INTO academic_calendars (
                title,
                url,
                content_hash,
                content
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                url,
                content_hash,
                content,
            ),
        )

        calendar_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return calendar_id


def get_calendars(
    limit: Optional[int] = None,
):
    conn = get_connection()
    cursor = conn.cursor()

    if limit is not None:

        cursor.execute(
            """
            SELECT *
            FROM academic_calendars
            ORDER BY datetime(updated_at) DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )

    else:

        cursor.execute("""
            SELECT *
            FROM academic_calendars
            ORDER BY datetime(updated_at) DESC, id DESC
            """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_latest_calendar():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM academic_calendars
        ORDER BY datetime(updated_at) DESC, id DESC
        LIMIT 1
        """)

    row = cursor.fetchone()
    conn.close()

    return row


def delete_calendar(
    calendar_id: int,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM academic_calendars
        WHERE id = ?
        """,
        (calendar_id,),
    )

    conn.commit()

    deleted = cursor.rowcount > 0

    conn.close()

    return deleted
