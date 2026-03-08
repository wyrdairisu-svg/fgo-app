import database
import sqlite3

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, name, class_name FROM servants WHERE class_name LIKE '%beast%' OR class_name LIKE '%unknown%' OR class_name LIKE '%foreign%' OR name LIKE '%オルガ%' OR name LIKE '%エレシュ%'")
rows = cursor.fetchall()
conn.close()

with open("survey.log", "w", encoding="utf-8") as f:
    f.write(f"Found {len(rows)} candidates:\n")
    for r in rows:
        f.write(f"ID: {r['id']} | Name: {r['name']} | Class: {r['class_name']}\n")
