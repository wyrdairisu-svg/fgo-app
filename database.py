import sqlite3
import os
import json

DB_FILENAME = "fgo_full_data_jp.db"
USER_DB_FILENAME = "user_data.db"

def init_user_db():
    """ユーザーデータ用DBの初期化"""
    conn = sqlite3.connect(USER_DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS view_history (
            servant_id INTEGER PRIMARY KEY,
            updated_at REAL
        )
    ''')
    conn.commit()
    conn.close()

def log_servant_view(servant_id):
    """サーヴァント閲覧履歴を保存"""
    import time
    init_user_db()
    conn = sqlite3.connect(USER_DB_FILENAME)
    c = conn.cursor()
    # OR REPLACE works in SQLite to update priority
    c.execute('INSERT OR REPLACE INTO view_history (servant_id, updated_at) VALUES (?, ?)', 
              (servant_id, time.time()))
    conn.commit()
    conn.close()

def get_recent_servant_ids(limit=10):
    """閲覧履歴からIDを取得"""
    if not os.path.exists(USER_DB_FILENAME):
        return []
    
    conn = sqlite3.connect(USER_DB_FILENAME)
    c = conn.cursor()
    c.execute('SELECT servant_id FROM view_history ORDER BY updated_at DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_recent_servants_history(limit=10):
    """履歴にあるサーヴァントの詳細情報を取得"""
    ids = get_recent_servant_ids(limit)
    if not ids:
        return []
    
    # 既存の検索機能などはIDリスト指定に対応していないため、単純にループで取得するか、IN句で取得する
    # 順番を維持したいので、個別に取得してリストにするのが確実（件数少ないし）
    # または IN 句で取得してから Python 側でソート
    
    results = []
    
    # 一括取得用SQL
    if not ids:
        return []
        
    conn = get_db_connection()
    if not conn:
        return []
        
    placeholders = ','.join(['?'] * len(ids))
    sql = f"""
        SELECT id, collection_no, name, class_name, rarity, face_url, json_data 
        FROM servants 
        WHERE id IN ({placeholders})
    """
    
    cursor = conn.cursor()
    cursor.execute(sql, tuple(ids))
    columns = [desc[0] for desc in cursor.description]
    raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    
    # 辞書にしてIDアクセスできるようにする
    res_map = {row['id']: row for row in raw_results}
    
    # マシュの特別対応 (ID 800100 -> 800101/800102 のマッピングが履歴にあるかどうか)
    # 履歴には 800101 とかが入るかもしれない。
    # raw_results は物理DBのID (800100) しか持たないかもしれない。
    # もし履歴に 800101 があったら、物理DBから 800100 を取ってきて変換が必要
    
    # Mash Handling Logic Re-use or Simplified?
    # search_servants logic is complex specifically for Mash filtering.
    # Here we just want to display them.
    # Let's use get_servant_detail logic but simplified for list view?
    # Or just use the raw data and let the template handle basic display?
    # Template uses: face_url, name, class_name, rarity.
    
    final_results = []
    for rid in ids:
        # Check if direct hit
        if rid in res_map:
            final_results.append(translate_row(res_map[rid]))
        else:
            # Maybe it's a Mash variant ID?
            # If rid is 800101 or 800102, we need 800100 data
            if rid in [800101, 800102]:
                # Find 800100 in results?
                row = res_map.get(800100)
                if not row:
                   # Try separate fetch if not in batch (shouldn't happen if 800100 was not in ids)
                   # Wait, if I viewed 800101, ids has 800101. SQL 'WHERE id IN (800101)' fails.
                   # So we need to fetch 800100 if 800101/02 is in ids.
                   pass
            
            # Re-fetch missing IDs mapping to 800100
            real_id = rid
            if rid in [800101, 800102]:
                real_id = 800100
            
            if real_id != rid and real_id in res_map:
                # We have the base data, need to augment it like search_servants does
                base_row = res_map[real_id].copy() # Copy!
                
                if rid == 800101:
                    base_row['id'] = 800101
                    base_row['name'] = "マシュ (オルテナウス)"
                    base_row['class_name'] = "shielder_ortinax"
                    if base_row.get('face_url'):
                         base_row['face_url'] = base_row['face_url'].replace('800100', '800150').replace('status/0', 'status/800150')
                elif rid == 800102:
                    base_row['id'] = 800102
                    base_row['name'] = "マシュ (パラディーン)"
                    base_row['class_name'] = "shielder_paladin"
                    base_row['rarity'] = 5
                    if base_row.get('face_url'):
                         base_row['face_url'] = base_row['face_url'].replace('800100', '800200').replace('status/0', 'status/800200')
                
                final_results.append(translate_row(base_row))
                continue
                
            # If still not found (maybe data deletion?), skip
            pass
            
    # For Mash variants to work, we need to ensure 800100 is fetched if 800101/102 is requested.
    # Improved Batch Fetch:
    req_ids = set()
    for i in ids:
        if i in [800101, 800102]:
            req_ids.add(800100)
        else:
            req_ids.add(i)
            
    # Re-run query if needed (or just structurally fix above logic)
    # Let's rewrite the query part properly.
    if not req_ids:
        return []
        
    conn = get_db_connection()
    placeholders = ','.join(['?'] * len(req_ids))
    sql = f"SELECT id, collection_no, name, class_name, rarity, face_url, json_data FROM servants WHERE id IN ({placeholders})"
    cursor = conn.cursor()
    cursor.execute(sql, tuple(req_ids))
    columns = [desc[0] for desc in cursor.description]
    raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    
    res_map = {row['id']: row for row in raw_results}
    
    final_output = []
    for rid in ids:
        target_id = rid
        if rid in [800101, 800102]:
            target_id = 800100
            
        if target_id in res_map:
            row = res_map[target_id].copy()
            
            # Apply Mash Transforms if needed
            if rid == 800101:
                row['id'] = 800101
                row['name'] = "マシュ (オルテナウス)"
                row['class_name'] = "shielder" # Icon display logic handles shielder?
                # search_servants uses 'shielder_ortinax' for filtering, but 'shielder' might be better for icon mapping?
                # CLASS_NAME_JP entries: 'shielder_ortinax': 'シールダー'
                # So it's safe to use specific key if 'translate_row' handles it.
                row['class_name'] = "shielder_ortinax"
                if row.get('face_url'):
                     row['face_url'] = row['face_url'].replace('800100', '800150').replace('status/0', 'status/800150')
            elif rid == 800102:
                row['id'] = 800102
                row['name'] = "マシュ (パラディーン)"
                row['class_name'] = "shielder_paladin"
                row['rarity'] = 5
                if row.get('face_url'):
                     row['face_url'] = row['face_url'].replace('800100', '800200').replace('status/0', 'status/800200')
            
            final_output.append(translate_row(row))
            
    return final_output


def get_db_connection():
    """データベース接続を取得する"""
    if not os.path.exists(DB_FILENAME):
        return None
    
    conn = sqlite3.connect(DB_FILENAME)
    conn.row_factory = sqlite3.Row  # カラム名でアクセスできるようにする
    return conn

def get_last_updated_time():
    """データベースの最終更新日時を取得する"""
    conn = get_db_connection()
    if not conn:
        return "未更新"
    
    cursor = conn.cursor()
    try:
        # _meta_infoテーブルがあるか確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_meta_info'")
        if not cursor.fetchone():
            return "未更新"

        cursor.execute("SELECT MAX(updated_at) as last_updated FROM _meta_info")
        row = cursor.fetchone()
        if row and row['last_updated']:
            # ISO format to readable string
            # 2024-01-01T12:00:00.123 -> 2024-01-01 12:00
            ts = row['last_updated']
            try:
                import datetime
                dt = datetime.datetime.fromisoformat(ts)
                return dt.strftime('%Y-%m-%d %H:%M')
            except:
                return ts
        return "未更新"
    except Exception as e:
        return f"エラー: {e}"
    finally:
        conn.close()

# 翻訳マッピング
CLASS_NAME_JP = {
    "saber": "セイバー", "archer": "アーチャー", "lancer": "ランサー",
    "rider": "ライダー", "caster": "キャスター", "assassin": "アサシン",
    "berserker": "バーサーカー", "shielder": "シールダー", "ruler": "ルーラー",
    "avenger": "アヴェンジャー", "moonCancer": "ムーンキャンサー", "alterEgo": "アルターエゴ",
    "foreigner": "フォーリナー", "pretender": "プリテンダー", "beast": "ビースト",
    "shielder_paladin": "シールダー",
    "shielder_ortinax": "シールダー",
    "unBeastOlgaMarie": "アンビースト",
    "beastEresh": "ビースト"
}

ATTRIBUTE_JP = {
    "sky": "天", "earth": "地", "human": "人", "star": "星", "beast": "獣"
}

TRAIT_JP = {
    # 性別
    "genderFemale": "女性", "genderMale": "男性", "genderUnknown": "性別不詳",
    # 属性
    "sky": "天", "earth": "地", "human": "人", "star": "星", "beast": "獣",
    # クラス
    "saber": "セイバー", "archer": "アーチャー", "lancer": "ランサー", "rider": "ライダー", 
    "caster": "キャスター", "assassin": "アサシン", "berserker": "バーサーカー", 
    "shielder": "シールダー", "ruler": "ルーラー", "avenger": "アヴェンジャー", 
    "moonCancer": "ムーンキャンサー", "alterEgo": "アルターエゴ", "foreigner": "フォーリナー", 
    "pretender": "プリテンダー",
    # 共通特性
    "servant": "サーヴァント", "humanoid": "人型", "dragon": "竜", "divine": "神性", 
    "demon": "悪魔", "demonic": "魔性", "undead": "死霊", "giant": "巨人", "king": "王",
    "roman": "ローマ", "greekMythologyMales": "ギリシャ神話男性", "argonau": "アルゴノーツ",
    "arthur": "アーサー", "knightsOfTheRound": "円卓の騎士", "riding": "騎乗", "territoryCreation": "陣地作成",
    "madnessEnhancement": "狂化", "independentAction": "単独行動", "presenceConcealment": "気配遮断",
    "threatToHumanity": "人類の脅威"
    # 不要な内部特性は除外するためマッピング定義しない
    # "fgo", "canBeInBattle", "unknown", "servant", "class*", "attribute*", etc...
}

def translate_row(row_dict):
    """行データの英語を日本語に変換する"""
    if "class_name" in row_dict:
        c = row_dict["class_name"]
        row_dict["class_name"] = CLASS_NAME_JP.get(c, c) # マッチしない場合はそのまま
    
    if "attribute" in row_dict:
        a = row_dict["attribute"]
        row_dict["attribute"] = ATTRIBUTE_JP.get(a, a)

    # Face URLが空の場合、Atlas AcademyのURLを自動生成
    if "face_url" not in row_dict or not row_dict["face_url"]:
        if "id" in row_dict:
            rid = int(row_dict["id"])
            # Mash Virtual IDs Handling
            if rid == 800101: # Ortinax
                 row_dict["face_url"] = "https://static.atlasacademy.io/JP/Faces/f_8001500.png"
            elif rid == 800102: # Paladin
                 row_dict["face_url"] = "https://static.atlasacademy.io/JP/Faces/f_8002000.png"
            else:
                # 基本再臨(セイントグラフ)のURLを生成
                # ID + 0 (例: 100100 -> f_1001000)
                row_dict["face_url"] = f"https://static.atlasacademy.io/JP/Faces/f_{row_dict['id']}0.png"
        
    return row_dict

def filter_ce_advanced(row, data, filters):
    """
    高度なCE検索フィルターロジック
    row: DB Row (dict access)
    data: JSON parsed data
    filters: list of filter strings
    Return: True if matches, False otherwise
    """
    if not filters:
        return True
    
    # フィルタカテゴリの分類
    req_np_charge = [] 
    req_stats = [] 
    req_tactics = [] 
    req_traits = [] 
    req_bonus = [] 
    req_cost = [] 
    req_rarity = [] 
    
    for f in filters:
        if f.startswith('np_'): req_np_charge.append(f)
        elif f.startswith('stat_'): req_stats.append(f)
        elif f.startswith('tac_'): req_tactics.append(f)
        elif f.startswith('trait_'): req_traits.append(f)
        elif f.startswith('bonus_'): req_bonus.append(f)
        elif f.startswith('cost_'): req_cost.append(int(f.replace('cost_', '')))
        elif f.startswith('rarity_'): req_rarity.append(int(f.replace('rarity_', '')))

    # --- 1. NP Charge ---
    if req_np_charge:
        charge_val = 0
        skills = data.get('skills', [])
        for skill in skills:
            for func in skill.get('functions', []):
                if func.get('funcType') == 'gainNp':
                    for sval in func.get('svals', []):
                        if 'Value' in sval:
                            try:
                                val = int(sval['Value'])
                                if val > charge_val:
                                    charge_val = val
                            except:
                                pass
        
        matched_np = False
        for req in req_np_charge:
            if req == 'np_100':
                if charge_val >= 10000: matched_np = True 
            elif req == 'np_80plus':
                if charge_val >= 8000: matched_np = True
            elif req == 'np_50plus':
                if charge_val >= 5000: matched_np = True
            elif req == 'np_charge_exist': 
                if charge_val > 0: matched_np = True
        
        if not matched_np:
            return False

    # --- 2. Stats ---
    if req_stats:
        hp = row['hp_max']
        atk = row['atk_max']
        matched_stat = False
        
        for req in req_stats:
            if req == 'stat_atk': 
                if atk > 0 and hp == 0: matched_stat = True
            elif req == 'stat_hp':
                if hp > 0 and atk == 0: matched_stat = True
            elif req == 'stat_balance':
                if hp > 0 and atk > 0: matched_stat = True
        
        if not matched_stat:
            return False

    # --- 3. Tactics & Traits (Text Search) ---
    detail_text = row.get('detail')
    if not detail_text and data:
        # Fallback to JSON skill[0].detail
        try:
            if 'skills' in data and data['skills']:
                detail_text = data['skills'][0].get('detail', '')
        except:
            pass
            
    text = (detail_text or "") + (row['name'] or "")
    
    if req_tactics:
        matched_tac = False
        for req in req_tactics:
            if req == 'tac_ignore_def':
                if '防御無視' in text: matched_tac = True
            elif req == 'tac_taunt':
                if 'ターゲット集中' in text: matched_tac = True
            elif req == 'tac_on_death':
                if '退場時' in text: matched_tac = True
            elif req == 'tac_demerit':
                if 'デメリット' in text or '減少' in text or 'ダウン' in text: 
                    if '【デメリット】' in text or 'HPが減少' in text or '防御力がダウン' in text:
                        matched_tac = True
            elif req == 'tac_oc_up':
                 if 'チャージ段階' in text and '上げる' in text: matched_tac = True

        if not matched_tac:
            return False

    # --- 4. Traits ---
    if req_traits:
        matched_trait = False
        for req in req_traits:
            key = req.replace('trait_', '')
            keywords = []
            if key == 'divine': keywords = ['神性']
            elif key == 'humanoid': keywords = ['人型']
            elif key == 'dragon': keywords = ['竜']
            elif key == 'demonic': keywords = ['魔性']
            elif key == 'undead': keywords = ['死霊']
            elif key == 'king': keywords = ['王']
            
            for k in keywords:
                if f"〔{k}〕特攻" in text:
                    matched_trait = True
                    break
        
        if not matched_trait:
            return False

    # --- 5. Bonus ---
    if req_bonus:
        matched_bonus = False
        for req in req_bonus:
            if req == 'bonus_bond':
                # "絆" included. Check for "獲得量" OR "得られる" OR "増やす"
                # Many Bond CEs: "クエストクリア時に得られる絆ポイントを...増やす"
                if '絆' in text and ('獲得量' in text or '増やす' in text or '得られる' in text or (row['cost'] == 9 and row['rarity'] == 4)):
                     matched_bonus = True
            elif req == 'bonus_exp':
                 if '経験値' in text or 'EXP' in text: matched_bonus = True
            elif req == 'bonus_qp':
                 # Mona Lisa: "得られるQPを...増やす"
                 if 'QP' in text and ('獲得量' in text or '増やす' in text or '得られる' in text): matched_bonus = True
        
        if not matched_bonus:
            return False

    # --- 6. Card Type ---
    req_cards = [f for f in filters if f in ['Arts', 'Buster', 'Quick']]
    if req_cards:
        matched_card = False
        for c in req_cards:
             # Check detail text for "Arts card performance" etc.
             if f"{c}カード性能" in text or f"{c}性能" in text:
                 matched_card = True
        
        if not matched_card:
            return False

    return True


def search_craft_essences(query=None, filters=None, limit=100):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    
    sql = "SELECT * FROM craft_essences WHERE 1=1"
    params = []
    
    if query:
        keywords = query.split()
        for kw in keywords:
            sql += " AND (name LIKE ? OR detail LIKE ?)"
            params.append(f'%{kw}%')
            params.append(f'%{kw}%')


    # まず候補を取得
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    results = []
    
    for i, row in enumerate(rows):
        row_dict = dict(row)
        
        # JSON Parse
        try:
            data = json.loads(row_dict['json_data']) if row_dict.get('json_data') else {}
        except:
            data = {}
            
        # Advanced Filtering in Python
        if filters:
            if not filter_ce_advanced(row_dict, data, filters):
                continue
        
        # Basic Filters (Integrated into filter_ce_advanced)
        # if filters:
        #    req_cards... (Removed)
            
        # Display Data Generation
        
        # Display Data Generation
        # 1. Icon URL (CharaGraph for CE)
        if row_dict.get("id"):
           row_dict["icon_url"] = f"https://static.atlasacademy.io/JP/CharaGraph/{row_dict['id']}/{row_dict['id']}a.png"
        else:
           row_dict["icon_url"] = row_dict.get("face_url")

        # 2. Effect Description
        effect = ""
        try:
            if data and "skills" in data and len(data["skills"]) > 0:
                effect = data["skills"][0].get("detail", "")
        except:
            pass
        if not effect:
             effect = row_dict.get('detail', '') # Fallback
        row_dict["effect"] = effect

        results.append(translate_row(row_dict))
        if len(results) >= limit:
            break
            
    return results

def search_servants(query=None, filters=None, limit=100):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    
    # We always need json_data for NP filtering
    # Use GROUP BY collection_no to prevent duplicates
    # Filter id < 9000000 to remove obvious enemy/boss entries (common heuristic)
    sql = """
        SELECT id, collection_no, name, class_name, rarity, face_url, json_data 
        FROM servants 
        WHERE (collection_no > 0 OR id IN (3300200, 4000100)) AND id < 9000000
    """
    params = []
    
    if query:
        # Split by whitespace (full-width/half-width handled by default split)
        keywords = query.split()
        for kw in keywords:
            sql += " AND name LIKE ?"
            params.append(f'%{kw}%')

    # SQL Filtering based on filters
    if filters:
        jp_to_db_class = {
            'セイバー': 'saber', 'アーチャー': 'archer', 'ランサー': 'lancer', 
            'ライダー': 'rider', 'キャスター': 'caster', 'アサシン': 'assassin', 'バーサーカー': 'berserker',
            'シールダー': 'shielder', 'ルーラー': 'ruler', 'アヴェンジャー': 'avenger', 
            'ムーンキャンサー': 'moonCancer', 'アルターエゴ': 'alterEgo', 'フォーリナー': 'foreigner', 
            'プリテンダー': 'pretender', 'ビースト': 'beast',
            'シールダーパラディーン': 'shielder_paladin',
            'シールダーオルテナウス': 'shielder_ortinax',
            'アンビースト': 'unBeastOlgaMarie'
        }
        
        req_classes = []
        req_rarity = []
        
        for f in filters:
            if f in jp_to_db_class:
                req_classes.append(jp_to_db_class[f])
            elif isinstance(f, int) or (isinstance(f, str) and f.isdigit()):
                # Rarity Filter
                r = int(f)
                if 0 <= r <= 5:
                    req_rarity.append(r)
        
        # MASH SPECIAL HANDLING: 
        # If Shielder Variants requested, MUST query 'shielder' to fetch ID 800100
        sql_classes = req_classes.copy()
        if 'shielder_paladin' in sql_classes or 'shielder_ortinax' in sql_classes:
             if 'shielder' not in sql_classes:
                  sql_classes.append('shielder')
                  
        # BEAST SPECIAL HANDLING:
        # If 'beast' is requested, also include 'beastEresh' (Space Ereshkigal)
        if 'beast' in sql_classes:
             if 'beastEresh' not in sql_classes:
                 sql_classes.append('beastEresh')
                 
        if sql_classes:
            placeholders = ','.join(['?'] * len(sql_classes))
            sql += f" AND class_name IN ({placeholders})"
            params.extend(sql_classes)
            
        if req_rarity:
            placeholders = ','.join(['?'] * len(req_rarity))
            sql += f" AND rarity IN ({placeholders})"
            params.extend(req_rarity)

    # Ensure collection_no is treated as integer for grouping
    sql += " GROUP BY CAST(collection_no AS INTEGER) ORDER BY CAST(collection_no AS INTEGER) ASC"
    
    # Increase limit if filtering, or keep distinct?
    # If filtering by class, 100 is fine.
    
    cursor.execute(sql, tuple(params))
    columns = [desc[0] for desc in cursor.description]
    raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    
    # Pre-process raw_results to split Mash (800100)
    processed_rows = []
    for row in raw_results:
        if row['id'] == 800100:
            # 1. Ortinax (800101)
            ortinax = row.copy()
            ortinax['id'] = 800101
            ortinax['name'] = "マシュ (オルテナウス)"
            ortinax['class_name'] = "shielder" # Or distinct class? User asked for filtering.
            # Let's use custom class for filtering visibility if needed, or keep shielder.
            # User previously asked for Shielder Paladin class.
            ortinax['class_name'] = "shielder_ortinax" # I'll add this to map
            
            # 2. Paladin (800102)
            paladin = row.copy()
            paladin['id'] = 800102
            paladin['name'] = "マシュ (パラディーン)"
            paladin['class_name'] = "shielder_paladin"
            
            # Prepare Data Filtering (Miniature version for search)
            try:
                # Shared Index Constants
                # User Protocol 2026 Updates:
                # Ortinax: Black Barrel B(8), Amalgam D(7), Paradox C(9)
                idx_ortinax = [8, 7, 9]
                # Paladin: Snowflakes B(10), Chalk A(11), Resolution A(12)
                idx_paladin = [10, 11, 12] 
                
                # Base Exclusions: Remove Ortinax/Paladin specific skills + Bunker Bolt(5) + Tragic(4)?
                # Base should usually keep 0, 1, 2, 3 (Part 1 Upgrade).
                # Exclude 4,5,6,7,8,9,10,11,12.
                idx_exclude_from_base = [4, 5, 6, 7, 8, 9, 10, 11, 12]
                
                # NP Indices Update:
                # Ortinax: Index 3 (Now Fragile...)
                # Paladin: Index 8 (Building Hope...) + Index 6 (Evidencing Hope - Buster)
                idx_np_ortinax = 3
                
                # Ortinax Data
                o_data = json.loads(ortinax['json_data'])
                if 'noblePhantasms' in o_data and len(o_data['noblePhantasms']) > idx_np_ortinax:
                     o_data['noblePhantasms'] = [o_data['noblePhantasms'][idx_np_ortinax]]
                # Ortinax Skills
                o_skills = o_data.get('skills', [])
                o_data['skills'] = [s for i, s in enumerate(o_skills) if i in idx_ortinax]
                
                if ortinax.get('face_url'):
                    ortinax['face_url'] = ortinax['face_url'].replace('800100', '800150').replace('status/0', 'status/800150')
                ortinax['json_data'] = json.dumps(o_data)
                
                # Paladin Data
                # Rarity 5, Cost 16
                paladin['rarity'] = 5
                paladin['cost'] = 16
                
                p_data = json.loads(paladin['json_data'])
                p_nps = p_data.get('noblePhantasms', [])
                # Paladin has NP 8 and 6
                p_selected_nps = []
                if len(p_nps) > 8: p_selected_nps.append(p_nps[8])
                if len(p_nps) > 6: p_selected_nps.append(p_nps[6])
                p_data['noblePhantasms'] = p_selected_nps
                
                # Paladin Skills
                p_skills = p_data.get('skills', [])
                p_data['skills'] = [s for i, s in enumerate(p_skills) if i in idx_paladin]

                if paladin.get('face_url'):
                    paladin['face_url'] = paladin['face_url'].replace('800100', '800200').replace('status/0', 'status/800200')
                paladin['json_data'] = json.dumps(p_data)
                
                # Normal Data
                n_data = json.loads(row['json_data'])
                if 'noblePhantasms' in n_data:
                    nps = n_data['noblePhantasms']
                    # Keep only non-special NPs. Exclude Ortinax(3), Paladin(8,6)
                    # Base Exclusions: 3, 6, 8. (Also 4, 5, 7, 9, 10, 11, 12?)
                    # Base should keep 1, 2, 4? No, user says Base is "Lord Chaldeas". Index 2 "Now Far Ideal Castle"? 
                    # User Protocol: "1.4 NP: Lord Chaldeas (Arts) Rank D (Enhanced)". 
                    # Dump: Index 1: "Virtual NP...", Index 2: "Now Far Ideal..."
                    # We should probably keep 1 and 2 for Base. Exclude 3, 6, 8.
                    # Index 4, 5, 7 are Ortinax/Paladin copies?
                    # Dump: 4="Now Exists Dream Castle", 5="Hope Building". 
                    # Let's exclude strictly: 3, 4, 5, 6, 7, 8.
                    filtered_nps = [n for i, n in enumerate(nps) if i not in [3, 4, 5, 6, 7, 8]]
                    n_data['noblePhantasms'] = filtered_nps
                    
                    # Normal Skills
                    n_skills = n_data.get('skills', [])
                    n_data['skills'] = [s for i, s in enumerate(n_skills) if i not in idx_exclude_from_base]
                    
                row['json_data'] = json.dumps(n_data)
                
            except:
                pass
            
            processed_rows.append(row)
            processed_rows.append(ortinax)
            processed_rows.append(paladin)
        else:
            processed_rows.append(row)
            
    raw_results = processed_rows

    # Python-side filtering & Deduplication
    results = []
    seen_ids = set()
    
    for row in raw_results:
        # Deduplication check
        if row['id'] in seen_ids:
            continue
            
        # Base filter object
        keep = True
        
        # Parse JSON primarily for NP info
        data = {}
        try:
            if row.get("json_data"):
                data = json.loads(row["json_data"])
        except:
            pass
            
        # 0. Enemy Filter (Strict)
        # Check 'type' field in JSON
        s_type = data.get('type', 'normal')
        if s_type in ['enemy', 'enemyCollection', 'boss']:
            continue # Skip this row completely
            
        # Check 'flag' if needed? Usually type is enough.
            
        # Extract NP info
        np_cards = set()
        np_types = set()
        
        nps = data.get("noblePhantasms", [])
        if nps:
            for np in nps:
                # 1. Card
                # Card: 'arts', 'buster', 'quick' OR 1, 2, 3
                raw_card = np.get("card")
                card_map = {1: "Arts", 2: "Buster", 3: "Quick"}
                
                c_str = "Unknown"
                try:
                    c_int = int(raw_card)
                    c_str = card_map.get(c_int, "Unknown")
                except (ValueError, TypeError):
                    c_str = str(raw_card).capitalize() if raw_card else "Unknown"
                
                if c_str != "Unknown":
                    np_cards.add(c_str)
                
                # 2. Type
                is_attack = False
                is_aoe = False
                
                if not np.get('functions') and not np.get('detail'):
                    continue
                if np.get('name') == '？？？':
                    continue
                    
                for func in np.get("functions", []):
                    # Lowercase check just in case
                    ftype = func.get("funcType", "")
                    target_team = func.get("funcTargetTeam", "")
                    target_type = func.get("funcTargetType", "")
                    
                    if "damageNp" in ftype:
                        is_attack = True
                        if "enemyAll" in target_type:
                            is_aoe = True
                
                if is_attack:
                    if is_aoe:
                        np_types.add("AoE")
                    else:
                        np_types.add("ST")
                else:
                    np_types.add("Support")
        
        # Default if no NP found
        if not np_types:
            np_types.add("Support")

        # Apply Filters
        if filters:
            # filters is a list of strings
            
            jp_to_db_class = {
                'セイバー': 'saber', 'アーチャー': 'archer', 'ランサー': 'lancer', 
                'ライダー': 'rider', 'キャスター': 'caster', 'アサシン': 'assassin', 'バーサーカー': 'berserker',
                'シールダー': 'shielder', 'ルーラー': 'ruler', 'アヴェンジャー': 'avenger', 
                'ムーンキャンサー': 'mooncancer', 'アルターエゴ': 'alterego', 'フォーリナー': 'foreigner', 
                'プリテンダー': 'pretender', 'ビースト': 'beast',
                'シールダーパラディーン': 'shielder_paladin',
                'シールダーオルテナウス': 'shielder_ortinax',
                'アンビースト': 'unBeastOlgaMarie'
            }
            
            # Categories
            all_cards = ['Buster', 'Arts', 'Quick']
            type_map = {'全体': 'AoE', '単体': 'ST', '補助': 'Support'}
            
            req_classes = []
            req_cards = []
            req_types = []
            
            for f in filters:
                if f in all_cards:
                    req_cards.append(f) 
                elif f in type_map:
                    req_types.append(type_map[f])
                elif f in jp_to_db_class:
                    req_classes.append(jp_to_db_class[f].lower())
                else:
                    pass
            
            
            # (Zombie code removed)

            # 1. Class Check (SQL Generation Helper - Though exact logic is further down, we modify behavior here?)
            # Actually, `search_servants` builds SQL query below this loop using `filters`.
            # But wait, `filters` argument is used directly in `search_servants`? 
            # No, `search_servants` builds query based on `filters`.
            # I need to find where SQL query is built. 
            # It's NOT in this loop. This loop (lines 261-278) parses filters for POST-filtering (lines 282+).
            # The SQL generation is BEFORE this block or AFTER?
            # Looking at previous view, this block is inside "Python-side filtering".
            # The ACTUAL SQL query happens at start of function!
            # I need to edit the START of the function.
            pass
            
            # Check conditions
            
            # 1. Class Check
            if req_classes:
                db_cls = str(row.get('class_name', '')).strip().lower()
                # Special: if 'shielder' requested, accept 'shielder_ortinax' too
                if db_cls == 'shielder_ortinax' and 'shielder' in req_classes:
                    pass # Match
                # Special: if 'beast' requested, accept 'beastEresh' (Space Ereshkigal)
                elif db_cls == 'beasteresh' and 'beast' in req_classes:
                    pass # Match
                elif db_cls not in req_classes:
                    keep = False
            
            # 2. Card Check (Intersection: Has ANY of the requested cards?)
            # Actually, usually filters are inclusive within category (OR)
            # If user checked 'Buster' and 'Arts', and servant has 'Buster', Keep? Yes.
            if req_cards:
                # Check if intersection is non-empty
                if not set(req_cards).intersection(np_cards):
                    keep = False
            
            # 3. Type Check (Intersection: Has ANY of the requested types?)
            if req_types:
                if not set(req_types).intersection(np_types):
                    keep = False
                
        if keep:
            results.append(translate_row(row))
            seen_ids.add(row['id'])
            if len(results) >= limit:
                break
                
    return results

def get_servant_detail(servant_id):
    """サーヴァントの詳細を取得する"""
    conn = get_db_connection()
    if not conn:
        return None
    
    # Mash Handling
    target_id_alias = int(servant_id)
    real_id = servant_id
    if target_id_alias in [800101, 800102]:
        real_id = 800100

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM servants WHERE id = ?", (real_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        servant = dict(row)
        
        # Mash Transformation
        if int(servant['id']) == 800100:
            try:
                data = json.loads(servant["json_data"]) if servant["json_data"] else {}
                
                # Strict Separation Logic (Refined)
                all_skills = data.get('skills', [])
                all_nps = data.get('noblePhantasms', [])
                
                # Skill Indices (Based on Dump):
                # User Protocol 2026:
                # Ortinax: Black Barrel B(8), Amalgam D(7), Paradox C(9)
                idx_ortinax = [8, 7, 9]
                # Paladin: Snowflakes B(10), Chalk A(11), Resolution A(12)
                idx_paladin = [10, 11, 12]
                
                idx_exclude_from_base = [4, 5, 6, 7, 8, 9, 10, 11, 12]
                
                # NP Indices:
                idx_np_ortinax = 3
                
                if target_id_alias == 800101: # ORTINAX
                    servant['id'] = 800101
                    servant['name'] = "マシュ (オルテナウス)"
                    servant['class_name'] = "shielder" 
                    servant['class_name'] = "shielder_ortinax" 
                    
                    # Icon Override
                    if servant.get('face_url'):
                        servant['face_url'] = servant['face_url'].replace('800100', '800150').replace('status/0', 'status/800150')
                    
                    # NP: Only Ortinax NP (Index 3)
                    if len(all_nps) > idx_np_ortinax:
                         data['noblePhantasms'] = [all_nps[idx_np_ortinax]]
                    else:
                         data['noblePhantasms'] = []
                    # Skills: Only Ortinax
                    data['skills'] = [s for i, s in enumerate(all_skills) if i in idx_ortinax]

                elif target_id_alias == 800102: # PALADIN
                    servant['id'] = 800102
                    servant['name'] = "マシュ (パラディーン)"
                    servant['class_name'] = "shielder_paladin"
                    # Stats Override
                    servant['rarity'] = 5
                    servant['cost'] = 16
                    
                    # Icon Override
                    if servant.get('face_url'):
                        servant['face_url'] = servant['face_url'].replace('800100', '800200').replace('status/0', 'status/800200')

                    # NP: Paladin NPs (Index 8 and 6)
                    p_selected_nps = []
                    if len(all_nps) > 8: p_selected_nps.append(all_nps[8])
                    if len(all_nps) > 6: p_selected_nps.append(all_nps[6])
                    data['noblePhantasms'] = p_selected_nps
                         
                    # Skills: Only Paladin
                    data['skills'] = [s for i, s in enumerate(all_skills) if i in idx_paladin]
                    
                else: # BASE (800100)
                    # NP: Exclude Ortinax and Paladin (3, 4, 5, 6, 7, 8)
                    filtered_nps = []
                    for i, n in enumerate(all_nps):
                        if i not in [3, 4, 5, 6, 7, 8]:
                            filtered_nps.append(n)
                    data['noblePhantasms'] = filtered_nps
                    
                    # Skills: Exclude Ortinax AND Paladin
                    data['skills'] = [s for i, s in enumerate(all_skills) if i not in idx_exclude_from_base]
                
                servant["json_data"] = json.dumps(data)
            except Exception as e:
                print(f"Error in Mash Transform: {e}")

        # JSONデータのパースと詳細情報の展開
        if "json_data" in servant and servant["json_data"]:
            try:
                data = json.loads(servant["json_data"])
                
                # スキル情報 (Slotごとにグルーピング)
                raw_skills = data.get("skills", [])
                skill_groups = {}
                for s in raw_skills:
                    num = s.get("num")
                    if num not in skill_groups:
                        skill_groups[num] = []
                    skill_groups[num].append(s)
                
                # Priority順にソートしてリスト化
                servant["skill_slots"] = []
                for num in sorted(skill_groups.keys()):
                    # Priority昇順 (古い -> 新しい)
                    sorted_skills = sorted(skill_groups[num], key=lambda x: x.get("priority", 0))
                    
                    slot_data = []
                    for skill in sorted_skills:
                        slot_data.append({
                            "name": skill.get("name", "Unknown"),
                            "icon": skill.get("icon"), 
                            "coolDown": skill.get("coolDown", []),
                            "detail": skill.get("detail", "")
                        })
                    servant["skill_slots"].append(slot_data)

                # 宝具情報 (Slotごとにグルーピング、基本は1つだが強化で増える)
                raw_nps = data.get("noblePhantasms", [])
                np_groups = {}
                for n in raw_nps:
                    num = n.get("num")
                    if num not in np_groups:
                        np_groups[num] = []
                    np_groups[num].append(n)
                
                servant["np_slots"] = []
                # Card Map for int -> str
                card_map = {1: "Arts", 2: "Buster", 3: "Quick"}
                
                for num in sorted(np_groups.keys()):
                    sorted_nps = sorted(np_groups[num], key=lambda x: x.get("priority", 0))
                    
                    slot_data = []
                    for np in sorted_nps:
                        raw_card = np.get("card", "Unknown")
                        card_str = "Unknown"
                        if isinstance(raw_card, int):
                            card_str = card_map.get(raw_card, "Unknown")
                        else:
                             card_str = str(raw_card).upper()
                        
                        # Hit Count (Size of distribution array)
                        dist = np.get("npDistribution", [])
                        hit_count = len(dist) if dist else 0

                        slot_data.append({
                            "name": np.get("name", "Unknown"),
                            "type": card_str,
                            "rank": np.get("rank", ""),
                            "detail": np.get("detail", ""),
                            "np_gain": np.get("npGain", {}),
                            "hits": hit_count
                        })
                    servant["np_slots"].append(slot_data)
                
                # Hidden Parameters Extraction (TCA v3.0)
                # 1. Attribute (Ten/Chi/Jin)
                servant["attribute"] = data.get("attribute", "earth") # Default to Earth if missing
                
                # 2. Hit Counts (Distribution)
                # format in JSON: "hits": {"buster": [10, 20, 70], "arts": ...} OR "hits": {"buster": 3, ...} 
                # usually it's a list of per-hit percentages.
                raw_hits = data.get("hits", {})
                processed_hits = {}
                for card, hit_data in raw_hits.items():
                    # If list, length is hit count. If int, it's hit count.
                    if isinstance(hit_data, list):
                        processed_hits[card] = len(hit_data)
                    else:
                        processed_hits[card] = hit_data
                servant["hits_distribution"] = processed_hits
                
                # 3. NP Gain (Base)
                # "noblePhantasms" -> "npGain" is per card type? 
                # Usually Servant has a base "atkBase" and "defBase" NP gain.
                # In Atlas data: "noblePhantasms" might override? No. 
                # "noblePhantasms" has "npDistribution"
                # Actually, check "noblePhantasms" list items for specific NP gain?
                # Usually standard gain is stored at servant level? 
                # Atlas JSON usually has "noblePhantasms" containing "npGain" map {"arts": [0.54], ...} which is the servant's base * card mod ??
                # Let's rely on what we did before: servant["np_charge_rate"]
                
                # 隠しステータス
                servant["star_absorb"] = data.get("starAbsorb", 0)
                servant["star_gen"] = data.get("starGen", 0)
                
                # NP獲得率 & 宝具ヒット数 (最新の宝具データを使用)
                if servant["np_slots"] and servant["np_slots"][0]:
                     # 最後の要素(=最新の強化後)を参照
                    latest_np = servant["np_slots"][0][-1]
                    np_gain = latest_np.get("np_gain", {})
                    # Arts Gain (Attack)
                    servant["np_charge_rate"] = np_gain.get("arts", [0])[0] if "arts" in np_gain else 0
                    
                    # NP Hit Count
                    # NP Hit Count is already in np_slots
                else:
                    servant["np_charge_rate"] = "N/A"
                    
                # 特性 (翻訳辞書にあるものだけを表示)
                servant["traits"] = [TRAIT_JP[t["name"]] for t in data.get("traits", []) if "name" in t and t["name"] in TRAIT_JP]

            except Exception as e:
                # print(f"JSON Error: {e}")
                pass

        return translate_row(servant)
    return None


def search_command_codes(query=None, filters=None, limit=50):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    
    conditions = ["collection_no > 0"]
    params = []
    
    if query:
        conditions.append("(name LIKE ? OR json_data LIKE ?)")
        params.extend([f'%{query}%', f'%{query}%'])
        
    if filters:
        for f in filters:
            conditions.append("json_data LIKE ?")
            params.append(f'%{f}%')

    where_clause = " AND ".join(conditions)

    # We need json_data to extract the description
    sql = f"""
        SELECT id, collection_no, name, rarity, face_url, json_data 
        FROM command_codes 
        WHERE {where_clause}
        ORDER BY collection_no DESC 
        LIMIT ?
    """
    params.append(limit)
    
    cursor.execute(sql, tuple(params))
    
    columns = [desc[0] for desc in cursor.description]
    raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    
    results = []
    for row in raw_results:
        # User requested CC Illustration
        # Correct path: https://static.atlasacademy.io/JP/CommandCodes/c_{id}.png
        if row.get("id"):
           row["icon_url"] = f"https://static.atlasacademy.io/JP/CommandCodes/c_{row['id']}.png"
        else:
           row["icon_url"] = row.get("face_url")

        effect = ""
        try:
            if row.get("json_data"):
                data = json.loads(row["json_data"])
                if "skills" in data and len(data["skills"]) > 0:
                    effect = data["skills"][0].get("detail", "")
        except:
            pass
            
        row["effect"] = effect
        del row["json_data"]
        results.append(row)
        
    return results

def search_materials(query=None, limit=100):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    
    if query:
        sql = """
            SELECT id, name, icon_url 
            FROM items 
            WHERE name LIKE ? 
            ORDER BY id DESC 
            LIMIT ?
        """
        cursor.execute(sql, (f'%{query}%', limit))
    else:
        sql = """
            SELECT id, name, icon_url 
            FROM items 
            ORDER BY id DESC 
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
    
    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return results
