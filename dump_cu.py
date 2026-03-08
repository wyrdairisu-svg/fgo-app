import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

# Cu Chulainn (ST)
cur.execute('SELECT json_data FROM servants WHERE id=400400')
row = cur.fetchone()
if row:
    data = json.loads(row[0])
    np = data['noblePhantasms'][0]
    funcs = np['functions']
    print(f"NP Card: {np.get('card')}")
    for i, func in enumerate(funcs):
        print(f"Func {i}: Type='{func.get('funcType')}' Target='{func.get('funcTargetTeam')}'")

conn.close()
