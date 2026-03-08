import sqlite3
import db_builder

DB_FILENAME = "fgo_full_data_jp.db"
conn = sqlite3.connect(DB_FILENAME)
cursor = conn.cursor()
# 'wars' is the last item, url ends with nice_war.json
url = "https://api.atlasacademy.io/export/JP/nice_war.json"
print(f"Clearing meta info for: {url}")
cursor.execute("DELETE FROM _meta_info WHERE url = ?", (url,))
conn.commit()
conn.close()

print("Running update to populate cache for War...")
db_builder.run_update()
