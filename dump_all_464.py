import sqlite3
import json

conn = sqlite3.connect('fgo_full_data_jp.db')
cur = conn.cursor()

# Check int 464
print("--- Int 464 ---")
cur.execute('SELECT id, name FROM servants WHERE collection_no = 464')
for r in cur.fetchall():
    print(r)

# Check string '464'
print("--- Str '464' ---")
cur.execute('SELECT id, name FROM servants WHERE collection_no = "464"')
for r in cur.fetchall():
    print(r)

# Check via CAST
print("--- Cast 464 ---")
cur.execute('SELECT id, name FROM servants WHERE CAST(collection_no as INTEGER) = 464')
for r in cur.fetchall():
    print(r)

conn.close()
