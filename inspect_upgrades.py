import database
import json

conn = database.get_db_connection()
cursor = conn.cursor()
# Artoria (100100) has multiple upgrades
cursor.execute("SELECT json_data FROM servants WHERE id=100100")
data = json.loads(cursor.fetchone()[0])

print("--- SKILLS ---")
# Group by 'num'
skill_groups = {}
for s in data.get('skills', []):
    num = s.get('num')
    if num not in skill_groups:
        skill_groups[num] = []
    skill_groups[num].append(s)

for num in sorted(skill_groups.keys()):
    print(f"Slot {num}:")
    # Sort by priority?
    sorted_skills = sorted(skill_groups[num], key=lambda x: x.get('priority', 0) if x.get('priority') is not None else x.get('id', 0))
    for s in sorted_skills:
        print(f"  ID: {s.get('id')} | Name: {s.get('name')} | Priority: {s.get('priority')} | Detail: {s.get('detail')[:20]}...")

print("\n--- NOBLE PHANTASMS ---")
# NPs typically just list all versions? Or do they have 'num'?
# They usually have 'num' (1)
np_groups = {}
for n in data.get('noblePhantasms', []):
    num = n.get('num')
    if num not in np_groups:
        np_groups[num] = []
    np_groups[num].append(n)

for num in sorted(np_groups.keys()):
    print(f"NP Slot {num}:")
    sorted_nps = sorted(np_groups[num], key=lambda x: x.get('priority', 0) if x.get('priority') is not None else x.get('id', 0))
    for n in sorted_nps:
        print(f"  ID: {n.get('id')} | Name: {n.get('name')} | Priority: {n.get('priority')} | Rank: {n.get('rank')}")
