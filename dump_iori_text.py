import database
import json

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT json_data FROM servants WHERE id = 106000")
data = json.loads(cursor.fetchone()[0])
conn.close()

with open('iori_text.txt', 'w', encoding='utf-8') as f:
    for np in data.get('noblePhantasms', []):
        f.write(f"NP: {np.get('name')}\n")
        f.write(f"Detail: {np.get('detail')}\n\n")
