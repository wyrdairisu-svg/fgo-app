import sqlite3
import json

conn = sqlite3.connect("fgo_full_data_jp.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name, json_data FROM craft_essences WHERE name='龍脈'")
row = cursor.fetchone()

if row:
    print(f"Name: {row['name']}")
    data = json.loads(row['json_data'])
    for s in data.get('skills', []):
        print(f"Skill: {s.get('name')}")
        for f in s.get('functions', []):
            if f.get('funcType') == 'gainNp':
                print(f"  Func: gainNp")
                for sv in f.get('svals', []):
                    print(f"    sval: {sv}")
else:
    print("Not Found")
