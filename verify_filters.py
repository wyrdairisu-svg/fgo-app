import database
import json

def test_filter(filter_name, expected_id):
    print(f"--- Testing Filter: {filter_name} (Expect ID: {expected_id}) ---")
    results = database.search_servants(filters=[filter_name])
    found = False
    for r in results:
        if r['id'] == expected_id:
            found = True
            print(f"SUCCESS: Found {r['name']} ({r['class_name']})")
    
    if not found:
        print(f"FAILURE: Did not find ID {expected_id}")
        # Debug why
        # By-pass filter to check raw fetch?
        # No, let's just inspect what WAS found
        print(f"Found {len(results)} other results.")

print("running tests...")
test_filter("アンビースト", 4000100) # U-Olga
test_filter("ビースト", 3300200)   # Eresh
test_filter("ビースト", 3300100)   # Draco (Control)
