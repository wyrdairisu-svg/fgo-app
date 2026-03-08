import sqlite3
import json

conn = sqlite3.connect("fgo_full_data_jp.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name, json_data FROM craft_essences WHERE name='カレイドスコープ'")
row = cursor.fetchone()

if row:
    print(f"Name: {row['name']}")
    data = json.loads(row['json_data'])
    for s in data.get('skills', []):
        for f in s.get('functions', []):
            if f.get('funcType') == 'gainNp':
                print(f"Functions: {f}")
                for sv in f.get('svals', []):
                    print(f"Value: {sv.get('Value')}")
else:
    print("Not Found")
