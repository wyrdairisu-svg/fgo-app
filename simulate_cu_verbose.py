import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

sid = 400400 # Cu
cur.execute('SELECT json_data FROM servants WHERE id=?', (sid,))
row = cur.fetchone()

with open('debug_cu.log', 'w') as f:
    if row:
        data = json.loads(row[0])
        np = data['noblePhantasms'][0]
        
        is_attack = False
        is_aoe = False
        
        f.write(f"Functions Count: {len(np.get('functions', []))}\n")
        
        for i, func in enumerate(np.get("functions", [])):
            ftype = func.get("funcType", "")
            target = func.get("funcTargetTeam", "")
            f.write(f"Func {i}: Type='{ftype}' Target='{target}'\n")
            
            if "damageNp" in ftype:
                is_attack = True
                f.write(f"  -> Attack Detected (matched 'damageNp')\n")
                if "enemyAll" in target or "playerAndEnemy" in target:
                    is_aoe = True
                    f.write(f"  -> AoE Detected (matched target)\n")
                else:
                    f.write(f"  -> ST Condition Found\n")

        if is_attack:
            np_type = "AoE" if is_aoe else "ST"
        else:
            np_type = "Support"
            
        f.write(f"Final Prediction: {np_type}\n")
    else:
        f.write("Cu not found\n")

conn.close()
