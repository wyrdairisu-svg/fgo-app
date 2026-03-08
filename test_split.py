import re
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

text = "花咲翁とフローラの相性について教えて"
delimiters = r'[ 　,、と＆\+の]|について|相性|を|教えて|は|が'
parts = re.split(delimiters, text)

print(f"Original: {text}")
print(f"Parts: {parts}")
for i, p in enumerate(parts):
    print(f"Part {i}: '{p}' (Len: {len(p)})")
