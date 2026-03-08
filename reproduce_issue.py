import requests
import re

def test_repro():
    base_url = "http://127.0.0.1:5000/craft_essences"
    
    # 1. Baseline: Search for Kaleido (Expect Found)
    print("--- Test 1: Query Only ---")
    resp = requests.get(base_url, params={'q': 'カレイド'})
    if 'カレイドスコープ' in resp.text:
        print("PASS: Found Kaleidoscope with query only.")
    else:
        print("FAIL: Kaleidoscope NOT found with query only.")

    # 2. Filter: Kaleido + Taunt (Expect NOT Found)
    print("\n--- Test 2: Query + Taunt Filter ---")
    # Simulate: ?q=カレイド&filters=tac_taunt
    resp = requests.get(base_url, params={'q': 'カレイド', 'filters': 'tac_taunt'})
    
    # We need to check if Kscope is in the RESULT LIST.
    # The page might just show "No results".
    if 'カレイドスコープ' in resp.text:
        print("FAIL: Found Kaleidoscope despite Taunt Filter! (Backend Logic Broken)")
        # Print count if possible
        count = resp.text.count('class="chaldea-card servant-item"')
        print(f"Items returned: {count}")
    else:
        print("PASS: Kaleidoscope correctly filtered out. (Backend Logic OK)")

    # 3. Filter: Kaleido + NP 80% (Expect Found)
    print("\n--- Test 3: Query + NP 80% Filter ---")
    resp = requests.get(base_url, params={'q': 'カレイド', 'filters': 'np_80plus'})
    if 'カレイドスコープ' in resp.text:
        print("PASS: Found Kaleidoscope with NP 80% Filter.")
    else:
        print("FAIL: Kaleidoscope NOT found with NP 80% filter. (Logic Error?)")

if __name__ == "__main__":
    test_repro()
