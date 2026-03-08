import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

sid = 400400
cur.execute('SELECT json_data FROM servants WHERE id=?', (sid,))
row = cur.fetchone()
data = json.loads(row[0])
np = data['noblePhantasms'][0]
func1 = np['functions'][1]

print(f"Func 1 Type: '{func1.get('funcType')}'")
print(f"Func 1 Target: '{func1.get('funcTargetTeam')}'")

try:
    func2 = np['functions'][2]
    print(f"Func 2 Type: '{func2.get('funcType')}'")
    print(f"Func 2 Target: '{func2.get('funcTargetTeam')}'")
except:
    pass

conn.close()
