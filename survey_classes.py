import database
import sqlite3

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, name, class_name FROM servants WHERE class_name LIKE '%beast%' OR class_name LIKE '%unknown%' OR class_name LIKE '%foreign%' OR name LIKE '%オルガ%' OR name LIKE '%エレシュ%'")
rows = cursor.fetchall()
conn.close()

print(f"Found {len(rows)} candidates:")
for r in rows:
    print(f"ID: {r['id']} | Name: {r['name']} | Class: {r['class_name']}")
