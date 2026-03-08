import database
import logging

# Suppress other logs
logging.basicConfig(level=logging.ERROR)

results = database.search_servants(filters=[])
# Check for No. 464
flora = [r for r in results if r['collection_no'] == 464]
print(f"Flora (464) count: {len(flora)}")
for f in flora:
    print(f"- ID: {f['id']} | Name: {f['name']}")

# Check for Hebi (463)
hebi = [r for r in results if r['collection_no'] == 463]
print(f"Hebi (463) count: {len(hebi)}")
for h in hebi:
    print(f"- ID: {h['id']} | Name: {h['name']}")

if len(flora) > 1 or len(hebi) > 1:
    print("FAIL: Duplicates found")
else:
    print("PASS: No duplicates")
