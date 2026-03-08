
import json
import database

def check_koyan():
    svt_id = 604000
    print(f"Checking ID: {svt_id}")
    svt = database.get_servant_detail(svt_id)
    if not svt:
        print("Not found")
        return

    data = json.loads(svt['json_data'])
    print(f"Name: {svt['name']}")
    for sk in data.get('skills', []):
        print(f"Skill: {sk.get('name')} / {sk.get('detail')}")

if __name__ == "__main__":
    check_koyan()
