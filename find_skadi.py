
import database

def find_skadi():
    print("Searching for 'スカディ'...")
    results = database.search_servants("スカディ")
    for r in results:
        print(f"ID: {r['id']} | Name: {r['name']} | Class: {r['class_name']}")

if __name__ == "__main__":
    find_skadi()
