import database
import json

def check_entity(id, label):
    with open("protocol_verify.log", "a", encoding="utf-8") as f:
        f.write(f"\n--- {label} (ID: {id}) ---\n")
        
    detail = database.get_servant_detail(id)
    with open("protocol_verify.log", "a", encoding="utf-8") as f:
        if not detail:
            f.write("Data NOT FOUND\n")
            return

        f.write(f"Name: {detail.get('name')}\n")
        f.write(f"Class: {detail.get('class_name')}\n")
        
        f.write("Skills:\n")
        for i, s in enumerate(detail.get('skill_slots', [])):
            if not s: # Empty list safety
                f.write(f"  Slot {i+1}: []\n")
                continue
            names = [x['name'] for x in s]
            f.write(f"  Slot {i+1}: {names}\n")

        f.write("Noble Phantasm:\n")
        for i, slot in enumerate(detail.get('np_slots', [])):
             # detail['np_slots'] returns list of dicts.
            names = [f"{x['name']} (Rank: {x.get('rank')}, Type: {x.get('type')})" for x in slot]
            f.write(f"  {names}\n")

if __name__ == "__main__":
    with open("protocol_verify.log", "w", encoding="utf-8") as f:
        f.write("START VERIFICATION\n")

    check_entity(800100, "ENTITY_MASH_V1 (PRE_LOSTBELT)")
    check_entity(800101, "ENTITY_MASH_V2 (ORTENAUS)") 
    check_entity(800102, "ENTITY_MASH_V3 (PALADIN)")
