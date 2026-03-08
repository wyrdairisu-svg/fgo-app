import urllib.request

# Known CC IDs from screenshot
# 8402180 (Forest Guardian)
# 8402120 (Kingmaker)
ids = [8402180, 8402120, 8400010]

patterns = [
    'https://static.atlasacademy.io/JP/CommandCode/{id}.png',
    'https://static.atlasacademy.io/JP/CommandCode/{id}0.png', 
    'https://static.atlasacademy.io/JP/Items/{id}.png',
]

for id in ids:
    print(f'\nChecking ID {id}...')
    for p in patterns:
        url = p.format(id=id)
        try:
            req = urllib.request.Request(url, method='HEAD')
            urllib.request.urlopen(req)
            print(f'[OK] {url}')
        except Exception as e:
            # print(f'[FAIL] {url}')
            pass
