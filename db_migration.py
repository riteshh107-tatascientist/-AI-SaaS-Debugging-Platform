import sqlite3

DB_NAME = "users.db"

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_migration():
    conn = get_conn()
    c = conn.cursor()

    # create table safely
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password BLOB,
            is_banned INTEGER DEFAULT 0
        )
    """)

    # check columns
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]

    # add is_banned if missing
    if "is_banned" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")

    # ⚠️ FIX: created_at WITHOUT DEFAULT (IMPORTANT)
    if "created_at" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN created_at TEXT")

    conn.commit()
    conn.close()