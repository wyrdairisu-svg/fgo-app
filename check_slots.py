import database
import json

s = database.get_servant_detail(100100) # Artoria

if not s:
    print("Servant not found")
else:
    print(f"Name: {s.get('name')}")
    
    if 'skill_slots' in s:
        print(f"Skill Slots Count: {len(s['skill_slots'])}")
        for i, slot in enumerate(s['skill_slots']):
            print(f"  Slot {i+1} Versions: {len(slot)}")
            for j, skill in enumerate(slot):
                print(f"    v{j+1}: {skill.get('name')}")
    else:
        print("No skill_slots found")

    if 'np_slots' in s:
        print(f"NP Slots Count: {len(s['np_slots'])}")
        for i, slot in enumerate(s['np_slots']):
            print(f"  NP Slot {i+1} Versions: {len(slot)}")
            for j, np in enumerate(slot):
                print(f"    v{j+1}: {np.get('name')}")
    else:
        print("No np_slots found")
