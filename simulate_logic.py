import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

targets = [
    (100100, "Artoria"),
    (400400, "Cu Chulainn"),
    (800100, "Mash")
]

for sid, name in targets:
    cur.execute('SELECT json_data FROM servants WHERE id=?', (sid,))
    row = cur.fetchone()
    if row:
        data = json.loads(row[0])
        np = data['noblePhantasms'][0]
        
        # LOGIC PASTE START
        # Type: Check functions for damage
        is_attack = False
        is_aoe = False
        
        debug_logs = []
        
        for func in np.get("functions", []):
            ftype = func.get("funcType", "")
            target = func.get("funcTargetTeam", "")
            
            # 'damageNp', 'damageNpPierce'
            if "damageNp" in ftype:
                is_attack = True
                debug_logs.append(f"Found Attack Func: {ftype} Target: {target}")
                # 'enemyAll' (Standard AoE), 'enemyAllElsewhere'
                # 'playerAndEnemy' (Some global AoE?) -> Treat as overall AoE context if damage
                if "enemyAll" in target or "playerAndEnemy" in target:
                    is_aoe = True
                    debug_logs.append(" -> Identified as AoE")
        
        if is_attack:
            np_type = "AoE" if is_aoe else "ST"
        else:
            np_type = "Support"
        # LOGIC PASTE END
        
        print(f"--- {name} ({sid}) ---")
        print(f"Result: {np_type}")
        for log in debug_logs:
            print(log)
    else:
        print(f"{name} not found")

conn.close()
