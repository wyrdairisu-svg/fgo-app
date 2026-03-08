import database
import json

def inspect_mash():
    # Use Mash or Artoria
    res = database.search_servants('アルトリア', limit=1)
    if not res:
        print("Servant not found")
        return

    svt = res[0]
    print(f"Checking {svt['name']} (ID: {svt['id']})")
    data = json.loads(svt['json_data'])
    
    print("\n--- SKILLS ---")
    if 'skills' in data:
        for sk in data['skills'][:3]:
            # print(f"Name: {sk.get('name')}")
            print(f"Skill Icon Value: '{sk.get('icon')}'")
            # print(f"Keys: {sk.keys()}")

    print("\n--- NP ---")
    if 'noblePhantasms' in data:
        for np in data['noblePhantasms'][:1]:
            print(f"Name: {np.get('name')}")
            print(f"Card: {np.get('card')}")
            print(f"Icon: {np.get('icon')}")
            print(f"Keys: {np.keys()}")

if __name__ == "__main__":
    inspect_mash()
