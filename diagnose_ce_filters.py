import database
import json

def test_filter(filter_key, expected_contain_name):
    print(f"\n--- Testing Filter: {filter_key} ---")
    results = database.search_craft_essences(filters=[filter_key], limit=50)
    
    found_names = [r['name'] for r in results]
    match = False
    for name in found_names:
        if expected_contain_name in name:
            match = True
            break
            
    print(f"Target: '{expected_contain_name}'")
    print(f"Result: {'PASSED' if match else 'FAILED'}")
    if not match:
        print(f"  -> Found {len(results)} items: {found_names[:5]}...")
        # Deep dive: Find the target item without filter and inspect why it failed
        verify_failure(filter_key, expected_contain_name)

def verify_failure(filter_key, target_name):
    print(f"  [DIAGNOSIS] Inspecting why '{target_name}' failed for '{filter_key}'...")
    all_res = database.search_craft_essences(query=target_name, limit=5)
    target = None
    for r in all_res:
        if target_name in r['name']:
            target = r
            break
            
    if not target:
        print("  -> ERROR: Target item not found in DB even without filter!")
        return

    # Check logic manually
    data = json.loads(target['json_data']) if target.get('json_data') else {}
    row = target
    
    # Re-run filter logic (copy of database.py logic for debugging)
    # We'll just call the function if we can, or simulate it.
    # Since filter_ce_advanced is checking the row, let's print relevant fields.
    
    print(f"  -> Item: {row['name']} (ID: {row['id']})")
    print(f"  -> Detail: {row.get('detail')}")
    
    if filter_key.startswith('np_'):
        print("  -> Checking NP Charge logic...")
        skills = data.get('skills', [])
        found_vals = []
        for skill in skills:
            for func in skill.get('functions', []):
                if func.get('funcType') == 'gainNp':
                    for sval in func.get('svals', []):
                         found_vals.append(sval.get('Value'))
        print(f"    -> Found GainNP values: {found_vals}")

    elif filter_key.startswith('tac_') or filter_key.startswith('trait_') or filter_key.startswith('bonus_'):
        print("  -> Checking Text Search logic...")
        text = (row.get('detail') or "") + (row.get('name') or "")
        print(f"    -> Search Text (Snippet): {text[:50]}...")
        
        if filter_key == 'tac_ignore_def':
            print(f"    -> Contains '防御無視'? {'防御無視' in text}")
        elif filter_key == 'tac_taunt':
            print(f"    -> Contains 'ターゲット集中'? {'ターゲット集中' in text}")
        elif filter_key == 'trait_divine':
            print(f"    -> Contains '〔神性〕特攻'? {'〔神性〕特攻' in text}")
    
    elif filter_key.startswith('stat_'):
        print(f"  -> Stats: HP={row.get('hp_max')}, ATK={row.get('atk_max')}")

if __name__ == "__main__":
    with open("diagnose_log.txt", "w", encoding='utf-8') as f:
        import sys
        original_stdout = sys.stdout
        sys.stdout = f
        
        try:
            # 1. NP Charge
            test_filter('np_80plus', 'カレイドスコープ') # Kaleidoscope
            
            # 2. Stats
            test_filter('stat_atk', '黒の聖杯') # Black Grail is ATK only

            # 3. Tactics
            test_filter('tac_ignore_def', '起源弾') # Origin Bullet
            test_filter('tac_taunt', 'ぐだぐだ看板娘') # GUDAGUDA Poster Girl
            test_filter('tac_on_death', '五百年の妄執') # 500-Year Obsession
            test_filter('tac_oc_up', '魔性菩薩') # Devilish Bodhisattva

            # 4. Traits
            test_filter('trait_divine', 'フォンダン・オ・ショコラ') # DIVINE Special Attack
            test_filter('trait_humanoid', '死の芸術') # Humanoid Special Attack
            
            # 5. Bonus
            test_filter('bonus_bond', 'カルデア・ランチタイム')
            test_filter('bonus_qp', 'モナ・リザ')
        finally:
            sys.stdout = original_stdout
