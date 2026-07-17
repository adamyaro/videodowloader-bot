import os
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")

pool = None


async def connect_db():
    global pool

    pool = await asyncpg.create_pool(DATABASE_URL)

    await pool.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username TEXT,
            first_name TEXT,
            joined_at TIMESTAMP DEFAULT NOW()
        );
    """)

    await pool.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id SERIAL PRIMARY KEY,
            platform TEXT
        );
    """)


async def add_user(telegram_id, username, first_name):
    await pool.execute(
        """
        INSERT INTO users (telegram_id, username, first_name)
        VALUES ($1, $2, $3)
        ON CONFLICT (telegram_id) DO NOTHING;
        """,
        telegram_id,
        username,
        first_name,
    )


async def add_download(platform):
    await pool.execute(
        """
        INSERT INTO downloads (platform)
        VALUES ($1);
        """,
        platform,
    )


async def get_stats():
    users = await pool.fetchval(
        "SELECT COUNT(*) FROM users;"
    )

    total = await pool.fetchval(
        "SELECT COUNT(*) FROM downloads;"
    )

    tiktok = await pool.fetchval(
        "SELECT COUNT(*) FROM downloads WHERE platform='TikTok';"
    )

    youtube = await pool.fetchval(
        "SELECT COUNT(*) FROM downloads WHERE platform='YouTube';"
    )

    instagram = await pool.fetchval(
        "SELECT COUNT(*) FROM downloads WHERE platform='Instagram';"
    )

    return {
        "users": users,
        "total": total,
        "tiktok": tiktok,
        "youtube": youtube,
        "instagram": instagram,
    }