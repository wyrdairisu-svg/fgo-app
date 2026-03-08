import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

# 1. Check Class Names in DB
cur.execute("SELECT DISTINCT class_name FROM servants")
classes = [r[0] for r in cur.fetchall()]
print("DB Classes:", classes)

# 2. Check Artoria (ID 100100) Data
cur.execute("SELECT name, class_name, json_data FROM servants WHERE id=100100")
row = cur.fetchone()
if row:
    data = json.loads(row[2])
    np = data['noblePhantasms'][0]
    print(f"\nArtoria JSON Card: {np.get('card')} (Type: {type(np.get('card'))})")
    
    # Simulate Filter Logic
    filters = ['Buster']
    # filters = ['セイバー'] 
    
    req_cards = ['Buster'] # Simplified
    
    card_map = {1: "Arts", 2: "Buster", 3: "Quick"}
    np_card = card_map.get(np.get("card"), "Unknown")
    print(f"Mapped NP Card: {np_card}")
    
    keep = True
    if req_cards and np_card not in req_cards:
        keep = False
        print(f"Filtered OUT by Card (Expected {req_cards}, Got {np_card})")
    else:
        print("Kept by Card Filter")

conn.close()
