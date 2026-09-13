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

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.main,
section[data-testid="stMain"] {
    background-color: #080d16 !important;
    color: #ffffff !important;
}

[data-testid="stAppViewContainer"] .main .block-container {
    background-color: #080d16 !important;
    color: #ffffff !important;
}

[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] span {
    color: #ffffff;
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4 {
    color: #ffffff !important;
    font-weight: 900 !important;
}

/* カード：背景と文字をセットで管理 */
.mobile-guide {
    background-color: #111827 !important;
    color: #ffffff !important;
    border: 1px solid #475569 !important;
    border-left: 7px solid #38bdf8 !important;
}

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

/* レベル別バッジ等 */
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

/* セレクトボックスのダーク化 */
div[data-testid="stSelectbox"] {
    background-color: #080d16 !important;
    border-left: 7px solid #ffe600;
    padding-left: 10px;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #000000 !important;
    background-color: #000000 !important;
    border: 2px solid #64748b !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    min-height: 48px !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 900 !important;
}

div[data-baseweb="popover"],
div[data-baseweb="menu"],
div[role="listbox"] {
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

a {
    color: #60a5fa !important;
    font-weight: 800 !important;
}

a:hover {
    color: #93c5fd !important;
}

hr {
    border-color: #64748b !important;
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

            for series in data[0].get("timeSeries", []):
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
                "forecasts": weather_forecasts[:4] if weather_forecasts else [f"【{region_name}】 &nbsp; &nbsp; エリアの気象データを正常に取得しました。"]
            }
    except Exception as e:
        return {
            "success": False,
            "office": "気象庁（オフライン/フォールバック）",
            "forecasts": [f"【{region_name}】 &nbsp; &nbsp; リアルタイムAPI接続確認中（通信環境または制限によりキャッシュ表示中）"]
        }

@st.cache_data(ttl=300)
def fetch_region_prefecture_weather(region_name):
    """選択地域の各都道府県の天気および最高・最低気温情報を取得"""
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
            max_temp = "--"
            min_temp = "--"
            
            # タイムシリーズから天気と気温データを探索
            for series in data[0].get("timeSeries", []):
                # 天気の取得
                for area in series.get("areas", []):
                    weathers = area.get("weathers", [])
                    if weathers and not weather:
                        weather = str(weathers[0]).strip()
                
                # 気温データの取得（tempsリストがあれば抽出）
                for temp_area in series.get("areas", []):
                    temps = temp_area.get("temps", [])
                    if temps:
                        if len(temps) > 1 and temps[1] != "":
                            max_temp = temps[1]
                        elif len(temps) > 0 and temps[0] != "":
                            max_temp = temps[0]
                        if len(temps) > 2 and temps[2] != "":
                            min_temp = temps[2]

            weather_match = re.match(r"(晴|曇|雨|雪|雷|晴れ|曇り|雨時々曇|曇時々雨|雨一時曇|曇一時雨)", weather)
            weather_label = weather_match.group(1) if weather_match else "気象情報あり"

            results.append({
                "prefecture": prefecture,
                "success": True,
                "weather": weather_label,
                "comment": weather or "天気情報を取得しました。",
                "max_temp": max_temp,
                "min_temp": min_temp
            })
        except Exception:
            results.append({
                "prefecture": prefecture,
                "success": False,
                "weather": "取得できず",
                "comment": "リアルタイム気象情報を取得できませんでした。",
                "max_temp": "--",
                "min_temp": "--"
            })

    return results

# ==========================================
# メイン画面
# ==========================================

# 1. 起動時の注意書き（ダブルチェック用・常時表示）
st.warning(
    "**【起動時のご注意】**\n\n"
    "一定時間アクセスがないと「Zzzz」というスリープ画面が表示されます。"
    "その場合は、画面にある青いボタン（**Yes, get this app back up!**）を1回押してサーバーを復帰させてください。"
)

st.title("🛡️ 全国インフラ・気象防災カルテ・リアルリンク共用システム")
st.markdown("災害時のリアルタイム気象状況・インフラ情報をモバイル最適化で提供します。")
st.markdown("---")

# 2. 監視エリア選択
selected_region = st.selectbox("🌍 監視エリアを選択してください", list(REGION_CODES.keys()), index=2)

# 3. 気象データ取得
weather_data = fetch_jma_realtime_data(selected_region)

# 4. リアルタイム天気予報の表示
st.markdown(f"### 📡 {selected_region}地方の気象情報 ({weather_data['office']})")
for forecast in weather_data["forecasts"]:
    st.markdown(f"- {forecast}")

st.markdown("---")

# 5. 都道府県別の詳細ステータス（最高・最低気温の常時表示対応）
st.markdown(f"### 📋 {selected_region}管内 都道府県別ステータス・気温")
pref_weather_list = fetch_region_prefecture_weather(selected_region)
for pw in pref_weather_list:
    # 都道府県ごとに気温情報と天気をわかりやすく並べて表示
    st.markdown(
        f"**📍 {pw['prefecture']}**: {pw['weather']} "
        f"(最高: **{pw['max_temp']}°C** / 最低: **{pw['min_temp']}°C**)\n\n"
        f"> 📝 {pw['comment']}"
    )
    st.markdown("")
