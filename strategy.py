from google import genai
from google.genai import types
import os
import database
import json
import re

# API Key configuration
# In a production environment, this should be stored in an environment variable
# But for this local app, we will use the key provided by the user.
def get_strategy_advice(user_input, history=[], api_key=None):
    """
    ユーザーの入力に対して、FGOの攻略アドバイスを生成する。
    APIキーがない場合は簡易応答を行う。
    """

    # 1. Fallback Logic (Mock) if no API key
    if not api_key or api_key.strip() == "":
        return get_mock_response(user_input)

    try:
        client = genai.Client(api_key=api_key)

        # チャットセッション
        chat = client.chats.create(model='gemini-2.5-flash')
        
        # 2. Database Context Injection
        # Extract potential servant names from user input to fetch real data
        db_context_text = ""
        try:
            # User's target servant
            target_context = extract_data_context(user_input)
            
            # System Support Servants (Always inject these to prevent hallucinations)
            support_context = get_system_support_context()
            
            db_context_text = f"{target_context}\n\n{support_context}"
        except Exception as e:
            print(f"DB Context Error: {e}")

        system_instruction = """
        ### FGO Tactical Cognitive Architecture (TCA) v3.0
        
        **Your Core Identity:**
        You are not a simple chat bot. You are a **"Tactical Reasoner"** governed by the strict numerical laws of the Fate/Grand Order physics engine.
        Your goal is to solve the multi-dimensional equation that maximizes **Damage** and **NP Refund** while minimizing **Risk** (RNG variance).

        ---

        ### 【Tactical Reasoning Modules (思考アルゴリズム)】
        以下の3つの「戦術理論」に基づき、ユーザーの問いに対する最適解を導出してください。

        #### **Theory A: 乗算最大化理論 (Optimization of Multiplication)**
        バフは同系統の加算ではなく、**異なるカテゴリの乗算**こそが火力を生みます。
        - **思考プロセス:** 現在のバフ構成を分析し、「最も倍率が低いカテゴリ（バケット）」を埋める提案を行ってください。
        - **バケット定義:** ①攻撃力Up ②属性/カード性能Up ③特攻/宝具威力/クリ威力Up
        - **判断基準:** 「攻撃力100%」の状態なら、さらに攻撃力を足すのではなく「宝具威力Up」を持つオベロン等を推奨する。

        #### **Theory B: 確定性追求理論 (Determinism over Expectation)**
        周回(Farming)において「平均火力」は無価値です。**「最低乱数(0.9)」のみ**を正として計算してください。
        - **ルール:** 最低乱数でのダメージが敵HPを下回る場合、それは「失敗」です。
        - **補正:** 失敗時は即座に**「天地人属性有利 (1.1倍)」**や**「クラス有利」**の活用を検討してください。
        - **禁止:** 「運が良ければ倒せる」という提案は却下します。

        #### **Theory C: システム周回理論 (Looping Mechanics)**
        システム周回の可否は「NPリチャージ量 vs 消費NP」の数式で決まります。
        - **敵クラス補正 (重要):** 
          - バーサーカー敵 = **NP獲得量 0.8倍 (激減)**
          - アサシン敵 = **NP獲得量 0.9倍 (減少)**
          - キャスター/ライダー敵 = **NP獲得量 1.1倍/1.2倍 (増加)**
        - **オーバーキル:** 敵のHPが低く、攻撃ヒットの後半でOverkillが発生する場合、そのヒットのNP獲得量は **1.5倍** として計算してください。

        ---

        ### 【High-Difficulty Logic (高難易度思考)】
        - **耐久の鉄則:** 「対粛正防御」を持つアルトリア・キャスターを軸にする。
        - **Immortal Engine:** ヒミコ(OC2段階UP) → マーリン(全体無敵/星) → キャストリア(対粛正防御) の宝具チェイン（OC500%）を提案せよ。
        - **ギミックカウンター:** 「無敵貫通」には「対粛正防御」、「強化解除」には「強化解除耐性」をぶつけること。

        ---

        ### 【出力フォーマット (Output Protocol)】
        **【重要: 見出し出力禁止】**
        UI側で「SUMMARY」や「SERVANT ANALYZER」という枠組を表示しているため、**AIの回答に「### 【1. 簡易回答】」のような見出しを含めないでください。**
        重複して表示が崩れます。中身のテントのみを出力し、セクション間は**セパレーターのみ**で区切ってください。

        **[Section 1: Executive Summary]** (見出し不可・中身のみ)
        - 結論を3行以内で記述。
        - その下に、**「強化後スキル3種」と「宝具」の内容**を箇条書きで記載する。
        - **重要:** 提供されたデータの**アイコン画像リンク（![Skill](...) や ![Arts](...)）**を必ずそのまま引用して表示すること。
        - (例: - ![Skill](url) スキル名: 効果...)

        <<TACTICAL_DATA>>

        **[Section 2: Tactical Data]** (見出し不可・中身のみ)
        - **📊 戦術分析 (Tactical Breakdown):** 上記の理論(A/B/C)を用いた分析結果。専門用語("TCA"等)は使わず、噛み砕いて説明すること。
        - **公式データ引用:** 解説の中で、重要な**スキルや宝具の公式テキスト（効果説明）**を引用し、数値の根拠を示すこと。
        - **数値の根拠:** 「なぜ強いか」を「ヒット数」「NP効率」「乗算バフ」の観点で説明。
        - **注意:** スキル4表記は禁止。「アペンド2（魔力装填）」と記述。
        - **注意:** 常に**強化後（最新）のスキル**を前提とする。

        <<PARTY_DATA>>

        **[Section 3: Party Formation]** (見出し不可・中身のみ)
        - 以下のカラムを持つテーブルを出力すること:
        `| Role | Icon | Servant | Craft Essence | Note |`
        `| ロール | アイコン | サーヴァント名 | 推奨礼装 | 運用・備考 |`
        
        - **運用コンセプト:** 周回システム名（例：Wコヤンシステム）や、高難易度での耐久手順。
        - **短期決戦 (Short-term):** 周回や超高難易度速攻など、3ターン以内で決着をつける「短期運用」も考慮し、NPチャージ礼装やオダチェン活用の提案を含めること。

        ---
        **【重要: テーブル出力の絶対厳守ルール】**
        1. **Icon列**: データベース情報の `IconURL` があれば `![Alt](URL)`、なければ `(No Image)` とすること。
        2. **Servant列**: 必ず `[サーヴァント名](/servant/ID)` の形式にすること。IDはデータベースに従うこと。
           - 特定のサーヴァントではなく「Artsサポーター」等の場合、IDは不要だが「キャスター」などのクラス名を明記すること。
        3. **Role列**: 「メインアタッカー」「サポーター」などを記述。
        """

        # Append Protocol for Synergy Analysis (JSON Mode)
        system_instruction += """
        
        ---

        ### 【特別プロトコル: クロス・シナジー分析 (Cross-Synergy Protocol)】
        ユーザーが**「2騎以上のサーヴァント（の相性）」**について質問した場合、**上記の手順を無視し**、以下のJSON形式で回答してください。

        **1. 分析ロジック:**
        - **Target A / Target B:** 入力された2騎のサーヴァント。
        - **Synergy Matrix:** お互いが相手に何を提供できるか（NP、星、バフ種類）。
        - **3rd Member:** その2騎の弱点を補う、あるいは長所を伸ばす3人目の最適解。

        **2. 出力JSONフォーマット (厳守):**
        ```json
        {
          "query_type": "synergy_analysis",
          "targets": ["NameA", "NameB"],
          "summary_chat": {
            "short_verdict": "一言で言うとどういう組み合わせか（例：システム周回の革命的ペア）",
            "rating": "S/A/B/C"
          },
          "servant_analyzer": {
            "title": "クロス・シナジー分析",
            "synergy_vectors": [
              {
                "direction": "A_to_B",
                "label": "NameAによる支援",
                "details": ["スキルXによるCT短縮", "宝具によるOC増加"]
              },
              {
                "direction": "B_to_A",
                "label": "NameBによる支援",
                "details": ["スター大量獲得", "バスター耐性ダウン付与"]
              }
            ],
            "shared_strength": "両者とも神性特攻を持つため対神性において最強",
            "critical_weakness": "回避・無敵手段が皆無"
          },
          "party_formation": {
            "concept": "運用コンセプト（例：短期決戦クリティカル型）",
            "third_member": "推奨される3人目のサーヴァント名",
            "third_member_reason": "なぜその3人目が必要か（例：AとBだけではNPが回らないため）",
            "craft_essences": [
              {"holder": "NameA", "recommendation": "推奨礼装名"},
              {"holder": "NameB", "recommendation": "推奨礼装名"}
            ],
            "strategy_steps": [
              "1ターン目の動き",
              "重要なコンボの手順"
            ]
          }
        }
        ```
        **注意:** JSONモードの場合、Markdownのセパレーター（<<TACTICAL_DATA>>等）は不要です。純粋なJSONのみ出力してください。
        """

        if db_context_text:
            system_instruction += f"\n\n【重要：データベース参照情報】\n以下の公式データを基に回答を作成してください。幻覚（ハルシネーション）を避け、数値やスキル効果はこのデータに従ってください。\n**注:** データ内には強化前後のスキルが含まれる場合がありますが、必ず**最新のスキル**（リストの後ろにあるもの）を正として扱ってください。\n\n{db_context_text}"

        full_prompt = f"{system_instruction}\n\nユーザーの質問: {user_input}"

        response = chat.send_message(full_prompt)
        text = response.text
        
        # Try processing as JSON (Synergy Mode) first
        try:
            # Clean up JSON markdown code blocks if present
            cleaned_text = re.sub(r'^```json\s*|\s*```$', '', text.strip(), flags=re.MULTILINE)
            data = json.loads(cleaned_text)
            if data.get('query_type') == 'synergy_analysis':
                return process_synergy_json(data)
        except json.JSONDecodeError:
            pass
            
        # Fallback to standard text processing
        return inject_servant_link_data(text)
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            print(f"Gemini API Rate Limit: {e}")
            return "⚠️ **通信混雑中 (Error 429)**\n\nアクセス集中により、トリスメギストスⅡへの接続が制限されています。\n申し訳ありませんが、**1〜2分ほど時間を空けて**再度お試しください。\n\n(Google Gemini APIの無料枠制限: 5回/分 に到達しました)"

        print(f"Gemini API Error: {e}")
        return f"トリスメギストスⅡとの接続に失敗しました。(Error: {e})\n\n【簡易演算モード】\n" + get_mock_response(user_input)

# ... (SYSTEM_SUPPORT_IDS, _filter_skills, get_system_support_context, extract_data_context remain unchanged) ...

def process_synergy_json(data):
    """
    Process the Synergy Analysis JSON directly, injecting icons/links into fields.
    Returns the modified Dict object (which app.py will jsonify).
    """
    
    def get_svt_markup(name):
        # Helper to get markdown link/icon
        # Remove generic suffixes like (剣) for search
        clean_name = re.sub(r'\(.+?\)', '', name).strip()
        res = database.search_servants(clean_name, limit=1)
        if res:
            svt = res[0]
            icon = svt.get('face_url', '')
            if icon:
                return f"![{svt['name']}]({icon}) [{svt['name']}](/servant/{svt['id']})"
            else:
                return f"(No Image) [{svt['name']}](/servant/{svt['id']})"
        else:
            # Check generic
            name_lower = clean_name.lower()
            if "arts" in name_lower or "アーツ" in name_lower:
                return f"![Arts]({GENERIC_ICON_MAP['arts']}) {name}"
            if "buster" in name_lower or "バスター" in name_lower:
                return f"![Buster]({GENERIC_ICON_MAP['buster']}) {name}"
            if "quick" in name_lower or "クイック" in name_lower:
                return f"![Quick]({GENERIC_ICON_MAP['quick']}) {name}"
            return name

    # Process Target Names (in summary or title logic usually, but here just in the data)
    # Actually, we might want to inject icons into the 'summary' text or just provide them fields.
    # The JSON structure has specific fields. We will inject Markup into:
    # - targets (maybe not needed as array, but good for display)
    # - third_member
    
    # Update Third Member
    if 'party_formation' in data and 'third_member' in data['party_formation']:
        tm = data['party_formation']['third_member']
        data['party_formation']['third_member_markup'] = get_svt_markup(tm)

    # We can also add markup for targets 
    if 'targets' in data:
        data['targets_markup'] = [get_svt_markup(t) for t in data['targets']]

    # Craft Essence holders
    if 'party_formation' in data and 'craft_essences' in data['party_formation']:
        for ce in data['party_formation']['craft_essences']:
             # Holder name markup
             ce['holder_markup'] = get_svt_markup(ce['holder'])
             # CE name markup? (Future work)

    return data


# System Support IDs (Castoria, KoyanLight, Oberon, Skadi Ruler, Skadi Caster)
# Note: IDs must match database keys
SYSTEM_SUPPORT_IDS = [
    504800, # Altria Caster
    604200, # Koyanskaya of Light (Assassin) - Corrected from 604000
    901300, # Oberon
    901400, # Scathach Skadi (Ruler) - Summer
    215000  # Scathach Skadi (Caster) - Corrected
]

def _filter_skills(skills):
    """
    Filter skills to only keep the latest version for each slot.
    Assumes standard FGO data where upgrades appear later in the list.
    """
    if not skills:
        return []
    
    # Store by slot number (1, 2, 3). Non-numbered skills (passives) are kept as is.
    active_slots = {}
    passives = []
    
    for sk in skills:
        num = sk.get('num')
        # If it has a slot number 1-3, it's an active skill (usually)
        if num in [1, 2, 3]:
            # Overwrite with the latest one encountered (assuming chronological order)
            active_slots[num] = sk
        else:
            passives.append(sk)
            
    # Reconstruct list: Sorted active skills + Passives
    filetered_active = [active_slots[k] for k in sorted(active_slots.keys())]
    return filetered_active + passives

def get_system_support_context():
    """
    Fetches context data for system support servants to prevent hallucinations.
    """
    context_lines = ["\n【システム・サポーター定数データ】"]
    for svt_id in SYSTEM_SUPPORT_IDS:
        try:
            # get_servant_detail returns dict with 'json_data' string
            svt = database.get_servant_detail(svt_id)
            if not svt:
                continue
                
            data = json.loads(svt['json_data'])
            name = svt['name']
            
            context_lines.append(f"■ {name} (ID: {svt_id})")
            
            # Skills only (NPs are less critical for supports instructions usually, but added if needed)
            skills = data.get('skills', [])
            # Filter for latest skills
            skills = _filter_skills(skills)
            
            for sk in skills:
                sk_name = sk.get('name', '不明')
                sk_detail = sk.get('detail', '不明')
                context_lines.append(f"- スキル: {sk_name} / {sk_detail}")
            
            # Oberon's Class Skill (Merlin/Oberon passives sometimes matter) or NP for Oberon
            if svt_id == 901300: # Oberon
                 nps = data.get('noblePhantasms', [])
                 for np in nps:
                     context_lines.append(f"- 宝具: {np.get('name')} / {np.get('detail')}")

            context_lines.append("")
        except:
            continue
            
    return "\n".join(context_lines)

def extract_data_context(text):
    """
    ユーザーの入力からサーヴァント名を推測し、データベースから情報を抽出する
    """
    # 簡易的なキーワード抽出（本来は形態素解析などが望ましいが、スペース区切りや部分一致で代用）
    # 1. Try treating the whole text as a single query first (e.g. full name)
    results = database.search_servants(text, limit=3)
    
    if not results:
        # 2. Multi-target extraction
        # Split by particles and common query words to isolate nouns
        delimiters = r'[ 　,、と＆\+の]|について|相性|を|教えて|は|が'
        parts = re.split(delimiters, text)
        
        all_found = []
        seen_ids = set()
        
        for p in parts:
            p = p.strip()
            # Length filter > 1 to avoid single char noise like "?" or "!"
            if len(p) > 1: 
                res = database.search_servants(p, limit=3)
                if res:
                    for s in res:
                        if s['id'] not in seen_ids:
                            all_found.append(s)
                            seen_ids.add(s['id'])
                            
        results = all_found
    
    if not results:
        return ""

    context_lines = []
    for svt in results:
        # 詳細データの取得 (search_servantsはjson_dataを含んでいるが、文字列なのでパースが必要)
        try:
            data = json.loads(svt['json_data'])
            id = svt['id']
            name = svt['name']
            cls = svt['class_name']
            rarity = svt['rarity']
            face_url = svt.get('face_url', '')
            
            context_lines.append(f"■ {name} (ID: {id}, クラス: {cls}, レアリティ: ★{rarity}, IconURL: {face_url})")
            
            # Hidden Parameters (TCA v3.0)
            attr = svt.get('attribute', 'earth')
            np_gain = svt.get('np_charge_rate', 'N/A')
            hits = svt.get('hits_distribution', {})
            traits = svt.get('traits', [])
            
            context_lines.append("【隠しパラメータ (TCA v3.0 Reference)】")
            context_lines.append(f"- 天地人属性: {attr}")
            context_lines.append(f"- 基礎NP獲得率(Atk): {np_gain}%")
            
            hits_str = ", ".join([f"{k.capitalize()}: {v}Hit" for k, v in hits.items()])
            context_lines.append(f"- ヒット数分布: {hits_str}")
            
            traits_str = ", ".join(traits)
            context_lines.append(f"- 保有特性: {traits_str}")

            # Skills
            skills = data.get('skills', [])
            # Filter for latest skills
            skills = _filter_skills(skills)
            
            context_lines.append("【保有スキル (最新)】")
            for sk in skills:
                sk_name = sk.get('name', '不明')
                sk_detail = sk.get('detail', '不明')
                # Try to get icon URL
                sk_icon = sk.get('icon')
                if sk_icon:
                    # Markdown Image
                    icon_md = f"![Skill]({sk_icon})"
                else:
                    icon_md = "(Icon)"
                    
                context_lines.append(f"- {icon_md} {sk_name}: {sk_detail}")
                
            # NPs
            nps = data.get('noblePhantasms', [])
            context_lines.append("【宝具】")
            for np in nps:
                np_name = np.get('name', '不明')
                np_detail = np.get('detail', '不明')
                np_card = np.get('card', 'unknown').lower()
                
                # Map card to generic local icon
                card_icon_url = GENERIC_ICON_MAP.get(np_card, '')
                if card_icon_url:
                     card_md = f"![{np_card}]({card_icon_url})"
                else:
                     card_md = f"({np_card})"
                
                np_type = "全体" if "敵全体" in np_detail else ("単体" if "敵単体" in np_detail else "補助")
                
                # NP Hits logic (from earlier)
                np_dist = np.get("npDistribution", [])
                np_hits = len(np_dist) if np_dist else 0
                
                context_lines.append(f"- {card_md} {np_name} ({np_type}, {np_hits}Hit): {np_detail}")
                
            context_lines.append("") # Empty line separator
            
        except:
            continue
            
    return "\n".join(context_lines)

def get_mock_response(text):
    """APIキーがない場合のパターンマッチ応答"""
    text = text.lower()
    
    if "周回" in text or "farming" in text:
        return "周回効率を上げるには、NPチャージ持ちのサーヴァント（アルトリア・キャスター、光のコヤンスカヤ、オベロン等）の育成を優先することを推奨します。"
    elif "高難易度" in text or "cq" in text:
        return "高難易度クエストでは、耐久パーティ（キャストリア＋マーリン＋モルガン等）が有効です。敵のギミックを確認し、無敵貫通や弱体解除を用意してください。"
    elif "マシュ" in text:
        return "マシュ・キリエライトはコスト0で編成可能な優秀な盾役です。第2部6章以降の戦闘では、オルテナウス形態の活用も視野に入れてください。"
    elif "ガチャ" in text or "召喚" in text:
        return "聖晶石の残量に注意してください。ピックアップ召喚の確率は0.8%です。ご利用は計画的に。"
    else:
        return "申し訳ありません。現在オフラインモードのため、詳細な解析ができません。設定画面からGemini APIキーを入力することで、高度な攻略相談が可能になります。"


# Generic Card Icons (Local SVGs for High Visibility)
GENERIC_ICON_MAP = {
    'arts': '/static/arts.svg',
    'buster': '/static/buster.svg',
    'quick': '/static/quick.svg',
    '1': '/static/arts.svg',
    '2': '/static/buster.svg',
    '3': '/static/quick.svg'
}

# Atlas Academy Class Icons
CLASS_ICON_MAP = {
    'セイバー': 'https://static.atlasacademy.io/JP/ClassIcons/class_1.png',
    'アーチャー': 'https://static.atlasacademy.io/JP/ClassIcons/class_2.png',
    'ランサー': 'https://static.atlasacademy.io/JP/ClassIcons/class_3.png',
    'ライダー': 'https://static.atlasacademy.io/JP/ClassIcons/class_4.png',
    'キャスター': 'https://static.atlasacademy.io/JP/ClassIcons/class_5.png',
    'アサシン': 'https://static.atlasacademy.io/JP/ClassIcons/class_6.png',
    'バーサーカー': 'https://static.atlasacademy.io/JP/ClassIcons/class_7.png',
    'シールダー': 'https://static.atlasacademy.io/JP/ClassIcons/class_8.png',
    'ルーラー': 'https://static.atlasacademy.io/JP/ClassIcons/class_9.png',
    'アルターエゴ': 'https://static.atlasacademy.io/JP/ClassIcons/class_10.png',
    'アヴェンジャー': 'https://static.atlasacademy.io/JP/ClassIcons/class_11.png',
    'ムーンキャンサー': 'https://static.atlasacademy.io/JP/ClassIcons/class_23.png',
    'フォーリナー': 'https://static.atlasacademy.io/JP/ClassIcons/class_25.png',
    'プリテンダー': 'https://static.atlasacademy.io/JP/ClassIcons/class_28.png',
    'ビースト': 'https://static.atlasacademy.io/JP/ClassIcons/class_33.png'
}

def inject_servant_link_data(text):
    """
    AIの応答テキストからMarkdownテーブルの行を解析し、
    サーヴァント名をデータベースで検索して、正しいアイコンURLとリンクIDを注入する。
    サーヴァントが見つからない場合でも、役割名（Artsサポーター等）からアイコンを自動付与する。
    """
    lines = text.split('\n')
    new_lines = []
    
    # テーブル行の判定パターン: パイプで始まり、パイプで終わる
    # | Position | Icon | Name | ...
    
    for line in lines:
        stripped = line.strip()
        # テーブル行かつ見出し行(---)でない場合
        if stripped.startswith('|') and stripped.endswith('|') and '---' not in stripped:
            parts = [p.strip() for p in stripped.split('|')]
            
            # parts[0] is empty (before first |), parts[-1] is empty (after last |)
            # Strategy requests 5 columns -> 7 parts usually
            # | Pos | Icon | Name | Role | CE |
            
            if len(parts) >= 6:
                # 3rd column (index 3) is Name (0='', 1=Pos, 2=Icon, 3=Name)
                raw_name_col = parts[3]
                
                # ヘッダー行("サーヴァント名"など)はスキップ
                # ヘッダー行("サーヴァント名"など)はスキップ
                if "サーヴァント" in raw_name_col or "名称" in raw_name_col or "Servant" in raw_name_col:
                    # Clear the Icon column (Index 2)
                    if len(parts) > 2:
                        parts[2] = "" 
                    new_line = " | ".join(parts)
                    new_lines.append(new_line)
                    continue

                # 名前からMarkdownリンクを除去して純粋な名前を抽出
                # [Name](URL) -> Name
                clean_name = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', raw_name_col)
                # Remove class emojis if any remain (though prompt forbids it)
                clean_name = re.sub(r'[⚔️🏹📍🐎🪄👤👹⚖️⛓️🌙🎭🐙🃏🛡️]', '', clean_name).strip()
                
                # Class Suffix Detection (TCA v3.0 Bugfix)
                # AI might output "ギルガメッシュ(術)" or "Gilgamesh (Caster)"
                # We need to extract this class to filter the search
                detected_class = None
                
                # Map common suffixes to JP class names (for database.search_servants filter)
                suffix_map = {
                    r'\(術\)': 'キャスター', r'（術）': 'キャスター', r'\(Caster\)': 'キャスター',
                    r'\(弓\)': 'アーチャー', r'（弓）': 'アーチャー', r'\(Archer\)': 'アーチャー',
                    r'\(槍\)': 'ランサー', r'（槍）': 'ランサー', r'\(Lancer\)': 'ランサー',
                    r'\(剣\)': 'セイバー', r'（剣）': 'セイバー', r'\(Saber\)': 'セイバー',
                    r'\(騎\)': 'ライダー', r'（騎）': 'ライダー', r'\(Rider\)': 'ライダー',
                    r'\(殺\)': 'アサシン', r'（殺）': 'アサシン', r'\(Assassin\)': 'アサシン',
                    r'\(狂\)': 'バーサーカー', r'（狂）': 'バーサーカー', r'\(Berserker\)': 'バーサーカー',
                    r'\(裁\)': 'ルーラー', r'（裁）': 'ルーラー', r'\(Ruler\)': 'ルーラー',
                    r'\(讐\)': 'アヴェンジャー', r'（讐）': 'アヴェンジャー', r'\(Avenger\)': 'アヴェンジャー',
                    r'\(月\)': 'ムーンキャンサー', r'（月）': 'ムーンキャンサー', r'\(MoonCancer\)': 'ムーンキャンサー',
                    r'\(分\)': 'アルターエゴ', r'（分）': 'アルターエゴ', r'\(AlterEgo\)': 'アルターエゴ',
                    r'\(降\)': 'フォーリナー', r'（降）': 'フォーリナー', r'\(Foreigner\)': 'フォーリナー',
                    r'\(詐\)': 'プリテンダー', r'（詐）': 'プリテンダー', r'\(Pretender\)': 'プリテンダー',
                    r'\(盾\)': 'シールダー', r'（盾）': 'シールダー', r'\(Shielder\)': 'シールダー',
                    r'\(獣\)': 'ビースト', r'（獣）': 'ビースト', r'\(Beast\)': 'ビースト'
                }
                
                search_name = clean_name
                filters = None
                
                for pattern, cls_name in suffix_map.items():
                    if re.search(pattern, clean_name, re.IGNORECASE):
                        detected_class = cls_name
                        # Remove suffix from search name
                        search_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE).strip()
                        filters = [cls_name]
                        break

                # データベース検索
                found_svt = None
                # First try with clean name (or stripped name) + filters
                results = database.search_servants(search_name, filters=filters, limit=1)
                
                if results:
                    found_svt = results[0]
                else:
                    # 見つからない場合、カッコ書きを除去して再検索 (例: "アルトリア(剣)" -> "アルトリア")
                    # (Fallback if regex above missed some other pattern)
                    base_name = re.sub(r'\s*\(.*?\)', '', clean_name) # clean_name original
                    base_name = re.sub(r'\s*（.*?）', '', base_name) # full-width
                    
                    if base_name != clean_name and base_name:
                         # Retry with base name but KEEP filters if detected
                         results_retry = database.search_servants(base_name, filters=filters, limit=1)
                         if results_retry:
                             found_svt = results_retry[0]
                         else:
                             # Last resort: Try without filters (might link wrong class but better than nothing)
                             results_last = database.search_servants(base_name, limit=1)
                             if results_last:
                                 found_svt = results_last[0]
                
                if found_svt:
                    # データを上書き
                    s_id = found_svt['id']
                    s_name = found_svt['name']
                    s_url = found_svt.get('face_url', '')
                    
                    # アイコン列 (Index 2)
                    if s_url:
                        parts[2] = f"![{s_name}]({s_url})"
                    else:
                        parts[2] = "(No Image)"
                        
                    # 名前列 (Index 3)
                    parts[3] = f"[{s_name}](/servant/{s_id})"
                
                else:
                    # サーヴァントが見つからない場合、汎用ロール判定を行う
                    name_lower = clean_name.lower()
                    icon_url = None
                    
                    # 1. Class Icon Check (Priority)
                    for cls_name, cls_url in CLASS_ICON_MAP.items():
                        if cls_name in clean_name: # Simple string match
                            icon_url = cls_url
                            break
                    
                    # 2. Card Type Icon Check (Fallback)
                    if not icon_url:
                        if "arts" in name_lower or "アーツ" in name_lower:
                            icon_url = GENERIC_ICON_MAP['arts']
                        elif "buster" in name_lower or "バスター" in name_lower:
                            icon_url = GENERIC_ICON_MAP['buster']
                        elif "quick" in name_lower or "クイック" in name_lower:
                            icon_url = GENERIC_ICON_MAP['quick']
                    
                    if icon_url:
                        parts[2] = f"![Role]({icon_url})"
                        parts[3] = clean_name
                    else:
                        parts[2] = "(No Image)"

                    
                # 行を再構築
                new_line = " | ".join(parts)
                new_lines.append(new_line)
                continue
        
        new_lines.append(line)
        
    return "\n".join(new_lines)

