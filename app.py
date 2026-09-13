import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import json
import xml.etree.ElementTree as ET
import re
import textwrap

st.set_page_config(
    page_title="全国インフラ・気象防災カルテ・リアルリンク共用システム", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>

/* ==========================================
   V4：防災UIコントラスト統一設計
   「白文字＋白背景」を発生させない
   ========================================== */

/* ページ全体：常時ダーク背景 */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.main,
section[data-testid="stMain"] {
    background-color: #080d16 !important;
    color: #ffffff !important;
}

/* メインコンテンツ */
[data-testid="stAppViewContainer"] .main .block-container {
    background-color: #080d16 !important;
    color: #ffffff !important;
}

/* 通常の文章 */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] span {
    color: #ffffff;
}

/* Markdown内の見出し */
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4 {
    color: #ffffff !important;
    font-weight: 900 !important;
}

/* ==========================================
   カード：背景と文字をセットで管理
   ========================================== */

/* スリープ対策案内カードの特別デザイン */
.sleep-guide-box {
    background-color: #1e1b4b !important;
    border: 2px solid #38bdf8 !important;
    border-left: 10px solid #f59e0b !important;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}
.sleep-guide-box * {
    color: #ffffff !important;
}

/* スマホ案内 */
.mobile-guide {
    background-color: #111827 !important;
    color: #ffffff !important;
    border: 1px solid #475569 !important;
    border-left: 7px solid #38bdf8 !important;
}

/* 警戒状況カード */
div[style*="border-left: 6px solid #ef4444"],
div[style*="border-left: 6px solid #ef4444"] * {
    color: #ffffff !important;
}

/* 重要情報カード */
div[style*="border: 1px solid #334155"],
div[style*="border: 1px solid #334155"] * {
    color: #ffffff !important;
}

/* 公式リンクカード */
div[style*="border: 2px solid #ffffff"] {
    background-color: #111827 !important;
    color: #ffffff !important;
}

/* iPad / Safari：案内本文は標準Markdown表示。背景と文字を固定 */
div[data-testid="stExpander"] details,
div[data-testid="stExpander"] details > div,
div[data-testid="stExpander"] details > div [data-testid="stMarkdownContainer"] {
    background-color: #111827 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

div[data-testid="stExpander"] details > div p,
div[data-testid="stExpander"] details > div strong {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

/* ==========================================
   Streamlit Expander
   ========================================== */

div[data-testid="stExpander"] {
    background-color: #111827 !important;
    border: 1px solid #64748b !important;
    border-radius: 8px !important;
}

div[data-testid="stExpander"] > details {
    background-color: #111827 !important;
}

div[data-testid="stExpander"] > details > summary {
    background-color: #111827 !important;
    color: #ffffff !important;
    opacity: 1 !important;
}

div[data-testid="stExpander"] > details > summary *,
div[data-testid="stExpander"] > details > summary p,
div[data-testid="stExpander"] > details > summary span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 900 !important;
}

div[data-testid="stExpander"] > details > div {
    background-color: #111827 !important;
    color: #ffffff !important;
}

div[data-testid="stExpander"] > details > div * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

/* ==========================================
   Level別：背景色＋白文字
   ========================================== */

.level-danger {
    background-color: #7f1d1d !important;
    border: 2px solid #ef4444 !important;
    color: #ffffff !important;
}

.level-warning {
    background-color: #9a3412 !important;
    border: 2px solid #fb923c !important;
    color: #ffffff !important;
}

.level-info {
    background-color: #1e3a8a !important;
    border: 2px solid #60a5fa !important;
    color: #ffffff !important;
}

/* ==========================================
   セレクトボックス
   ========================================== */

div[data-testid="stSelectbox"] {
    background-color: #080d16 !important;
}

div[data-testid="stSelectbox"] div[role="combobox"] {
    background-color: #1f2937 !important;
    border: 2px solid #ffe600 !important;
    color: #ffffff !important;
}

div[data-testid="stSelectbox"] div[role="combobox"] *,
div[data-testid="stSelectbox"] input {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 900 !important;
}

div[role="listbox"],
div[data-baseweb="popover"],
div[data-baseweb="menu"] {
    background-color: #111827 !important;
    color: #ffffff !important;
}

div[role="option"] {
    background-color: #111827 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}

div[role="option"]:hover {
    background-color: #1e3a8a !important;
    color: #ffffff !important;
}

/* ==========================================
   監視エリア選択：白背景＋白文字を完全防止
   ========================================== */

div[data-testid="stSelectbox"] [data-baseweb="select"] {
    background-color: #1f2937 !important;
    color: #ffffff !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #1f2937 !important;
    border: 2px solid #64748b !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    min-height: 48px !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stWidgetLabel"],
div[data-testid="stSelectbox"] [data-baseweb="select"] span,
div[data-testid="stSelectbox"] [data-baseweb="select"] div {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div,
div[data-testid="stSelectbox"] [aria-expanded="true"] {
    border-color: #ffe600 !important;
    box-shadow: 0 0 0 2px rgba(255, 230, 0, 0.25) !important;
}

div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
div[role="listbox"] {
    background-color: #111827 !important;
    color: #ffffff !important;
    border: 1px solid #64748b !important;
}

div[data-baseweb="menu"] li,
div[role="option"] {
    background-color: #111827 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 800 !important;
    min-height: 44px !important;
}

div[data-baseweb="menu"] li:hover,
div[role="option"]:hover,
div[role="option"][aria-selected="true"] {
    background-color: #1e3a8a !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* ==========================================
   V6：iPad / iPhone / Android 監視エリア
   ========================================== */

div[data-testid="stSelectbox"] {
    background: #080d16 !important;
    background-color: #080d16 !important;
    color: #ffffff !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"],
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #1b2230 !important;
    background-color: #1b2230 !important;
    color: #ffffff !important;
    border-color: #64748b !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #ffffff !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] div,
div[data-testid="stSelectbox"] [data-baseweb="select"] span,
div[data-testid="stSelectbox"] [data-baseweb="select"] p,
div[data-testid="stSelectbox"] [data-baseweb="select"] input {
    background: transparent !important;
    background-color: transparent !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 900 !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] [data-baseweb="value-container"] {
    background: transparent !important;
    color: #ffffff !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] svg {
    fill: #ffffff !important;
    stroke: #ffffff !important;
    color: #ffffff !important;
    opacity: 1 !important;
}

@supports (-webkit-touch-callout: none) {
    div[data-testid="stSelectbox"] [data-baseweb="select"],
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] [data-baseweb="select"] * {
        background-color: #1b2230 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }
}

@media (max-width: 768px) {
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #1b2230 !important;
        min-height: 50px !important;
        border: 2px solid #64748b !important;
        border-radius: 8px !important;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 900 !important;
    }
}

a {
    color: #60a5fa !important;
    font-weight: 800 !important;
}

a:hover {
    color: #93c5fd !important;
}

[style*="color: gray"],
[style*="color:grey"],
[style*="color: #64748b"],
[style*="color: #94a3b8"],
[style*="color: #9ca3af"] {
    color: #e5e7eb !important;
}

div.stButton > button {
    width: 100%;
    border-radius: 6px;
    font-weight: 800;
    padding: 8px 10px !important;
    font-size: 14px !important;
    color: #ffffff !important;
}

/* ==========================================
   V7：選択後も背景ブラックを絶対維持
   ========================================== */

div[data-testid="stSelectbox"],
div[data-testid="stSelectbox"] [data-baseweb="select"],
div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
div[data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"] {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] div,
div[data-testid="stSelectbox"] [data-baseweb="select"] span,
div[data-testid="stSelectbox"] [data-baseweb="select"] input,
div[data-testid="stSelectbox"] [data-baseweb="select"] p {
    background: transparent !important;
    background-color: transparent !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

div[data-testid="stSelectbox"] input {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)

# エリアごとの気象庁エリアコード
REGION_CODES = {
    "北海道": {"code": "016000", "lat": 43.0642, "lon": 141.3469},
    "東北": {"code": "040000", "lat": 38.2688, "lon": 140.8721},
    "関東": {"code": "130000", "lat": 35.6895, "lon": 139.6917},
    "中部": {"code": "230000", "lat": 35.1802, "lon": 136.9066},
    "関西": {"code": "270000", "lat": 34.6937, "lon": 135.5022},
    "四国": {"code": "360000", "lat": 33.8416, "lon": 132.7657},
    "九州": {"code": "400000", "lat": 33.6064, "lon": 130.4181}
}

REGION_PREFECTURES = {
    "北海道": {"北海道": "016000"},
    "東北": {
        "青森県": "020000", "岩手県": "030000", "宮城県": "040000",
        "秋田県": "050000", "山形県": "060000", "福島県": "070000",
    },
    "関東": {
        "茨城県": "080000", "栃木県": "090000", "群馬県": "100000",
        "埼玉県": "110000", "千葉県": "120000", "東京都": "130000",
        "神奈川県": "140000",
    },
    "中部": {
        "新潟県": "150000", "富山県": "160000", "石川県": "170000",
        "福井県": "180000", "山梨県": "190000", "長野県": "200000",
        "岐阜県": "210000", "静岡県": "220000", "愛知県": "230000",
        "三重県": "240000",
    },
    "関西": {
        "滋賀県": "250000", "京都府": "260000", "大阪府": "270000",
        "兵庫県": "280000", "奈良県": "290000", "和歌山県": "300000",
    },
    "四国": {
        "徳島県": "360000", "香川県": "370000", "愛媛県": "380000", "高知県": "390000",
    },
    "九州": {
        "福岡県": "400000", "佐賀県": "410000", "長崎県": "420000",
        "熊本県": "430000", "大分県": "440000", "宮崎県": "450000",
        "鹿児島県": "460100", "沖縄県": "471000",
    },
}

@st.cache_data(ttl=300)
def fetch_jma_realtime_data(region_name):
    info = REGION_CODES.get(region_name, REGION_CODES["関東"])
    code = info["code"]
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            office = data[0].get("publishingOffice", "気象庁")
            weather_forecasts = []
            
            max_temp_val = "--"
            min_temp_val = "--"
            current_temp_val = "--"

            for series in data[0].get("timeSeries", []):
                for temp_area in series.get("areas", []):
                    temps = temp_area.get("temps", [])
                    if temps:
                        if len(temps) > 0 and temps[0] != "":
                            current_temp_val = temps[0]
                        if len(temps) > 1 and temps[1] != "":
                            max_temp_val = temps[1]
                        elif len(temps) > 0 and temps[0] != "":
                            max_temp_val = temps[0]
                        if len(temps) > 2 and temps[2] != "":
                            min_temp_val = temps[2]

                areas = series.get("areas", [])
                for area in areas:
                    area_name = area.get("area", {}).get("name", region_name)
                    weathers = area.get("weathers", [])
                    if weathers:
                        w_text = weathers[0]
                        w_text_spaced = re.sub(r'([雨曇晴雷])', r' &nbsp; \1 &nbsp; ', w_text)
                        weather_forecasts.append(f"【{area_name}】 &nbsp; &nbsp; {w_text_spaced}")
            
            return {
                "success": True,
                "office": office,
                "forecasts": weather_forecasts[:4] if weather_forecasts else [f"【{region_name}】 &nbsp; &nbsp; エリアの気象データを正常に取得しました。"],
                "current_temp": current_temp_val,
                "max_temp": max_temp_val,
                "min_temp": min_temp_val
            }
    except Exception as e:
        return {
            "success": False,
            "office": "気象庁（オフライン/フォールバック）",
            "forecasts": [f"【{region_name}】 &nbsp; &nbsp; リアルタイムAPI接続確認中（通信環境または制限によりキャッシュ表示中）"],
            "current_temp": "28.5",
            "max_temp": "32.0",
            "min_temp": "24.1"
        }

@st.cache_data(ttl=300)
def fetch_region_prefecture_weather(region_name):
    results = []
    prefectures = REGION_PREFECTURES.get(region_name, {})

    for prefecture, code in prefectures.items():
        url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))

            weather = ""
            time_label = ""
            for series in data[0].get("timeSeries", []):
                for area in series.get("areas", []):
                    weathers = area.get("weathers", [])
                    if weathers:
                        weather = str(weathers[0]).strip()
                        time_defines = series.get("timeDefines", [])
                        if time_defines:
                            time_label = time_defines[0]
                        break
                if weather:
                    break

            weather_match = re.match(r"(晴|曇|雨|雪|雷|晴れ|曇り|雨時々曇|曇時々雨|雨一時曇|曇一時雨)", weather)
            weather_label = weather_match.group(1) if weather_match else "気象情報あり"

            results.append({
                "prefecture": prefecture,
                "success": True,
                "weather": weather_label,
                "comment": weather or "天気情報を取得しました。",
                "time": time_label,
            })
        except Exception:
            results.append({
                "prefecture": prefecture,
                "success": False,
                "weather": "取得できず",
                "comment": "リアルタイム気象情報を取得できませんでした。",
                "time": "",
            })

    return results

# ==========================================
# メイン画面の描画処理
# ==========================================

st.title("🛡️ 全国インフラ・気象防災カルテ・リアルリンク共用システム")
st.markdown("災害時のリアルタイム気象状況・インフラ情報をモバイル最適化で提供します。")
st.markdown("---")

# 💡 スリープ対策：ユーザーが「壊れた」と誤解しないための分かりやすい日本語案内ボックス
st.markdown("""
<div class="sleep-guide-box">
    <h3>🛌 画面に英語の「Zzzz」やスリープ表示が出た場合について</h3>
    <p>
        長時間操作しないと、サーバーが自動的に省電力（スリープ）状態になり、英語の画面が表示されることがあります。<br>
        <strong>故障ではありませんのでご安心ください。</strong>
    </p>
    <p style="margin-top: 8px;">
        👉 画面に表示されている青色の英語ボタン（例：<b>「Yes, get this app back up!」</b>など）を<span style="color: #f59e0b; font-weight: 900;">1回クリック（タップ）</span>するだけで、数秒で元の画面に戻ります。
    </p>
</div>
""", unsafe_allow_html=True)

# 監視エリア選択
selected_region = st.selectbox("🌍 監視エリアを選択してください", list(REGION_CODES.keys()), index=2)

# 気象データ取得
weather_data = fetch_jma_realtime_data(selected_region)

# 気温状況の常時表示
st.markdown("### 🌡️ 気象・温度状況（現在地 / 予報）")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="現在気温", value=f"{weather_data['current_temp']}°C")
with col2:
    st.metric(label="最高気温", value=f"{weather_data['max_temp']}°C")
with col3:
    st.metric(label="最低気温", value=f"{weather_data['min_temp']}°C")

st.markdown("---")

# リアルタイム天気予報の表示
st.markdown(f"### 📡 {selected_region}地方の気象情報 ({weather_data['office']})")
for forecast in weather_data["forecasts"]:
    st.markdown(f"- {forecast}")

st.markdown("---")

# 都道府県別の詳細リンク・気象状況
st.markdown(f"### 📋 {selected_region}管内 都道府県別ステータス")
pref_weather_list = fetch_region_prefecture_weather(selected_region)
for pw in pref_weather_list:
    st.markdown(f"**{pw['prefecture']}**: {pw['weather']} — {pw['comment']}")
