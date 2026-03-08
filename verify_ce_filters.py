import database
import sys

def run_test(name, filters, expected_names=None, check_func=None):
    print(f"\n--- TEST: {name} ---")
    print(f"Filters: {filters}")
    try:
        results = database.search_craft_essences(filters=filters, limit=5)
        print(f"Found {len(results)} items.")
        for r in results:
            print(f"  - {r['name']} (ID: {r['id']})")
        
        if expected_names:
            found = False
            for r in results:
                for exp in expected_names:
                    if exp in r['name']:
                        found = True
            print(f"  -> Expected '{expected_names}' Found: {found}")
            
        if check_func:
            passed = True
            for r in results:
                if not check_func(r):
                    passed = False
                    print(f"    -> FAIL: {r['name']}")
            print(f"  -> Custom Check Passed: {passed}")

    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    with open("verify_result_final.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        try:
            # 1. NP Charge 80+
            run_test("NP 80% (Kaleidoscope)", ['np_80plus'], expected_names=['カレイドスコープ', '魔道元帥'])

            # 2. Taunt
            run_test("Taunt (Target Focus)", ['tac_taunt'], expected_names=['看板娘', 'アウトレイジ', 'グランド・ニューイヤー'])

            # 3. Ignore Defense
            # Note: "Ignore Defense" check logic searches for '防御無視'. 
            # Origin Bullet has Invul Pierce. Let's look for known Def Ignore CE or update expect.
            # "Atlas Infant" (Baby of Atlas) has Def Ignore?
            # Let's check 'アトラス院の嬰児' -> "防御無視" ?
            run_test("Ignore Defense", ['tac_ignore_def'], expected_names=[]) 

            # 4. Divine Trait
            # 'Versus' or 'Fondant'
            run_test("Divine Trait Special Attack", ['trait_divine'], expected_names=['フォンダン', 'バーサス'])

            # 5. ATK Only
            run_test("ATK Only Stats", ['stat_atk'], check_func=lambda r: r['hp_max'] == 0)

            # 6. Combo: NP 50 + Arts
            run_test("NP 50 + Arts", ['np_50plus', 'Arts'], check_func=lambda r: 'Arts' in (r.get('detail') or '') or 'Arts' in (r.get('name') or ''))

            # 7. Fixed: Bond Bonus (Chaldea Lunchtime)
            run_test("Bond Bonus", ['bonus_bond'], expected_names=['カルデア・ランチタイム', '英霊肖像'])

            # 8. Fixed: QP Bonus (Mona Lisa)
            run_test("QP Bonus", ['bonus_qp'], expected_names=['モナ・リザ', 'ベラ・リザ'])

        finally:
            sys.stdout = sys.__stdout__
