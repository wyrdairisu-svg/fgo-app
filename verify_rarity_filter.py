import database
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

print("--- Testing Rarity Filter (5★) ---")
# Filter '5' (int) or '5' (str)
results = database.search_servants(filters=[5], limit=5)
for s in results:
    print(f"Name: {s['name']} | Rarity: {s['rarity']}")
    if int(s['rarity']) != 5:
        print("FAILURE: Found non-5-star servant!")

print("\n--- Testing Rarity Filter (1★) ---")
results = database.search_servants(filters=['1'], limit=5)
for s in results:
    print(f"Name: {s['name']} | Rarity: {s['rarity']}")
    if int(s['rarity']) != 1:
        print("FAILURE: Found non-1-star servant!")
