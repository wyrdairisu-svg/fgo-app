import database
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

test_cases = [
    "ギルガメッシュ",      # Should be Archer?
    "ギルガメッシュ(術)",  # Should be Caster
    "アルトリア",          # Ambiguous
    "コヤンスカヤ",        # Light or Dark?
    "スカサハ",            # Lancer?
    "スカサハ=スカディ",   # Caster or Ruler?
    "マシュ",              # Shielder
    "妖精騎士ランスロット", # Melusine
    "メリュジーヌ",        # Melusine
    "オベロン",            # Oberon
    "トネリコ"             # Aesc
]

print(f"{'Query':<20} | {'ID':<10} | {'Name':<30} | {'Class':<10}")
print("-" * 80)

for q in test_cases:
    results = database.search_servants(q, limit=3)
    if results:
        top = results[0]
        print(f"{q:<20} | {top['id']:<10} | {top['name']:<30} | {top['class_name']:<10}")
        # if len(results) > 1:
        #    print(f"   (2nd match: {results[1]['name']} - {results[1]['class_name']})")
    else:
        print(f"{q:<20} | NOT FOUND")
