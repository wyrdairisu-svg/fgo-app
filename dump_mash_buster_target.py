import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

cur.execute('SELECT json_data FROM servants WHERE id=800100')
row = cur.fetchone()
data = json.loads(row[0])
np = data.get('noblePhantasms', [])[6] # Index 6
func = np['functions'][0]

print(f"NP Name: {np.get('name')}")
print(f"TargetType: {func.get('funcTargetType')}")
print(f"TargetTeam: {func.get('funcTargetTeam')}")

conn.close()
