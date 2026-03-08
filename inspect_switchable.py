import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

# Search for Melusine (メリュジーヌ)
print("--- Melusine ---")
cur.execute('SELECT id, name, json_data FROM servants WHERE name LIKE "%メリュジーヌ%"')
rows = cur.fetchall()
for r in rows:
    data = json.loads(r[2])
    nps = data.get('noblePhantasms', [])
    print(f"ID: {r[0]} Name: {r[1]} NP Count: {len(nps)}")
    for i, np in enumerate(nps):
        func0 = np['functions'][0] if np['functions'] else {}
        print(f"  NP {i}: Card={np.get('card')} TargetType={func0.get('funcTargetType')}")

# Search for Ptolemy (プトレマイオス)
print("\n--- Ptolemy ---")
cur.execute('SELECT id, name, json_data FROM servants WHERE name LIKE "%プトレマイオス%"')
rows = cur.fetchall()
for r in rows:
    data = json.loads(r[2])
    nps = data.get('noblePhantasms', [])
    print(f"ID: {r[0]} Name: {r[1]} NP Count: {len(nps)}")
    for i, np in enumerate(nps):
        func0 = np['functions'][0] if np['functions'] else {}
        print(f"  NP {i}: Card={np.get('card')} TargetType={func0.get('funcTargetType')}")

conn.close()
