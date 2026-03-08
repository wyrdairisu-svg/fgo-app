import database
import sys
import inspect

print("STARTING SIMPLE VERIFY")
print(f"DB FILE: {database.__file__}")
try:
    print("SOURCE CODE loaded:")
    print(inspect.getsource(database.search_craft_essences)[:500])
except Exception as e:
    print(f"FAILED TO GET SOURCE: {e}")

try:
    results = database.search_craft_essences(filters=['np_80plus'], limit=5)
    print(f"RESULTS COUNT: {len(results)}")
    for r in results:
        print(f"RES: {r['name']}")
except Exception as e:
    print(f"EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("ENDING SIMPLE VERIFY")
