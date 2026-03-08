import database
import json

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, name, json_data FROM servants WHERE id = 106000")
rows = cursor.fetchall()
conn.close()

if rows:
    data = json.loads(rows[0]['json_data'])
    for np in data.get('noblePhantasms', []):
        print(f"NP Name: {np.get('name')}")
        print(f"Detail: {np.get('detail')}")
