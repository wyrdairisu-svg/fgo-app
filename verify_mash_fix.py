import database
import json

print("\n--- Testing Mash Ortinax (800101) ---")
detail = database.get_servant_detail(800101)
if detail:
    print(f"Name: {detail.get('name')}")
    print(f"Class: {detail.get('class_name')}")
    
    # Skills
    print(f"Skill Count: {len(detail.get('skill_slots', []))}")
    for i, slot in enumerate(detail.get('skill_slots', [])):
        print(f"Slot {i+1}: {[s['name'] for s in slot]}")

    # NPs
    print(f"NP Count: {len(detail.get('np_slots', []))}")
    for i, slot in enumerate(detail.get('np_slots', [])):
        print(f"NP Slot {i+1}: {[n['name'] + ' (' + n['type'] + ')' for n in slot]}")
else:
    print("Result is None")
