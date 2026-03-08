import database
import json

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, collection_no, name, class_name, rarity, json_data FROM servants WHERE name LIKE '%アニムスフィア%' OR name LIKE '%マリス%'")

rows = cursor.fetchall()

if not rows:
    print("No matches found.")
else:
    for r in rows:
        print(f"ID: {r['id']}")
        print(f"Name: {r['name']}")
        print(f"Class: {r['class_name']}")
        print(f"Rarity: {r['rarity']}")
        data = json.loads(r['json_data']) if r['json_data'] else {}
        print(f"Type: {data.get('type')}")
        print("-" * 20)

conn.close()
