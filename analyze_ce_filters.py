import sqlite3
import json

conn = sqlite3.connect("fgo_full_data_jp.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get a few samples:
# 1. Kaleidoscope (NP Charge) - usually early ID
# 2. Black Grail (Demerit)
# 3. Bond CE (Bond)
# 4. Event CE/EXP?
# We'll just grab a mix.

print("=== CE Samples ===")
cursor.execute("SELECT id, name, json_data FROM craft_essences LIMIT 5")
rows = cursor.fetchall()

def print_ce(row):
    print(f"\n--- {row['name']} (ID: {row['id']}) ---")
    try:
        data = json.loads(row['json_data'])
        # Print relevant keys
        print("Stats:", "HP:", data.get('hpMax'), "ATK:", data.get('atkMax'))
        print("Skills:", len(data.get('skills', [])))
        for s in data.get('skills', []):
            print(f"  Skill: {s.get('name')}")
            for f in s.get('functions', []):
                 print(f"    Func: {f.get('funcType')} Target: {f.get('funcTargetType')} Vals: {f.get('svals')}")
        print("Nice Traits:", [t.get('name') for t in data.get('traits', []) if t.get('name')])
    except:
        print("JSON parse error")

for r in rows:
    print_ce(r)

# Debug Kaleidoscope (ID: 9300034 usually, or search by name)
print("\n=== Debug Kaleidoscope ===")
cursor.execute("SELECT id, name, json_data FROM craft_essences WHERE name LIKE '%カレイドスコープ%' LIMIT 1")
row = cursor.fetchone()
if row:
    print(f"Found: {row['name']} (ID: {row['id']})")
    data = json.loads(row['json_data'])
    print("Skills:")
    for s in data.get('skills', []):
        for f in s.get('functions', []):
            if f.get('funcType') == 'gainNp':
                print(f"  Func: gainNp, svals: {f.get('svals')}")
else:
    print("Kaleidoscope not found in DB")
