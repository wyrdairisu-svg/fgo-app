import sqlite3
import json

conn = sqlite3.connect('fgo_full_data_jp.db')
cur = conn.cursor()

# Search by name loosely to catch everything
cur.execute('SELECT id, collection_no, name FROM servants WHERE name LIKE "%フローラ%"')
rows = cur.fetchall()

with open('dump.txt', 'w', encoding='utf-8') as f:
    f.write(f"Count: {len(rows)}\n")
    for r in rows:
        sid = r[0]
        cno = r[1]
        name = r[2]
        f.write(f"ID: {sid} (Type: {type(sid)})\n")
        f.write(f"No: {cno} (Type: {type(cno)})\n")
        f.write(f"Name: {name}\n")
        f.write("-" * 20 + "\n")

conn.close()
