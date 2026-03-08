import database
import json

print("--- Testing ID 800100 (Normal) ---")
normal = database.get_servant_detail(800100)
if normal:
    print(f"Name: {normal['name']}")
    print(f"Class: {normal['class_name']}")
    has_ortinax = False
    for slot in normal['np_slots']:
        for np in slot:
            if "オルテナウス" in np['name'] or "希望証す人理の剣" in np['name']:
                has_ortinax = True
                print(f"WARNING: Found Ortinax NP in Normal: {np['name']}")
    if not has_ortinax:
        print("PASS: No Ortinax NP found in Normal.")

print("\n--- Testing ID 800101 (Paladin) ---")
paladin = database.get_servant_detail(800101)
if paladin:
    print(f"Name: {paladin['name']}")
    print(f"Class: {paladin['class_name']}")
    found_ortinax = False
    for slot in paladin['np_slots']:
         for np in slot:
            print(f"NP Name: {np['name']}")
            if "希望証す人理の剣" in np['name']:
                found_ortinax = True
    
    if found_ortinax:
        print("PASS: Found Ortinax NP in Paladin.")
    else:
        print("FAIL: Ortinax NP missing in Paladin.")
else:
    print("FAIL: ID 800101 returned None.")
