import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

print("--- Mash Search ---")
cur.execute('SELECT id, collection_no, name, class_name, json_data FROM servants WHERE name LIKE "%マシュ%" OR name LIKE "%Mash%"')
rows = cur.fetchall()

for r in rows:
    sid = r[0]
    cno = r[1]
    name = r[2]
    cls = r[3]
    try:
        data = json.loads(r[4])
        battle_name = data.get('battleName', '')
    except:
        battle_name = 'error'
        
    print(f"ID: {sid} No: {cno} Name: {name} Class: {cls} BattleName: {battle_name}")

conn.close()
