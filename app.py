from flask import Flask, render_template, request, jsonify
import database
import strategy
import db_builder
import os
import webbrowser
import json
import sys
import shutil

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

app = Flask(__name__, template_folder=resource_path('templates'), static_folder=resource_path('static'))

SETTINGS_FILE = 'settings.json'
DB_FILE = 'fgo_full_data_jp.db'

def initialize_db_if_missing():
    # CWDにDBが無い場合、バンドルされたDBをコピーする
    if not os.path.exists(DB_FILE):
        bundled_db = resource_path(DB_FILE)
        if os.path.exists(bundled_db) and bundled_db != os.path.abspath(DB_FILE):
            try:
                print(f"Initializing database from bundle: {bundled_db} -> {DB_FILE}")
                shutil.copy2(bundled_db, DB_FILE)
            except Exception as e:
                print(f"Failed to copy bundled DB: {e}")

initialize_db_if_missing()

def load_settings():

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"master_name": "マスター"}

def save_settings(data):
    current = load_settings()
    current.update(data)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(current, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """ダッシュボード（トップページ）"""
    # 最新のサーヴァント数名を表示するなどで賑やかし -> 直近でステータス画面を開いた１０キャラクターを表示
    recent_servants = database.get_recent_servants_history(limit=10)
    settings = load_settings()
    return render_template('index.html', recent_servants=recent_servants, master_name=settings.get('master_name', 'マスター'))

@app.route('/search')
def search():
    """検索ページ & API"""
    query = request.args.get('q', '')
    if query:
        results = database.search_servants(query)
        # AJAXリクエストならJSONを返す
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(results)
    else:
        results = []
        
    return render_template('search.html', query=query, results=results)

@app.route('/servant/<int:servant_id>')
def servant_detail(servant_id):
    """サーヴァント詳細"""
    servant = database.get_servant_detail(servant_id)
    if not servant:
        return "Servant not found", 404
    database.log_servant_view(servant_id)
    return render_template('detail.html', servant=servant)

@app.route('/strategy')
def strategy_room():
    """AI攻略相談室"""
    return render_template('strategy.html')

@app.route('/servants')
def servant_list():
    """サーヴァント一覧"""
    query = request.args.get('q', '')
    filters = request.args.getlist('filters')
    
    # 検索条件がない場合は結果を返さない（初期表示は空）
    if not query and not filters:
        results = []
    else:
        results = database.search_servants(query, filters=filters, limit=100)
    
    return render_template('list_servant.html', results=results, query=query, current_filters=filters)

@app.route('/craft_essences')
def ce_list():
    """概念礼装一覧"""
    query = request.args.get('q', '')
    filters = request.args.getlist('filters')

    if not query and not filters:
         results = []
    else:
         results = database.search_craft_essences(query, filters=filters, limit=100)
    
    return render_template('list_ce.html', results=results, query=query, current_filters=filters)

@app.route('/command_codes')
def cc_list():
    """コマンドコード一覧"""
    query = request.args.get('q', '')
    filters = request.args.getlist('filters')
    results = database.search_command_codes(query, filters=filters, limit=100)
    return render_template('list_cc.html', results=results, query=query, current_filters=filters)

@app.route('/materials')
def material_list():
    """素材一覧"""
    query = request.args.get('q', '')
    results = database.search_materials(query, limit=100)
    return render_template('list_material.html', results=results, query=query)

@app.route('/settings')
def settings_page():
    """設定ページ"""
    settings = load_settings()
    last_updated = database.get_last_updated_time()
    # API key should generally not be sent back fully if sensitive, but for local app it's fine/convenient
    return render_template('settings.html', 
                          master_name=settings.get('master_name', ''),
                          api_key=settings.get('gemini_api_key', ''),
                          last_updated=last_updated)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """チャットAPI"""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify(error="No message provided"), 400
        
    # Gemini APIを呼び出し
    settings = load_settings()
    api_key = settings.get('gemini_api_key')
    
    reply = strategy.get_strategy_advice(user_message, api_key=api_key)
    return jsonify(reply=reply)

@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    # Validation?
    save_settings(data)
    return jsonify(status="success")

@app.route('/api/update_database', methods=['POST'])
def update_database():
    """データベース更新API"""
    try:
        logs = db_builder.run_update()
        return jsonify(status="success", logs=logs)
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

if __name__ == '__main__':
    # アプリ起動時にブラウザを自動で開く
    # (デバッグモードがオンだと2回開かれることがあるので注意)
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open("http://127.0.0.1:5000")
        
    app.run(debug=True)
