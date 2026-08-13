import logging
import sqlite3
from typing import Any, Optional

DB_NAME = "uiu_assistant.db"

logger = logging.getLogger(__name__)


def get_connection():
    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def column_exists(
    cursor,
    table_name: str,
    column_name: str,
):
    cursor.execute(f"PRAGMA table_info({table_name})")

    columns = cursor.fetchall()

    return any(row["name"] == column_name for row in columns)


def ensure_column(
    cursor,
    table_name: str,
    column_name: str,
    definition: str,
):
    if not column_exists(
        cursor,
        table_name,
        column_name,
    ):
        cursor.execute(f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {definition}
            """)


def init_db():
    conn = get_connection()

    try:
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

        ensure_column(
            cursor,
            "users",
            "notifications_enabled",
            "INTEGER DEFAULT 1",
        )

        ensure_column(
            cursor,
            "users",
            "first_name",
            "TEXT",
        )

        ensure_column(
            cursor,
            "users",
            "username",
            "TEXT",
        )

        ensure_column(
            cursor,
            "users",
            "created_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

        ensure_column(
            cursor,
            "users",
            "last_active",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

        ensure_column(
            cursor,
            "notices",
            "description",
            "TEXT",
        )

        ensure_column(
            cursor,
            "notices",
            "url",
            "TEXT",
        )

        ensure_column(
            cursor,
            "notices",
            "link",
            "TEXT",
        )

        ensure_column(
            cursor,
            "notices",
            "published_date",
            "TEXT",
        )

        ensure_column(
            cursor,
            "academic_calendars",
            "content_hash",
            "TEXT DEFAULT ''",
        )

        ensure_column(
            cursor,
            "academic_calendars",
            "content",
            "TEXT",
        )

        ensure_column(
            cursor,
            "academic_calendars",
            "created_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

        ensure_column(
            cursor,
            "academic_calendars",
            "updated_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        )

        cursor.execute("""
            UPDATE notices
            SET url = link
            WHERE
                (url IS NULL OR url = '')
                AND link IS NOT NULL
                AND link != ''
            """)

        cursor.execute("""
            UPDATE notices
            SET link = url
            WHERE
                (link IS NULL OR link = '')
                AND url IS NOT NULL
                AND url != ''
            """)

        cursor.execute("""
            UPDATE academic_calendars
            SET content_hash = ''
            WHERE content_hash IS NULL
            """)

        conn.commit()

    finally:
        conn.close()


def log_user_activity(
    telegram_id: int,
    first_name: str,
    username: Optional[str] = None,
):
    conn = get_connection()

    try:
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

    finally:
        conn.close()


def get_user(
    telegram_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        return cursor.fetchone()

    finally:
        conn.close()


def get_all_users():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT telegram_id
            FROM users
            WHERE telegram_id IS NOT NULL
            ORDER BY id ASC
            """)

        rows = cursor.fetchall()

        return [row["telegram_id"] for row in rows]

    finally:
        conn.close()


def get_user_count():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM users
            """)

        row = cursor.fetchone()

        return row["count"]

    finally:
        conn.close()


def get_setting(
    key: str,
    default: Any = None,
):
    conn = get_connection()

    try:
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

        if row is None:
            return default

        value = row["value"]

        try:
            number = float(value)

            if number.is_integer():
                return int(number)

            return number

        except (
            ValueError,
            TypeError,
        ):
            return value

    finally:
        conn.close()


def update_setting(
    key: str,
    value: Any,
):
    conn = get_connection()

    try:
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

    finally:
        conn.close()


def get_recent_notices(
    limit: int = 10,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                url,
                url AS link,
                published_date,
                created_at
            FROM notices
            ORDER BY
                datetime(created_at) DESC,
                id DESC
            LIMIT ?
            """,
            (limit,),
        )

        return cursor.fetchall()

    finally:
        conn.close()


def add_notice(
    title: str,
    description: str = "",
    url: str = "",
    published_date: str = "",
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM notices
            WHERE url = ?
            LIMIT 1
            """,
            (url,),
        )

        existing = cursor.fetchone()

        if existing:
            return existing["id"]

        cursor.execute(
            """
            INSERT INTO notices (
                title,
                description,
                url,
                link,
                published_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                url,
                url,
                published_date,
            ),
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def add_notice_if_new(
    title: str,
    link: str,
    published_date: str = "",
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM notices
            WHERE
                title = ?
                OR url = ?
                OR link = ?
            LIMIT 1
            """,
            (
                title,
                link,
                link,
            ),
        )

        if cursor.fetchone():
            return False

        cursor.execute(
            """
            INSERT INTO notices (
                title,
                url,
                link,
                published_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                link,
                link,
                published_date,
            ),
        )

        conn.commit()

        return True

    finally:
        conn.close()


def get_notice_by_url(
    url: str,
):
    conn = get_connection()

    try:
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

        return cursor.fetchone()

    finally:
        conn.close()


def get_notice(
    notice_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM notices
            WHERE id = ?
            """,
            (notice_id,),
        )

        return cursor.fetchone()

    finally:
        conn.close()


def delete_notice(
    notice_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM notices
            WHERE id = ?
            """,
            (notice_id,),
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


def get_notification_status(
    telegram_id: int,
):
    conn = get_connection()

    try:
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

            return True

        return bool(row["enabled"])

    finally:
        conn.close()


def set_notification_status(
    telegram_id: int,
    enabled: bool,
):
    conn = get_connection()

    try:
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

    finally:
        conn.close()


def toggle_notification(
    telegram_id: int,
):
    conn = get_connection()

    try:
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

        return bool(new_status)

    finally:
        conn.close()


def get_notification_users():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.telegram_id
            FROM users u
            LEFT JOIN notification_settings n
                ON u.telegram_id = n.telegram_id
            WHERE
                COALESCE(n.enabled, 1) = 1
                AND u.telegram_id IS NOT NULL
            ORDER BY u.id ASC
            """)

        rows = cursor.fetchall()

        return [row["telegram_id"] for row in rows]

    finally:
        conn.close()


def get_all_subscribers():
    return get_notification_users()


def get_calendar_by_url(
    url: str,
):
    conn = get_connection()

    try:
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

        return cursor.fetchone()

    finally:
        conn.close()


def get_calendar_by_id(
    calendar_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM academic_calendars
            WHERE id = ?
            """,
            (calendar_id,),
        )

        return cursor.fetchone()

    finally:
        conn.close()


def save_calendar(
    title: str,
    url: str,
    content_hash: str,
    content: str = "",
):
    conn = get_connection()

    try:
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

        return calendar_id

    finally:
        conn.close()


def get_calendars(
    limit: Optional[int] = None,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        if limit is not None:
            cursor.execute(
                """
                SELECT *
                FROM academic_calendars
                ORDER BY
                    datetime(updated_at) DESC,
                    id DESC
                LIMIT ?
                """,
                (limit,),
            )
        else:
            cursor.execute("""
                SELECT *
                FROM academic_calendars
                ORDER BY
                    datetime(updated_at) DESC,
                    id DESC
                """)

        return cursor.fetchall()

    finally:
        conn.close()


def get_latest_calendar():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM academic_calendars
            ORDER BY
                datetime(updated_at) DESC,
                id DESC
            LIMIT 1
            """)

        return cursor.fetchone()

    finally:
        conn.close()


def delete_calendar(
    calendar_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM academic_calendars
            WHERE id = ?
            """,
            (calendar_id,),
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()
