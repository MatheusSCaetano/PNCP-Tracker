import sqlite3

import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS licitacoes (
    id TEXT PRIMARY KEY,
    description TEXT
)
""")

conn.commit()

def exists(id):
    cursor.execute("SELECT 1 FROM licitacoes WHERE id=?",(id,))
    return cursor.fetchone() is not None

def save(item):
    cursor.execute(
        "INSERT INTO licitacoes (id, description) VALUES(?, ?)",
        (item["id"], item["description"])
    )
    conn.commit()

