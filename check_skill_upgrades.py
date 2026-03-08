import database
import json

# Check Altria (known to have upgrades)
s = database.get_servant_detail(100100)
if s:
    data = json.loads(s['json_data'])
    print(f"Name: {s['name']}")
    print("Skills:")
    for i, sk in enumerate(data.get('skills', [])):
        print(f"[{i}] ID:{sk.get('id')} Name:{sk.get('name')} Type:{sk.get('type')} Priority:{sk.get('priority', 'N/A')} StrengthStatus:{sk.get('strengthStatus', 'N/A')}")
        # Sometimes 'cond' or other fields indicate unlock requirements
