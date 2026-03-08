import urllib.request
import json

url = 'https://api.atlasacademy.io/export/JP/basic_servant.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

with urllib.request.urlopen(req) as r:
    data = json.loads(r.read().decode())
    for s in data:
        if "フローラ" in s.get('name', ''):
            print(f"URL: {s.get('face')}")
            break
