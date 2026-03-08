import sqlite3
import json

conn = sqlite3.connect('fgo_full_data_jp.db')
cur = conn.cursor()

names = ['フローラ', '蛇女房']
for name in names:
    print(f"--- Checking {name} ---")
    cur.execute('SELECT id, collection_no, name, class_name, json_data FROM servants WHERE name LIKE ?', (f'%{name}%',))
    rows = cur.fetchall()
    
    for r in rows:
        sid = r[0]
        cno = r[1]
        cno_type = type(cno)
        nameval = r[2]
        try:
            data = json.loads(r[4])
            stype = data.get('type')
        except:
            stype = "err"
            
        print(f"ID:{sid} No:{cno} ({cno_type}) Name:{nameval} Type:{stype}")

conn.close()
