import database
import json

def test_kscope_logic():
    print("--- TESTING KALEIDOSCOPE LOGIC DEEP ---")
    
    # 1. Fetch Kaleidoscope manually
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM craft_essences WHERE name LIKE '%カレイドスコープ%'")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("CRITICAL: Kaleidoscope not found in DB!")
        return

    row = dict(rows[0])
    data = json.loads(row['json_data'])
    print(f"Loaded: {row['name']} (ID: {row['id']})")
    
    # 2. Define Filter Scenarios
    scenarios = [
        (['np_80plus'], True),
        (['np_50plus'], True),
        (['np_100'], False),
        (['stat_atk'], True),
        (['stat_hp'], False),
        (['tac_taunt'], False),
        (['cost_12'], True) 
    ]
    
    for filters, expected in scenarios:
        print(f"\nTesting Filters: {filters}")
        # Call the logic directly
        result = database.filter_ce_advanced(row, data, filters)
        status = "PASS" if result == expected else "FAIL"
        print(f"  -> Result: {result} | Expected: {expected} | Status: {status}")
        
if __name__ == "__main__":
    test_kscope_logic()
