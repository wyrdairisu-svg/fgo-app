import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

sid = 400400 # Cu
cur.execute('SELECT json_data FROM servants WHERE id=?', (sid,))
row = cur.fetchone()
if row:
    data = json.loads(row[0])
    np = data['noblePhantasms'][0]
    
    is_attack = False
    is_aoe = False
    
    print(f"Functions Count: {len(np.get('functions', []))}")
    
    for i, func in enumerate(np.get("functions", [])):
        ftype = func.get("funcType", "")
        target = func.get("funcTargetTeam", "")
        print(f"Func {i}: Type='{ftype}' Target='{target}'")
        
        if "damageNp" in ftype:
            is_attack = True
            print(f"  -> Attack Detected")
            if "enemyAll" in target or "playerAndEnemy" in target:
                is_aoe = True
                print(f"  -> AoE Detected")
            else:
                print(f"  -> ST (Currently)")

    if is_attack:
        np_type = "AoE" if is_aoe else "ST"
    else:
        np_type = "Support"
        
    print(f"Final Prediction: {np_type}")
else:
    print("Cu not found")

conn.close()
