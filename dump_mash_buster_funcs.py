import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

cur.execute('SELECT json_data FROM servants WHERE id=800100')
row = cur.fetchone()
data = json.loads(row[0])
np = data.get('noblePhantasms', [])[6] # Index 6

print(f"NP Name: {np.get('name')}")
for i, func in enumerate(np.get('functions', [])):
    print(f"Func {i}: {func.get('funcType')} | TargetType: {func.get('funcTargetType')} | Team: {func.get('funcTargetTeam')}")

conn.close()
