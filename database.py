import logging
import os
from typing import Any, Optional

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def get_connection():
    host = os.getenv("TIDB_HOST")
    port = os.getenv("TIDB_PORT", "4000")
    user = os.getenv("TIDB_USER")
    password = os.getenv("TIDB_PASSWORD")
    database = os.getenv("TIDB_DATABASE", "sys")

    if not host:
        raise RuntimeError("TIDB_HOST is not configured.")

    if not user:
        raise RuntimeError("TIDB_USER is not configured.")

    if not password:
        raise RuntimeError("TIDB_PASSWORD is not configured.")

    return mysql.connector.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        ssl_disabled=False,
        ssl_verify_cert=False,
        ssl_verify_identity=False,
        connection_timeout=30,
        autocommit=False,
    )


def init_db():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                first_name VARCHAR(255),
                username VARCHAR(255),
                notifications_enabled TINYINT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                `key` VARCHAR(255) PRIMARY KEY,
                `value` TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
            )
            """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notices (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                url TEXT,
                link TEXT,
                published_date VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS academic_calendars (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                url VARCHAR(2048) NOT NULL,
                content_hash VARCHAR(128) NOT NULL,
                content LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_calendar_url (url(768))
            )
            """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_settings (
                telegram_id BIGINT PRIMARY KEY,
                enabled TINYINT DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
            )
            """)

        conn.commit()

        logger.info("TiDB tables initialized successfully.")

    except Exception:
        conn.rollback()
        logger.exception("Failed to initialize TiDB.")
        raise

    finally:
        cursor.close()
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
                username,
                last_active
            )
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE
                first_name = VALUES(first_name),
                username = VALUES(username),
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
            INSERT IGNORE INTO notification_settings (
                telegram_id,
                enabled
            )
            VALUES (%s, 1)
            """,
            (telegram_id,),
        )

        conn.commit()

    finally:
        cursor.close()
        conn.close()


def get_user(
    telegram_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE telegram_id = %s
            """,
            (telegram_id,),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def get_all_users():
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT telegram_id
            FROM users
            WHERE telegram_id IS NOT NULL
            ORDER BY id ASC
            """)

        return [row["telegram_id"] for row in cursor.fetchall()]

    finally:
        cursor.close()
        conn.close()


def get_user_count():
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM users
            """)

        row = cursor.fetchone()

        return row["count"]

    finally:
        cursor.close()
        conn.close()


def get_setting(
    key: str,
    default: Any = None,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT `value`
            FROM settings
            WHERE `key` = %s
            """,
            (key,),
        )

        row = cursor.fetchone()

        if not row:
            return default

        value = row["value"]

        if value is None:
            return default

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
        cursor.close()
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
                `key`,
                `value`
            )
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                `value` = VALUES(`value`),
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                key,
                str(value),
            ),
        )

        conn.commit()

    finally:
        cursor.close()
        conn.close()


def get_recent_notices(
    limit: int = 10,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                url,
                link,
                published_date,
                created_at
            FROM notices
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (int(limit),),
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def add_notice(
    title: str,
    description: str = "",
    url: str = "",
    published_date: str = "",
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id
            FROM notices
            WHERE url = %s
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
            VALUES (%s, %s, %s, %s, %s)
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
        cursor.close()
        conn.close()


def add_notice_if_new(
    title: str,
    link: str,
    published_date: str = "",
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id
            FROM notices
            WHERE
                title = %s
                OR url = %s
                OR link = %s
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
            VALUES (%s, %s, %s, %s)
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
        cursor.close()
        conn.close()


def get_notice_by_url(
    url: str,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM notices
            WHERE url = %s
            LIMIT 1
            """,
            (url,),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def get_notice(
    notice_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM notices
            WHERE id = %s
            """,
            (notice_id,),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
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
            WHERE id = %s
            """,
            (notice_id,),
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        cursor.close()
        conn.close()


def get_notification_status(
    telegram_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT enabled
            FROM notification_settings
            WHERE telegram_id = %s
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
                VALUES (%s, 1)
                """,
                (telegram_id,),
            )

            conn.commit()

            return True

        return bool(row["enabled"])

    finally:
        cursor.close()
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
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                enabled = VALUES(enabled),
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                telegram_id,
                1 if enabled else 0,
            ),
        )

        conn.commit()

    finally:
        cursor.close()
        conn.close()


def toggle_notification(
    telegram_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT enabled
            FROM notification_settings
            WHERE telegram_id = %s
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
                VALUES (%s, %s)
                """,
                (
                    telegram_id,
                    new_status,
                ),
            )

        else:
            new_status = 0 if bool(row["enabled"]) else 1

            cursor.execute(
                """
                UPDATE notification_settings
                SET
                    enabled = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE telegram_id = %s
                """,
                (
                    new_status,
                    telegram_id,
                ),
            )

        conn.commit()

        return bool(new_status)

    finally:
        cursor.close()
        conn.close()


def get_notification_users():
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT u.telegram_id
            FROM users u
            LEFT JOIN notification_settings n
                ON u.telegram_id = n.telegram_id
            WHERE
                u.telegram_id IS NOT NULL
                AND COALESCE(n.enabled, 1) = 1
            ORDER BY u.id ASC
            """)

        return [row["telegram_id"] for row in cursor.fetchall()]

    finally:
        cursor.close()
        conn.close()


def get_all_subscribers():
    return get_notification_users()


def get_calendar_by_url(
    url: str,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM academic_calendars
            WHERE url = %s
            LIMIT 1
            """,
            (url,),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def get_calendar_by_id(
    calendar_id: int,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM academic_calendars
            WHERE id = %s
            """,
            (calendar_id,),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def save_calendar(
    title: str,
    url: str,
    content_hash: str,
    content: str = "",
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id
            FROM academic_calendars
            WHERE url = %s
            LIMIT 1
            """,
            (url,),
        )

        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE academic_calendars
                SET
                    title = %s,
                    content_hash = %s,
                    content = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    title,
                    content_hash,
                    content,
                    existing["id"],
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
                VALUES (%s, %s, %s, %s)
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
        cursor.close()
        conn.close()


def get_calendars(
    limit: Optional[int] = None,
):
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        if limit is None:
            cursor.execute("""
                SELECT *
                FROM academic_calendars
                ORDER BY updated_at DESC, id DESC
                """)
        else:
            cursor.execute(
                """
                SELECT *
                FROM academic_calendars
                ORDER BY updated_at DESC, id DESC
                LIMIT %s
                """,
                (int(limit),),
            )

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def get_latest_calendar():
    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM academic_calendars
            ORDER BY updated_at DESC, id DESC
            LIMIT 1
            """)

        return cursor.fetchone()

    finally:
        cursor.close()
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
            WHERE id = %s
            """,
            (calendar_id,),
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        cursor.close()
        conn.close()
