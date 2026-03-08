import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

cur.execute('SELECT json_data FROM servants WHERE id=800100')
row = cur.fetchone()
data = json.loads(row[0])
nps = data.get('noblePhantasms', [])

for i, np in enumerate(nps):
    card = np.get('card')
    name = np.get('name')
    if str(card) == '2':
         print(f"FOUND BUSTER NP [{i}]: {name}")
    else:
         print(f"NP [{i}] is {card}")

conn.close()
