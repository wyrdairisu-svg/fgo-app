import database
import json

s = database.get_servant_detail(100100)
if s:
    data = json.loads(s['json_data'])
    print("Name:", s['name'])
    print("\nSkills:")
    for sk in data.get('skills', []):
        print(f"- {sk.get('name')}: {sk.get('detail')}")
    
    print("\nNPs:")
    for np in data.get('noblePhantasms', []):
         print(f"- {np.get('name')}: {np.get('detail')}")
else:
    print("Not found")
