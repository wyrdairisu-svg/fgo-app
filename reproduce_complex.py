import requests

def test_complex():
    base_url = "http://127.0.0.1:5000/craft_essences"
    
    # User Scenario: Query='カレイド', Filters=['Buster', 'stat_atk', 'stat_balance', 'tac_taunt']
    # If the user checks multiple boxes, 'filters' parm is repeated.
    params = [
        ('q', 'カレイド'),
        ('filters', 'Buster'),
        ('filters', 'stat_atk'),
        ('filters', 'stat_balance'),
        ('filters', 'tac_taunt')
    ]
    
    print("\n--- Test Complex: Query + Multiple Filters ---")
    print(f"Params: {params}")
    
    try:
        resp = requests.get(base_url, params=params)
        print(f"Status: {resp.status_code}")
        
        if 'カレイドスコープ' in resp.text:
            print("FAIL: Found Kaleidoscope! Backend is treating filters as OR or ignoring them.")
            # Let's count how many results
            count = resp.text.count('class="chaldea-card servant-item"')
            print(f"Total Results: {count}")
        else:
            print("PASS: Kaleidoscope correctly filtered out.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_complex()
