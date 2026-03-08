import database
import json

conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, name, json_data FROM servants WHERE collection_no > 0 AND id < 9000000")
rows = cursor.fetchall()
conn.close()

count_fixed = 0
for r in rows:
    data = json.loads(r['json_data'])
    nps = data.get('noblePhantasms', [])
    if not nps:
        continue
        
    # Current Logic Simulation
    np_types = set()
    first_np = nps[0] # Just check first distinct NP usually
    
    # Check all NPs to be safe (like in database.py) since sometimes they upgrade
    current_is_attack = False
    current_is_aoe = False
    
    for np in nps:
        for func in np.get("functions", []):
            ftype = func.get("funcType", "")
            target_type = func.get("funcTargetType", "")
            if "damageNp" in ftype:
                current_is_attack = True
                if "enemyAll" in target_type:
                    current_is_aoe = True
    
    # Fallback Logic Test
    detail_is_attack = False
    detail_is_aoe = False
    detail_text = ""
    
    for np in nps:
        d = np.get("detail", "")
        if "敵全体" in d and "強力な攻撃" in d:
            detail_is_attack = True
            detail_is_aoe = True
            detail_text = d
        elif "敵単体" in d and "強力な攻撃" in d:
            detail_is_attack = True # ST
            detail_text = d
            
    # Diagnosis
    if r['id'] == 106000:
        print(f"IORI STATUS: CurrentAttack={current_is_attack}, DetailAttack={detail_is_attack}, DetailAOE={detail_is_aoe}")
        
    # If Current says Support (Not Attack) BUT Detail says Attack -> Mismatch
    if not current_is_attack and detail_is_attack:
        print(f"[MISMATCH] ID: {r['id']} {r['name']}")
        print(f"  - Logic: Support")
        print(f"  - Text: {'AoE' if detail_is_aoe else 'ST'} (Found keyword in detail)")
        count_fixed += 1

print(f"Total Mismatches found: {count_fixed}")
