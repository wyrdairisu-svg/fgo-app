import sqlite3
import json

DB_PATH = "fgo_full_data_jp.db"

def diagnose_drop_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Check total count in quest_drops
    cursor.execute("SELECT count(*) FROM quest_drops")
    count = cursor.fetchone()[0]
    print(f"Total rows in quest_drops: {count}")
    
    if count == 0:
        print("CRITICAL: quest_drops table is empty!")
    
    # 2. Check for World Tree Seed (ID 6502)
    ITEM_ID = 6502
    cursor.execute("SELECT * FROM quest_drops WHERE item_id = ?", (ITEM_ID,))
    rows = cursor.fetchall()
    print(f"Drops for Item {ITEM_ID}: {len(rows)} found.")
    for r in rows:
        print(r)
        
    # 3. Check raw war data for this item if not found
    if len(rows) == 0:
        print("Searching raw war data for this item...")
        cursor.execute("SELECT json_data FROM wars")
        war_rows = cursor.fetchall()
        
        found_raw = False
        for r in war_rows:
            if not r[0]: continue
            war = json.loads(r[0])
            for spot in war.get('spots', []):
                for quest in spot.get('quests', []):
                    if quest.get('type') == 'free':
                        drops = quest.get('drops', [])
                        for drop in drops:
                            if drop.get('type') == 'item' and drop.get('objectId') == ITEM_ID:
                                print(f"Found in Raw Data! War: {war.get('name')}, Quest: {quest.get('name')}")
                                found_raw = True
                                # usage break not needed strictly, but to avoid spam
            if found_raw: break

    conn.close()

if __name__ == "__main__":
    diagnose_drop_data()
