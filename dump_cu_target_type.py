import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

sid = 400400 # Cu
cur.execute('SELECT json_data FROM servants WHERE id=?', (sid,))
row = cur.fetchone()
if row:
    data = json.loads(row[0])
    np = data['noblePhantasms'][0]
    func = np['functions'][0]
    
    print(f"Cu Func 0 TargetType: '{func.get('funcTargetType')}'")
    print(f"Cu Func 0 TargetTeam: '{func.get('funcTargetTeam')}'")

conn.close()
