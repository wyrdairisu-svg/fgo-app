import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

print("--- Scan Shielders ---")
cur.execute('SELECT id, collection_no, name, class_name FROM servants WHERE class_name LIKE "%shielder%" OR class_name = "shielder"')
rows = cur.fetchall()

for r in rows:
    print(r)

conn.close()
