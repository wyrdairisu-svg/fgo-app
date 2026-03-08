import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

# Find a servant likely to have Quick NP (e.g. name contains "沖田" or "Jack" or just search for one)
# Okita Souji = 沖田総司
cur.execute("SELECT id, name, json_data FROM servants WHERE name LIKE '%沖田%' LIMIT 1")
row = cur.fetchone()

if row:
    print(f"Found: {row[1]} (ID: {row[0]})")
    data = json.loads(row[2])
    if "noblePhantasms" in data and len(data["noblePhantasms"]) > 0:
        np = data["noblePhantasms"][0]
        raw_card = np.get("card")
        print(f"Raw Card Value: {repr(raw_card)} (Type: {type(raw_card)})")
        
        # Logic from database.py
        if isinstance(raw_card, int):
            card_map = {1: "Arts", 2: "Buster", 3: "Quick"}
            np_card = card_map.get(raw_card, "Unknown")
        else:
            np_card = str(raw_card).capitalize() if raw_card else "Unknown"
            
        print(f"Mapped NP Card: '{np_card}'")
        
        # Test Filter
        req_cards = ['Quick']
        if np_card not in req_cards:
            print(f"FAIL: '{np_card}' not in {req_cards}")
        else:
            print("PASS: Filter match")
    else:
        print("No NP data found")
else:
    print("Okita not found, trying generic search for Quick")
    # Search for any servant with card=quick (if string) or card=3 (if int)
    # This is hard to do in SQL if JSON.
    pass

conn.close()
