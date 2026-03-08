import database
import json

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, name, json_data FROM servants WHERE id = 106000") # Assuming ID from previous output
rows = cursor.fetchall()
conn.close()

if rows:
    r = rows[0]
    data = json.loads(r['json_data'])
    print(json.dumps(data.get('noblePhantasms'), indent=2, ensure_ascii=False))
