import sqlite3
import sys
import os

DB_FILENAME = "fgo_full_data_jp.db"

def search_servant(query_name):
    """データベースからサーヴァントを部分一致検索する"""
    if not os.path.exists(DB_FILENAME):
        print(f"エラー: データベースファイル '{DB_FILENAME}' が見つかりません。")
        print("先に 'FGO Full Database Builder.py' を実行してデータベースを作成してください。")
        return

    try:
        conn = sqlite3.connect(DB_FILENAME)
        cursor = conn.cursor()
        
        # 部分一致検索 (ケースインセンシティブはSQLiteのデフォルト依存だが、LIKEは通常大文字小文字区別なし)
        sql = "SELECT id, collection_no, name, class_name, rarity FROM servants WHERE name LIKE ?"
        cursor.execute(sql, (f'%{query_name}%',))
        results = cursor.fetchall()
        
        conn.close()
        
        if not results:
            print(f"検索結果: '{query_name}' に一致するサーヴァントは見つかりませんでした。")
            return

        print(f"=== 検索結果: '{query_name}' ({len(results)} 件) ===")
        # ヘッダーを表示
        print(f"{'No.':<6} {'クラス':<10} {'レア':<4} {'名前'}")
        print("-" * 50)
        
        for row in results:
            s_id, collection_no, name, class_name, rarity = row
            # collection_noがNoneの場合は0として扱う
            c_no = collection_no if collection_no is not None else 0
            # レア度を☆で表現
            rarity_str = "☆" * rarity if rarity else "-"
            
            print(f"{c_no:<6} {class_name:<10} {rarity_str:<4} {name}")
            
    except sqlite3.Error as e:
        print(f"データベースエラーが発生しました: {e}")

def main():
    if len(sys.argv) < 2:
        print("使用法: python fgo_db_search.py [サーヴァント名]")
        print("例: python fgo_db_search.py アルトリア")
        
        # 引数がない場合は対話モードへ
        while True:
            try:
                query = input("\n検索したいサーヴァント名を入力してください (終了するには 'q' または Enterのみ): ").strip()
                if not query or query.lower() == 'q':
                    print("終了します。")
                    break
                search_servant(query)
            except KeyboardInterrupt:
                print("\n終了します。")
                break
    else:
        # コマンドライン引数がある場合
        query = " ".join(sys.argv[1:])
        search_servant(query)

if __name__ == "__main__":
    main()