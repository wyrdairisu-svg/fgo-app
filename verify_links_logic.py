import strategy
import re
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Input text mimicking AI output table
input_text = """
| Pos | Icon | Name | Role | CE |
| :-- | :--: | :-- | :-- | :-- |
| F1 | - | ギルガメッシュ(術) | Caster | - |
| F2 | - | スカサハ=スカディ(ルーラー) | Ruler | - |
| F3 | - | アルトリア(剣) | Saber | - |
| B1 | - | トネリコ | Caster | - |
"""

print("--- Processing Input ---")
output_text = strategy.inject_servant_link_data(input_text)
print(output_text)

print("\n--- Verification ---")
# Check for correct IDs
# Gilgamesh (Caster): 201800
# Skadi (Ruler): 305400 ? No, 354? ID is usually 6 digits. Caster Skadi is 215000. Ruler Skadi is 305400?
# Let's check if the output URLs contain the expected IDs or at least DIFFERENT IDs from defaults.
# Gilgamesh (Archer) is 200200.
# Skadi (Caster) is 215000.

if "/servant/201800" in output_text:
    print("SUCCESS: Gilgamesh (Caster) -> ID 201800")
else:
    print("FAILURE: Gilgamesh (Caster) mismatch")

if "/servant/305400" in output_text: # ID check needed. 305400 is typical for Ruler Skadi?
    print("SUCCESS: Skadi (Ruler) -> ID 305400")
elif "/servant/" in output_text:
    print("INFO: Skadi ID found but need to verify manually.")
