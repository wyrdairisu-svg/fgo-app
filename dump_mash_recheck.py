import database
import json

conn = database.get_db_connection()
cur = conn.cursor()

with open('debug_mash_recheck.log', 'w', encoding='utf-8') as f:
    cur.execute('SELECT json_data FROM servants WHERE id=800100')
    row = cur.fetchone()
    data = json.loads(row[0])

    f.write("--- Noble Phantasms ---\n")
    for i, np in enumerate(data.get('noblePhantasms', [])):
        f.write(f"Index {i}: {np.get('name')} (Card: {np.get('card')})\n")

    f.write("\n--- Skills ---\n")
    for i, sk in enumerate(data.get('skills', [])):
        f.write(f"Index {i}: {sk.get('name')} (Num: {sk.get('num')}, Priority: {sk.get('priority')})\n")

    f.write("\n--- Assets / Skins ---\n")
    # Check for limit count images or skins
    extra = data.get('extraAssets', {})
    f.write(f"Extra Assets Keys: {extra.keys()}\n")
    
    # Faces
    faces = extra.get('faces', {})
    if hasattr(faces, 'get'):
        f.write(f"Faces Ascension: {faces.get('ascension', {}).keys()}\n")
        f.write(f"Faces Costume: {faces.get('costume', {}).keys()}\n")
    
conn.close()
