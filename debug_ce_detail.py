import database
import json

def inspect_ce(name):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM craft_essences WHERE name LIKE ?", (f'%{name}%',))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print(f"--- {row['name']} (ID: {row['id']}) ---")
        print(f"Detail Field: '{row['detail']}'")
        print(f"JSON Data keys: {json.loads(row['json_data']).keys() if row['json_data'] else 'None'}")
    else:
        print(f"CE '{name}' not found.")

if __name__ == "__main__":
    with open("inspect_detail.txt", "w", encoding="utf-8") as f:
        import sys
        sys.stdout = f
        inspect_ce("カルデア・ランチタイム")
        inspect_ce("モナ・リザ")
        inspect_ce("看板娘")
