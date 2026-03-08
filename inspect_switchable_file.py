import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

with open('debug_switchable.log', 'w', encoding='utf-8') as f:
    # Search for Melusine (メリュジーヌ)
    f.write("--- Melusine ---\n")
    cur.execute('SELECT id, name, json_data FROM servants WHERE name LIKE "%メリュジーヌ%"')
    rows = cur.fetchall()
    for r in rows:
        data = json.loads(r[2])
        nps = data.get('noblePhantasms', [])
        f.write(f"ID: {r[0]} Name: {r[1]} NP Count: {len(nps)}\n")
        for i, np in enumerate(nps):
            func0 = np['functions'][0] if np['functions'] else {}
            f.write(f"  NP {i}: Card={np.get('card')} TargetType={func0.get('funcTargetType')}\n")

    # Search for Ptolemy (プトレマイオス)
    f.write("\n--- Ptolemy ---\n")
    cur.execute('SELECT id, name, json_data FROM servants WHERE name LIKE "%プトレマイオス%"')
    rows = cur.fetchall()
    for r in rows:
        data = json.loads(r[2])
        nps = data.get('noblePhantasms', [])
        f.write(f"ID: {r[0]} Name: {r[1]} NP Count: {len(nps)}\n")
        for i, np in enumerate(nps):
            func0 = np['functions'][0] if np['functions'] else {}
            f.write(f"  NP {i}: Card={np.get('card')} TargetType={func0.get('funcTargetType')}\n")

conn.close()
