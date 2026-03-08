
import database

def find_koyan():
    print("Searching for 'コヤンスカヤ'...")
    results = database.search_servants("光のコヤンスカヤ")
    if not results:
         print("Not found '光のコヤンスカヤ', trying 'コヤンスカヤ'")
         results = database.search_servants("コヤンスカヤ")
    
    for r in results:
        print(f"ID: {r['id']} | Name: {r['name']} | Class: {r['class_name']}")

if __name__ == "__main__":
    find_koyan()
