import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

ids_to_check = [463, 464]
cur.execute(f'SELECT id, collection_no, name, json_data FROM servants WHERE collection_no IN ({",".join(map(str, ids_to_check))})')
rows = cur.fetchall()

print(f"Found {len(rows)} rows total.")

for r in rows:
    sid = r[0]
    cno = r[1]
    name = r[2]
    data = json.loads(r[3])
    
    stype = data.get('type')
    flag = data.get('flag')
    
    # Check identifying fields
    print(f"ID: {sid:<8} | No: {cno:<4} | Name: {name:<12} | Type: {stype} | Flag: {flag}")

conn.close()
