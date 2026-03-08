import database
conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, name, collection_no, class_name FROM servants WHERE id IN (3300200, 4000100)")
rows = cursor.fetchall()
conn.close()
for r in rows:
    print(f"ID: {r['id']}, Name: {r['name']}, No: {r['collection_no']}, Class: {r['class_name']}")
