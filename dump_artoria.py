import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

# Artoria (AoE)
cur.execute('SELECT json_data FROM servants WHERE id=100100')
row = cur.fetchone()
if row:
    data = json.loads(row[0])
    np = data['noblePhantasms'][0]
    func = np['functions'][0]
    print(f"Target: '{func.get('funcTargetTeam')}'")
    print(f"FuncType: '{func.get('funcType')}'")

conn.close()
