import database
import json

def inspect_ce(name_part):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, json_data FROM craft_essences WHERE name LIKE ?", (f'%{name_part}%',))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print(f"\n=== INSPECTING: {row['name']} ===")
        try:
            data = json.loads(row['json_data'])
            # Print specifically the skills/functions part which determines attributes
            if 'skills' in data and data['skills']:
                for i, skill in enumerate(data['skills']):
                    print(f"Skill {i+1}:")
                    for func in skill.get('functions', []):
                        print(f"  - FuncType: {func.get('funcType')}")
                        print(f"    svals: {func.get('svals')}")
            else:
                print("No skills data found.")
        except Exception as e:
            print(f"JSON Error: {e}")
            print(f"Raw: {row['json_data'][:200]}...")
    else:
        print(f"\nCE with name '{name_part}' not found.")

if __name__ == "__main__":
    inspect_ce("カレイドスコープ") # NP Charge
    inspect_ce("黒の聖杯") # Demerit, Power Mod
    inspect_ce("虚数魔術") # NP Charge
    inspect_ce("フォーマルクラフト") # Arts Up
