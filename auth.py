import sqlite3
import bcrypt
from datetime import datetime
import streamlit as st   # ✅ ADD

# ---------------- DATABASE ----------------
def connect():
    return sqlite3.connect("users.db", check_same_thread=False)


# ---------------- INIT TABLE ----------------
def create_table():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password BLOB,
        is_banned INTEGER DEFAULT 0,
        is_deleted INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS activity(
        username TEXT,
        action TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- SIGNUP ----------------
def signup(u, p):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT username FROM users WHERE username=?", (u,))
    if c.fetchone():
        conn.close()
        return False

    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("""
        INSERT INTO users (username, password, is_banned, is_deleted, created_at)
        VALUES (?, ?, 0, 0, ?)
    """, (u, hashed, created_at))

    conn.commit()
    conn.close()
    log_activity(u, "SIGNUP")
    return True


# ---------------- LOGIN ----------------
def login(u, p):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT password, is_banned, is_deleted FROM users WHERE username=?", (u,))
    data = c.fetchone()

    if not data:
        conn.close()
        return False

    hashed, banned, deleted = data

    if deleted == 1:
        return "DELETED"

    if banned == 1:
        return "BANNED"

    if bcrypt.checkpw(p.encode(), hashed):
        log_activity(u, "LOGIN SUCCESS")
        return True

    return False


# ---------------- ACTIVITY ----------------
def log_activity(user, action):
    conn = connect()
    c = conn.cursor()

    c.execute(
        "INSERT INTO activity VALUES (?, ?, ?)",
        (user, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()
    conn.close()


def get_activity():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM activity ORDER BY time DESC")
    data = c.fetchall()
    conn.close()
    return data


# ---------------- ADMIN ----------------
def get_all_users():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT username, is_banned, is_deleted, created_at FROM users")
    data = c.fetchall()
    conn.close()
    return data


def ban_user(username):
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()


def unban_user(username):
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE username=?", (username,))
    conn.commit()
    conn.close()


# ---------------- SOFT DELETE ----------------
def delete_user(username):
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE users SET is_deleted=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()
    log_activity(username, "USER DELETED")


# ---------------- RESTORE USER ----------------
def restore_user(username):
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE users SET is_deleted=0 WHERE username=?", (username,))
    conn.commit()
    conn.close()
    log_activity(username, "USER RESTORED")


# ================== 🔐 SECURE ADMIN (NEW) ==================
def ensure_admin():
    conn = connect()
    c = conn.cursor()

    admin_user = st.secrets["ADMIN_USERNAME"]
    admin_pass = st.secrets["ADMIN_PASSWORD"]

    c.execute("SELECT username FROM users WHERE username=?", (admin_user,))
    if not c.fetchone():

        hashed = bcrypt.hashpw(admin_pass.encode(), bcrypt.gensalt())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
            INSERT INTO users (username, password, is_banned, is_deleted, created_at)
            VALUES (?, ?, 0, 0, ?)
        """, (admin_user, hashed, now))

    conn.commit()
    conn.close()