import database
import json

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, name, json_data FROM servants WHERE name LIKE '%伊織%'")
rows = cursor.fetchall()
conn.close()

for r in rows:
    print(f"ID: {r['id']}, Name: {r['name']}")
    data = json.loads(r['json_data'])
    nps = data.get('noblePhantasms', [])
    for np in nps:
        print(f"NP ID: {np.get('id')}, Strength: {np.get('strengthStatus')}, Funcs:")
        for f in np.get('functions', []):
            print(f"  - Type: {f.get('funcType')}, Target: {f.get('funcTargetType')}")
