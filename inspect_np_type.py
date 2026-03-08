import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

# Artoria (AoE), Cu (ST), Mash (Support)
targets = [
    (100100, "Artoria (AoE)"),
    (400400, "Cu (ST)"),
    (800100, "Mash (Support)")
]

for id, label in targets:
    cur.execute('SELECT json_data FROM servants WHERE id=?', (id,))
    row = cur.fetchone()
    if row:
        data = json.loads(row[0])
        nps = data.get('noblePhantasms', [])
        if nps:
            np = nps[0] # taking first NP
            outputs = []
            
            # Check functions to determine target
            functions = np.get('functions', [])
            target_types = set()
            for func in functions:
                 # In Atlas data, functions have `funcTargetType`? 
                 # Or we look at `funcTargetTeam`?
                 # Let's print keys of a function to see
                 pass
            
            print(f"--- {label} ---")
            print(f"Card: {np.get('card')}")
            # Print first function's target info if available
            if functions:
                f = functions[0]
                print(f"Func 0: {f.get('funcType')}, Target: {f.get('funcTargetType')}, Team: {f.get('funcTargetTeam')}")
                
            # Usually AoE is enemyAll, ST is enemy, Support is player/playerAll
        else:
            print(f"{label}: No NP found")
    else:
        print(f"{label}: Not found in DB")

conn.close()
