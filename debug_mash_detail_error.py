import database
import json
import traceback

print("--- Debugging Mash Ortinax (800101) ---")
try:
    detail = database.get_servant_detail(800101)
    if detail:
        print(f"Name: {detail['name']}")
        print(f"ID: {detail['id']}")
        print(f"Class: {detail['class_name']}")
        
        # Check Skills
        print("\nSkills:")
        for slot in detail.get('skill_slots', []):
            for sk in slot:
                 print(f"  - {sk.get('name')}")
                 
        # Check NPs
        print("\nNPs:")
        for slot in detail.get('np_slots', []):
            for np in slot:
                print(f"  - {np.get('name')} (Type: {np.get('type')})")
    else:
        print("Result is None")
except Exception:
    traceback.print_exc()

print("\n--- Direct Transformation Check ---")
conn = database.get_db_connection()
cur = conn.cursor()
cur.execute("SELECT * FROM servants WHERE id=800100")
row = cur.fetchone()
conn.close()

servant = dict(row)
target_id_alias = 800101

try:
    data = json.loads(servant["json_data"])
    all_skills = data.get('skills', [])
    all_nps = data.get('noblePhantasms', [])
    
    idx_ortinax = [4, 5, 7]
    idx_paladin = [8, 9, 11]
    idx_exclude_from_base = idx_ortinax + idx_paladin
    
    idx_np_ortinax = 6
    idx_np_paladin = 8
    
    # Simulate Logic
    if target_id_alias == 800101:
        print("Simulating Ortinax Logic...")
        if len(all_nps) > idx_np_ortinax:
             data['noblePhantasms'] = [all_nps[idx_np_ortinax]]
             print("NP Filtered OK")
        else:
             print(f"NP Index {idx_np_ortinax} out of range (Len: {len(all_nps)})")
        
        data['skills'] = [s for i, s in enumerate(all_skills) if i in idx_ortinax]
        print(f"Skills Filtered: {len(data['skills'])} items")

except Exception as e:
    print(f"CAUGHT ERROR: {e}")
    traceback.print_exc()
