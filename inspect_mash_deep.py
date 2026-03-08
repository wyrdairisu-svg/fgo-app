import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

ids = [800100, 800101]
for i in ids:
    cur.execute('SELECT id, collection_no, name, json_data FROM servants WHERE id=?', (i,))
    row = cur.fetchone()
    if row:
        print(f"--- ID {i} ---")
        print(f"Collection No: {row[1]}")
        data = json.loads(row[3])
        nps = data.get('noblePhantasms', [])
        print(f"NP Count: {len(nps)}")
        for np in nps:
             print(f"  NP: {np.get('name')} (Card: {np.get('card')})")
        
        skills = data.get('skills', [])
        print(f"Skill Count: {len(skills)}")
    else:
        print(f"ID {i} NOT FOUND")

conn.close()
