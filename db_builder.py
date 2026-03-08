import requests
import sqlite3
import json
import os
import time
import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

# SSL警告を抑制
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 設定 ---
DB_FILENAME = "fgo_full_data_jp.db"
CACHE_DIR = "cache"

# 取得するデータの定義
DATA_SOURCES = [
    {
        "name": "サーヴァント",
        "url": "https://api.atlasacademy.io/export/JP/nice_servant.json",
        "table": "servants",
        "type": "servant"
    },
    {
        "name": "概念礼装",
        "url": "https://api.atlasacademy.io/export/JP/nice_equip.json",
        "table": "craft_essences",
        "type": "equip"
    },
    {
        "name": "コマンドコード",
        "url": "https://api.atlasacademy.io/export/JP/nice_command_code.json",
        "table": "command_codes",
        "type": "basic"
    },
    {
        "name": "魔術礼装 (マスタースキル)",
        "url": "https://api.atlasacademy.io/export/JP/nice_mystic_code.json",
        "table": "mystic_codes",
        "type": "basic"
    },
    {
        "name": "アイテム・素材",
        "url": "https://api.atlasacademy.io/export/JP/nice_item.json",
        "table": "items",
        "type": "item"
    },
    {
        "name": "クエスト・シナリオ (War)",
        "url": "https://api.atlasacademy.io/export/JP/nice_war.json",
        "table": "wars",
        "type": "basic" 
    }
]

def ensure_cache_dir():
    """キャッシュディレクトリを作成"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_retry_session():
    """リトライ機能付きのセッションを作成"""
    session = requests.Session()
    retries = Retry(
        total=3, backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_meta_info(conn, url):
    """DBから保存済みのETag/Last-Modifiedを取得"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT etag, last_modified FROM _meta_info WHERE url = ?", (url,))
        return cursor.fetchone()
    except sqlite3.Error:
        return None

def update_meta_info(conn, url, etag, last_modified):
    """ETag/Last-Modifiedを更新"""
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute('''
    INSERT OR REPLACE INTO _meta_info (url, etag, last_modified, updated_at)
    VALUES (?, ?, ?, ?)
    ''', (url, etag, last_modified, now))
    conn.commit()

def log_msg(logs, msg):
    """ログリストに追加し、コンソールにも表示"""
    print(msg)
    logs.append(msg)

def compute_diff(old_list, new_list):
    """新旧リストの差分を計算し、更新・追加すべきアイテムのリストを返す"""
    if not old_list:
        return new_list # キャッシュがない場合は全て新規

    # IDをキーにしたマップを作成
    old_map = {item['id']: item for item in old_list if 'id' in item}
    new_map = {item['id']: item for item in new_list if 'id' in item}

    diff_list = []

    for item_id, new_item in new_map.items():
        if item_id not in old_map:
            # 新規追加
            diff_list.append(new_item)
        else:
            # 既存アイテム：内容比較
            # 単純な文字列比較で変更検知 (順序などが変わると検知してしまうが、確実)
            old_item = old_map[item_id]
            if json.dumps(old_item, sort_keys=True) != json.dumps(new_item, sort_keys=True):
                diff_list.append(new_item)
    
    return diff_list

def load_cached_json(filename):
    """キャッシュされたJSONを読み込む"""
    path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_json_cache(filename, data):
    """JSONをキャッシュに保存"""
    ensure_cache_dir()
    path = os.path.join(CACHE_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_json_diff(url, name, table_name, conn, logs):
    """JSONデータを取得し、キャッシュと比較して差分のみを返す"""
    headers = {"User-Agent": "FGO-Full-DB-Builder/2.2"}
    
    # 差分チェック用のヘッダー設定
    meta = get_meta_info(conn, url)
    if meta:
        stored_etag, stored_lm = meta
        if stored_etag:
            headers["If-None-Match"] = stored_etag
        if stored_lm:
            headers["If-Modified-Since"] = stored_lm

    session = get_retry_session()
    
    try:
        response = session.get(url, headers=headers, timeout=(10.0, 180.0))
        
        # 更新なし (304 Not Modified)
        if response.status_code == 304:
            return [], (None, None), False # 差分なし, ヘッダなし, IsUpdated=False

        response.raise_for_status()
        new_data = response.json()
        
        # 新しいヘッダー情報を取得
        new_etag = response.headers.get("ETag")
        new_lm = response.headers.get("Last-Modified")
        
        # キャッシュ読み込み
        cache_filename = f"{table_name}.json"
        old_data = load_cached_json(cache_filename)
        
        # 差分計算
        diff_data = compute_diff(old_data, new_data)
        
        # キャッシュ更新
        save_json_cache(cache_filename, new_data)
        
        return diff_data, (new_etag, new_lm), True # 差分データ, ヘッダ, IsUpdated=True

    except Exception as e:
        log_msg(logs, f"[{name}] ダウンロードまたは処理中にエラー: {e}")
        # フォールバックは今回実装しない（キャッシュ破損防止など複雑になるため）
        return [], (None, None), False

def init_database(conn):
    """全テーブルの作成"""
    cursor = conn.cursor()

    # 0. 管理用テーブル (更新確認用)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS _meta_info (
        url TEXT PRIMARY KEY,
        etag TEXT,
        last_modified TEXT,
        updated_at TEXT
    )''')

    # 1. サーヴァント
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS servants (
        id INTEGER PRIMARY KEY, collection_no INTEGER, name TEXT, class_name TEXT,
        rarity INTEGER, cost INTEGER, hp_max INTEGER, atk_max INTEGER,
        attribute TEXT, alignment TEXT, gender TEXT, face_url TEXT,
        json_data TEXT
    )''')

    # 2. 概念礼装
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS craft_essences (
        id INTEGER PRIMARY KEY, collection_no INTEGER, name TEXT,
        rarity INTEGER, cost INTEGER, hp_max INTEGER, atk_max INTEGER,
        detail TEXT, face_url TEXT, json_data TEXT
    )''')

    # 3. コマンドコード
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS command_codes (
        id INTEGER PRIMARY KEY, collection_no INTEGER, name TEXT,
        rarity INTEGER, face_url TEXT, detail TEXT, json_data TEXT
    )''')

    # 4. アイテム
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY, name TEXT, type TEXT,
        detail TEXT, icon_url TEXT, json_data TEXT
    )''')

    # 5. 魔術礼装
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mystic_codes (
        id INTEGER PRIMARY KEY, name TEXT, detail TEXT, json_data TEXT
    )''')

    # 6. クエスト・War
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wars (
        id INTEGER PRIMARY KEY, name TEXT, age TEXT, json_data TEXT
    )''')

    # 7. クエストドロップ (検索用)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quest_drops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        quest_id INTEGER,
        war_name TEXT,
        quest_name TEXT,
        ap INTEGER,
        drop_rate INTEGER, -- 暫定
        type TEXT,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )''')
    
    # インデックス作成 (検索高速化)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quest_drops_item_id ON quest_drops(item_id)')

    conn.commit()

def rebuild_quest_drops(conn, logs):
    """warsデータからクエストドロップ情報を抽出して別テーブルに構築する"""
    cursor = conn.cursor()
    log_msg(logs, "[quest_drops] ドロップ情報の再構築を開始...")
    
    try:
        # 既存データをクリア
        cursor.execute("DELETE FROM quest_drops")
        
        # Warsからデータを取得
        cursor.execute("SELECT json_data FROM wars")
        rows = cursor.fetchall()
        
        count = 0
        
        for r in rows:
            if not r[0]: continue
            war = json.loads(r[0])
            war_name = war.get('name', 'Unknown')
            
            spots = war.get('spots', [])
            for spot in spots:
                spot_name = spot.get('name', '')
                quests = spot.get('quests', [])
                
                for quest in quests:
                    # フリークエストのみを対象とする（周回用）
                    q_type = quest.get('type')
                    if q_type != 'free':
                        continue
                        
                    quest_id = quest.get('id')
                    quest_name = f"{spot_name} - {quest.get('name')}"
                    ap = quest.get('consume') # 'cost' ではなく 'consume' の場合が多い
                    if ap is None:
                        ap = quest.get('cost')
                        
                    drops = quest.get('drops', [])
                    if not drops:
                        continue
                        
                    for drop in drops:
                        # drop は {"type": "item", "objectId": 123, "num": 1, ...} のような構造
                        d_type = drop.get('type')
                        item_id = drop.get('objectId')
                        
                        if d_type == 'item' and item_id:
                            # 挿入
                            cursor.execute('''
                            INSERT INTO quest_drops (item_id, quest_id, war_name, quest_name, ap, type)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ''', (item_id, quest_id, war_name, quest_name, ap, q_type))
                            count += 1
                            
        conn.commit()
        log_msg(logs, f"[quest_drops] 再構築完了: {count}件のドロップ情報を登録しました")
        
    except Exception as e:
        log_msg(logs, f"[quest_drops] エラー: {e}")
        conn.rollback()

def insert_data(conn, source_def, data, logs):
    """データタイプに応じた挿入処理"""
    cursor = conn.cursor()
    table = source_def["table"]
    dtype = source_def["type"]
    name = source_def["name"]
    
    count = 0
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # クエストドロップ情報の特別処理
        if dtype == "quest_drop_source":
            # War ID -> Name Mapを作成
            cursor.execute("SELECT id, name FROM wars")
            war_map = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 既存のドロップ情報をクリア（全更新）
            cursor.execute("DELETE FROM quest_drops")
            
            for quest in data:
                if quest.get('type') != 'free':
                    continue
                    
                drops = quest.get('drops', [])
                if not drops:
                    continue
                    
                quest_id = quest.get('id')
                # War Name解決 (warIdから)
                war_id = quest.get('warId')
                war_name = war_map.get(war_id, f"War {war_id}")
                
                spot_name = quest.get('spotName', '')
                q_name = quest.get('name', '')
                quest_name = f"{spot_name} - {q_name}" if spot_name else q_name
                
                ap = quest.get('consume')
                if ap is None: ap = quest.get('cost')
                
                for drop in drops:
                    if drop.get('type') == 'item':
                        item_id = drop.get('objectId')
                        
                        cursor.execute('''
                        INSERT INTO quest_drops (item_id, quest_id, war_name, quest_name, ap, type)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (item_id, quest_id, war_name, quest_name, ap, 'free'))
                        count += 1
            
            conn.commit()
            return count

        for item in data:
            item_json = json.dumps(item, ensure_ascii=False)
            
            if dtype == "servant":
                alignments = ",".join(item.get('alignments', [])) if item.get('alignments') else ""
                cursor.execute(f'''
                INSERT OR REPLACE INTO {table} (
                    id, collection_no, name, class_name, rarity, cost,
                    hp_max, atk_max, attribute, alignment, gender, face_url, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('id'), item.get('collectionNo'), item.get('name'), item.get('className'),
                    item.get('rarity'), item.get('cost'), item.get('hpMax'), item.get('atkMax'),
                    item.get('attribute'), alignments, item.get('gender'), item.get('face'),
                    item_json
                ))

            elif dtype == "equip": # 概念礼装
                cursor.execute(f'''
                INSERT OR REPLACE INTO {table} (
                    id, collection_no, name, rarity, cost,
                    hp_max, atk_max, detail, face_url, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('id'), item.get('collectionNo'), item.get('name'),
                    item.get('rarity'), item.get('cost'), item.get('hpMax'), item.get('atkMax'),
                    item.get('detail'), item.get('face'), item_json
                ))

            elif dtype == "item": # アイテム
                cursor.execute(f'''
                INSERT OR REPLACE INTO {table} (
                    id, name, type, detail, icon_url, json_data
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('id'), item.get('name'), item.get('type'),
                    item.get('detail'), item.get('icon'), item_json
                ))
            
            elif dtype == "basic": # 汎用
                i_id = item.get('id')
                i_name = item.get('name', '')
                
                if table == "command_codes":
                    cursor.execute(f'''
                    INSERT OR REPLACE INTO {table} (
                        id, collection_no, name, rarity, face_url, detail, json_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        i_id, item.get('collectionNo'), i_name,
                        item.get('rarity'), item.get('face'), item.get('detail'), item_json
                    ))
                elif table == "wars":
                     cursor.execute(f'''
                    INSERT OR REPLACE INTO {table} (id, name, age, json_data)
                    VALUES (?, ?, ?, ?)
                    ''', (i_id, i_name, item.get('age'), item_json))
                else:
                    cursor.execute(f'''
                    INSERT OR REPLACE INTO {table} (id, name, detail, json_data)
                    VALUES (?, ?, ?, ?)
                    ''', (i_id, i_name, item.get('detail'), item_json))

            count += 1

        conn.commit()
        return count
        
    except sqlite3.Error as e:
        log_msg(logs, f"[{name}] DBエラー: {e}")
        conn.rollback()
        return 0

def run_update():
    """データベース更新を実行し、ログを返す"""
    logs = []
    conn = sqlite3.connect(DB_FILENAME)
    init_database(conn)
    ensure_cache_dir()

    total_updated_items = 0
    updated_tables = []
    
    # 全ソースをチェック
    for source in DATA_SOURCES:
        # 差分取得
        diff_data, header_info, is_updated_from_api = fetch_json_diff(
            source["url"], source["name"], source["table"], conn, logs
        )
        
        if is_updated_from_api:
            # 差分があればDB更新
            if diff_data:
                count = insert_data(conn, source, diff_data, logs)
                if count > 0:
                    updated_tables.append(f"{source['name']}({count}件)")
                    total_updated_items += count
            else:
                # API更新あり・差分なし (メタデータのみ更新など)
                pass
                
            # メタデータ更新
            new_etag, new_lm = header_info
            if new_etag or new_lm:
                update_meta_info(conn, source["url"], new_etag, new_lm)
            
        time.sleep(1)

    # ドロップ情報の再構築 (Warsが更新された場合、またはテーブルが空の場合に走らせるべきだが、
    # 簡易実装として毎回走らせるか、更新があった場合のみにする。
    # ここでは「Warsが更新された」または「QuestDropsが空」のチェックを入れるのが理想だが
    # ユーザーが「再構築」を期待しているので、強制的に走らせる)
    rebuild_quest_drops(conn, logs)

    conn.close()
    
    if updated_tables:
        log_msg(logs, f"更新完了: {', '.join(updated_tables)}")
    else:
        log_msg(logs, "基本データの更新はありませんでした。")
    
    return logs

if __name__ == "__main__":
    run_update()
