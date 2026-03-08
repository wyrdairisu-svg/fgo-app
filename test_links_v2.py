import database
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

test_cases = [
    "ギルガメッシュ",      
    "ギルガメッシュ (術)",  
    "アルトリア",          
    "アルトリア・キャスター",
    "光のコヤンスカヤ",
    "闇のコヤンスカヤ",
    "スカサハ",            
    "スカサハ=スカディ",   
    "スカサハ=スカディ (ルーラー)",
    "マシュ",              
    "妖精騎士ランスロット", 
    "メリュジーヌ",        
    "オベロン",            
    "トネリコ"             
]

for q in test_cases:
    # Use strategy.py logic: clean up parens if needed? 
    # strategy.py does: clean_name = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', raw_name_col) -> DB
    
    results = database.search_servants(q, limit=1)
    if results:
        top = results[0]
        print(f"[{q}] -> ID:{top['id']} Name:{top['name']} Class:{top['class_name']}")
    else:
        # Fallback logic in strategy.py: remove parens
        import re
        base_name = re.sub(r'\s*\(.*?\)', '', q)
        if base_name != q:
             res2 = database.search_servants(base_name, limit=1)
             if res2:
                 top = res2[0]
                 print(f"[{q}] (Fallback: {base_name}) -> ID:{top['id']} Name:{top['name']} Class:{top['class_name']}")
             else:
                 print(f"[{q}] -> NOT FOUND")
        else:
            print(f"[{q}] -> NOT FOUND")
