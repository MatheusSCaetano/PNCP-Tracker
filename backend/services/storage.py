import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database.db"

def get_conn():
    """Cria uma conexão nova por thread (check_same_thread=False é seguro com este padrão)."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS licitacoes (
            id TEXT PRIMARY KEY,
            description TEXT
        )
    """)
    conn.commit()
    return conn

def exists(id):
    conn = get_conn()
    try:
        cur = conn.execute("SELECT 1 FROM licitacoes WHERE id=?", (id,))
        return cur.fetchone() is not None
    finally:
        conn.close()

def save(item):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO licitacoes (id, description) VALUES (?, ?)",
            (item["id"], item["description"])
        )
        conn.commit()
    finally:
        conn.close()