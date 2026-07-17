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