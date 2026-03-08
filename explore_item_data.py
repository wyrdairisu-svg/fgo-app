import sqlite3
import json

DB_PATH = "fgo_full_data_jp.db"

def explore_item_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get one record from items
    # Try to find a common material, e.g., "Dragon Fang" or generic name query if possible, 
    # but let's just grab a few
    c.execute("SELECT name, json_data FROM items LIMIT 5")
    rows = c.fetchall()
    
    if not rows:
        print("No item data found.")
        return

    for row in rows:
        name = row[0]
        data = json.loads(row[1])
        print(f"Item: {name}")
        print(f"Keys: {list(data.keys())}")
        
        # Check for 'drops' or 'quests'
        if 'drops' in data:
            print(f"Has 'drops': {data['drops']}")
        if 'quests' in data:
            print(f"Has 'quests': {len(data['quests'])}")
            print("Sample quest:", data['quests'][0])
            
        # Check 'usage' or 'held'
        print("-" * 20)

if __name__ == "__main__":
    explore_item_data()
