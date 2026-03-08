import database
import json
import sys

def dump_np_json(svt_id):
    svt = database.get_servant_detail(svt_id)
    if not svt:
        print(f"ID {svt_id} not found")
        return

    data = json.loads(svt['json_data'])
    nps = data.get('noblePhantasms', [])
    
    print(f"--- Servant ID: {svt_id} ({svt['name']}) ---")
    print(json.dumps(nps, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    with open("np_dump.json", "w", encoding="utf-8") as f:
        sys.stdout = f
        dump_np_json(104800) # Okita (Quick)
