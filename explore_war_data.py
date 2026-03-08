import sqlite3
import json

DB_PATH = "fgo_full_data_jp.db"

def explore_war_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get one record from wars
    c.execute("SELECT json_data FROM wars LIMIT 1")
    row = c.fetchone()
    if not row:
        print("No wars data found.")
        return

    war_data = json.loads(row[0])
    
    # Structure of War -> Spots -> Quests -> Drops
    print(f"War Name: {war_data.get('name')}")
    
    spots = war_data.get('spots', [])
    if not spots:
        print("No spots found.")
        return
        
    print(f"Found {len(spots)} spots. Checking first spot...")
    spot = spots[0]
    print(f"Spot Name: {spot.get('name')}")
    
    quests = spot.get('quests', [])
    if not quests:
        print("No quests found in first spot.")
        # Try finding a spot with quests
        for s in spots:
            if s.get('quests'):
                spot = s
                quests = s.get('quests')
                break
    
    if not quests:
        print("No quests found in any spot.")
        return

    print(f"checking quest: {quests[0].get('name')}")
    quest = quests[0]
    
    print(f"Quest Keys: {quest.keys()}")
    
    drops = quest.get('drops', [])
    print(f"Drops: {drops}")
    
    if drops:
        print("Drop structure sample:")
        print(json.dumps(drops[0], indent=2, ensure_ascii=False))
        
    # Check for free quests specifically
    print("-" * 20)
    print("Searching for a Free Quest...")
    found_free = False
    
    # Need to iterate wars/spots to find a free quest
    # But for now just check if this war has any
    
    c.execute("SELECT json_data FROM wars")
    rows = c.fetchall()
    
    found_drops = False
    for r in rows:
        w_data = json.loads(r[0])
        for s in w_data.get('spots', []):
            for q in s.get('quests', []):
                # Search for ANY key resembling drops
                if 'drops' in q:
                    print(f"FOUND 'drops' key! War: {w_data.get('name')}, Quest: {q.get('name')}")
                    print(f"Data: {q['drops'][:1]}")
                    found_drops = True
                    break
            if found_drops: break
        if found_drops: break
        
    if not found_drops:
        print("NO 'drops' KEY FOUND in any quest in wars table.")

if __name__ == "__main__":
    explore_war_data()
