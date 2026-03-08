
import database

def check_name(name):
    print(f"Searching for: {name}")
    results = database.search_servants(name, limit=5)
    for r in results:
        print(f"Found: {r['name']} (Class: {r['class_name']}, ID: {r['id']})")

check_name("コヤンスカヤ")
check_name("オベロン")
check_name("アルトリア・キャスター")
check_name("スカディ")
