import database
import urllib.request

conn = database.get_db_connection()
cur = conn.cursor()
cur.execute('SELECT id, name FROM craft_essences LIMIT 1')
row = cur.fetchone()
conn.close()

if row:
    id = row[0]
    name = row[1]
    print(f'Checking CE {name} (ID: {id})...')
    
    # Try Equip URL
    # usually: https://static.atlasacademy.io/JP/Equip/{id}/1.png (Normal)
    # or {id}/2.png (MLB?)
    
    url = f'https://static.atlasacademy.io/JP/Equip/{id}/1.png'
    try:
        urllib.request.urlopen(url)
        print(f'Valid URL: {url}')
    except Exception as e:
        print(f'Invalid URL: {url} | Error: {e}')
        
    # Try different pattern if needed
    url2 = f'https://static.atlasacademy.io/JP/CharaGraph/{id}/{id}a.png'
    try:
        urllib.request.urlopen(url2)
        print(f'Valid URL2: {url2}')
    except Exception as e:
        print(f'Invalid URL2: {url2} | Error: {e}')
else:
    print("No CE found")
