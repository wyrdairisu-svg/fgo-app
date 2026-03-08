import sqlite3
import json

conn = sqlite3.connect('fgo_full_data_jp.db')
cur = conn.cursor()

ids_to_check = [463, 464]
cur.execute(f'SELECT id, collection_no, name, class_name, json_data FROM servants WHERE collection_no IN ({",".join(map(str, ids_to_check))})')
rows = cur.fetchall()

print(f"Total rows: {len(rows)}")

for r in rows:
    sid = r[0]
    cno = r[1]
    name = r[2]
    cls = r[3]
    try:
        data = json.loads(r[4])
        stype = data.get('type')
    except:
        stype = "error"
        
    print(f"ID:{sid} No:{cno} {name} ({cls}) Type:{stype}")

conn.close()
