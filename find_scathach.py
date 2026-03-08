
import database

def find_scathach():
    print("Searching for 'スカサハ'...")
    results = database.search_servants("スカサハ")
    for r in results:
        print(f"ID: {r['id']} | Name: {r['name']} | Class: {r['class_name']}")

if __name__ == "__main__":
    find_scathach()
