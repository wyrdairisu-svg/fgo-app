import sqlite3
import json

db_path = 'fgo_full_data_jp.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row['name'] for row in cur.fetchall()]
print(f"Tables found: {tables}")

# Check Servants count
if 'servants' in tables:
    cnt = cur.execute("SELECT count(*) FROM servants").fetchone()[0]
    print(f"\nServants count: {cnt}")

# Check for others
expected = {
    'Craft Essences': ['craft_essences', 'ces', 'mstSvt'], # mstSvt sometimes contains CEs in raw data
    'Command Codes': ['command_codes', 'ccs', 'mstCommandCode'],
    'Materials': ['items', 'materials', 'mstItem']
}

for label, candidates in expected.items():
    found = None
    for c in candidates:
        if c in tables:
            found = c
            break
    
    if found:
        print(f"\n[{label} found in '{found}']")
        try:
            cur.execute(f"SELECT * FROM {found} LIMIT 1")
            row = cur.fetchone()
            if row:
                print(f"  Columns: {list(row.keys())}")
                # print first few cols
                keys = list(row.keys())
                sample = {k: row[k] for k in keys[:5]} 
                print(f"  Sample (partial): {sample}")
        except Exception as e:
            print(f"  Error reading table: {e}")
    else:
        print(f"\n[MISSING] No table found for {label}")

conn.close()
