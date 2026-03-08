import urllib.request
import json

url = 'https://api.atlasacademy.io/export/JP/basic_servant.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    print(f"Fetching {url}...")
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read().decode())
        if data:
            entry = data[0]
            print(f"ID: {entry.get('id')}")
            print(f"Name: {entry.get('name')}")
            print(f"Face URL: {entry.get('face')}")
            
            # Check specifically for Flora or Artoria if possible
            for s in data:
                if s.get('id') == 100100: # Artoria
                    print(f"Artoria Face: {s.get('face')}")
                if "フローラ" in s.get('name', ''):
                    print(f"Flora Face: {s.get('face')}")
                    break
except Exception as e:
    print(f"Error: {e}")
