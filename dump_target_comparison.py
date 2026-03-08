import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

targets = [
    (100100, "Artoria (AoE)"),
    (400400, "Cu (ST)")
]

for sid, name in targets:
    cur.execute('SELECT json_data FROM servants WHERE id=?', (sid,))
    row = cur.fetchone()
    if row:
        data = json.loads(row[0])
        np = data['noblePhantasms'][0]
        func = np['functions'][0] # Check first func (damage)
        
        print(f"--- {name} ---")
        print(f"Type: {func.get('funcType')}")
        print(f"TargetType: {func.get('funcTargetType')}")
        print(f"TargetTeam: {func.get('funcTargetTeam')}")

conn.close()
