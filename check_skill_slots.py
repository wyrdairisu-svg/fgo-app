import database
import json

s = database.get_servant_detail(100100)
if s:
    data = json.loads(s['json_data'])
    skills = data.get('skills', [])
    # Group by slot (num)
    slots = {}
    for sk in skills:
        num = sk.get('num', -1)
        if num not in slots:
            slots[num] = []
        slots[num].append(sk)
    
    for num, sk_list in slots.items():
        print(f"--- Slot {num} ---")
        for sk in sk_list:
            print(f"  Name: {sk.get('name')} | ID: {sk.get('id')} | StrengthStatus: {sk.get('strengthStatus')}")
