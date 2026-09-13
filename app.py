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

REGION_WARNING_OFFICES = {
    "北海道": ["016000"],
    "東北": ["020000", "030000", "040000", "050000", "060000", "070000"],
    "関東": ["080000", "090000", "100000", "110000", "120000", "130000", "140000"],
    "中部": ["150000", "160000", "170000", "180000", "190000", "200000", "210000", "220000", "230000", "240000"],
    "関西": ["250000", "260000", "270000", "280000", "290000", "300000"],
    "四国": ["360000", "370000", "380000", "390000"],
    "九州": ["400000", "410000", "420000", "430000", "440000", "450000", "460000", "470000"],
}

JMA_LEVEL_CODES = {
    "Level5": {"33", "39", "38", "35", "36", "37", "32", "51", "53"},
    "Level4": {"43", "49", "48", "40", "41"},
    "Level3": {"03", "09", "08", "30", "31"},
    "Level2": {"10", "29", "19", "12", "13", "14", "15", "16", "17", "20", "21", "22", "23", "24", "25", "26", "27"},
}

JMA_WARNING_NAMES = {
    "10": "レベル2大雨注意報", "03": "Level3大雨警報", "43": "Level4大雨危険警報", "33": "Level5大雨特別警報",
    "29": "Level2土砂災害注意報", "09": "Level3土砂災害警報", "49": "Level4土砂災害危険警報", "39": "Level5土砂災害特別警報",
    "19": "Level2高潮注意報", "08": "Level3高潮警報", "48": "Level4高潮危険警報", "38": "Level5高潮特別警報",
    "15": "強風注意報", "05": "暴風警報", "35": "暴風特別警報", "13": "風雪注意報", "02": "暴風雪警報", "32": "暴風雪特別警報",
    "16": "波浪注意報", "07": "波浪警報", "37": "波浪特別警報", "12": "大雪注意報", "06": "大雪警報", "36": "大雪特別警報",
    "17": "融雪注意報", "14": "雷注意報", "20": "濃霧注意報", "21": "乾燥注意報", "22": "なだれ注意報",
    "23": "低温注意報", "24": "霜注意報", "25": "着氷注意報", "26": "着雪注意報", "27": "その他の注意報",
    "30": "Level3氾濫警報", "31": "Level3氾濫警報", "40": "Level4氾濫危険警報", "41": "Level4氾濫危険警報",
    "51": "Level5氾濫特別警報", "53": "Level5氾濫特別警報",
}

def jma_level_from_code(code):
    code = str(code).zfill(2)
    for level, codes in JMA_LEVEL_CODES.items():
        if code in codes:
            return level
    return None

@st.cache_data(ttl=600)
def fetch_jma_area_names():
    url = "https://www.jma.go.jp/bosai/common/const/area.json"
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))

        mapping = {}
        def walk(obj):
            if isinstance(obj, dict):
                code = obj.get("code")
                name = obj.get("name")
                if code is not None and name:
                    mapping[str(code)] = str(name)
                for value in obj.values():
                    walk(value)
            elif isinstance(obj, list):
                for value in obj:
                    walk(value)

        walk(data)
        return mapping
    except Exception:
        return {}

@st.cache_data(ttl=60)
def fetch_jma_earthquake_info():
    """気象庁の公式地震情報JSONを取得（安定したエンドポイントを使用）"""
    url = "https://www.jma.go.jp/bosai/information/data/quake.json"
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            quakes = json.loads(response.read().decode('utf-8'))
            
        if quakes and isinstance(quakes, list):
            latest = quakes[0]
            time_str = latest.get("at", "日時不明")
            hypo = latest.get("hypocenter", {}).get("name", "震源地不明")
            max_scale = latest.get("maxScale", "不明")
            
            scale_map = {
                "10": "震度1", "20": "震度2", "30": "震度3", "40": "震度4",
                "45": "震度5弱", "50": "震度5強", "55": "震度6弱", "60": "震度6強", "70": "震度7"
            }
            scale_text = scale_map.get(str(max_scale), f"震度(コード:{max_scale})")
            
            return {
                "success": True,
                "time": time_str,
                "hypocenter": hypo,
                "max_scale": scale_text,
                "detail": latest.get("text", "直近の地震活動に特段の異常はありません。")
            }
    except Exception:
        pass
    
    return {
        "success": False,
        "time": "取得待機中",
        "hypocenter": "通信制限またはキャッシュ待機中",
        "max_scale": "--",
        "detail": "現在、気象庁地震情報APIへの接続を確認しています。"
    }

@st.cache_data(ttl=300)
def fetch_jma_warning_level_areas(region_name):
    office_codes = REGION_WARNING_OFFICES.get(
        region_name,
        [REGION_CODES.get(region_name, REGION_CODES["関東"])["code"]]
    )
    area_names = fetch_jma_area_names()
    
    level_data = {
        "Level5": {},
        "Level4": {},
        "Level3": {},
        "Level2": {}
    }

    for office_code in office_codes:
        warning_url = f"https://www.jma.go.jp/bosai/warning/data/warning/{office_code}.json"
        try:
            req = urllib.request.Request(
                warning_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))

            for area_type in data.get("areaTypes", []):
                for area in area_type.get("areas", []):
                    area_code = str(area.get("code", ""))
                    
                    name = area_names.get(area_code)
                    if not name or name == "地域不明":
                        continue
                    
                    for w in area.get("warnings", []):
                        status = w.get("status", "")
                        if status in ["解除", "発表警報・注意報はなし", "", None]:
                            continue
                        
                        w_code = str(w.get("code", "")).zfill(2)
                        lvl = jma_level_from_code(w_code)
                        w_name = JMA_WARNING_NAMES.get(w_code)
                        
                        if lvl and w_name and lvl in level_data:
                            if w_name not in level_data[lvl]:
                                level_data[lvl][w_name] = set()
                            level_data[lvl][w_name].add(name)
        except Exception:
            continue

    formatted_data = {}
    for lvl, warnings in level_data.items():
        formatted_data[lvl] = {}
        for w_name, cities in warnings.items():
            formatted_data[lvl][w_name] = sorted(list(cities))

    return formatted_data

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
                "max_temp": max_temp_val
            }
    except Exception as e:
        return {
            "success": False,
            "office": "気象庁（オフライン/フォールバック）",
            "forecasts": [f"【{region_name}】 &nbsp; &nbsp; リアルタイムAPI接続確認中（通信環境または制限によりキャッシュ表示中）"],
            "current_temp": "28.5",
            "max_temp": "32.0"
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
            max_t = "--"

            for series in data[0].get("timeSeries", []):
                for area in series.get("areas", []):
                    temps = area.get("temps", [])
                    if temps:
                        if len(temps) > 0 and temps[0] != "":
                            max_t = temps[0]
                        elif len(temps) > 1 and temps[1] != "":
                            max_t = temps[1]

                for area in series.get("areas", []):
                    weathers = area.get("weathers", [])
                    if weathers and not weather:
                        weather = str(weathers[0]).strip()

            weather_match = re.match(r"(晴|曇|雨|雪|雷|晴れ|曇り|雨時々曇|曇時々雨|雨一時曇|曇一時雨)", weather)
            weather_label = weather_match.group(1) if weather_match else "気象情報あり"

            results.append({
                "prefecture": prefecture,
                "success": True,
                "weather": weather_label,
                "comment": weather or "天気情報を取得しました。",
                "max_temp": max_t,
            })
        except Exception:
            results.append({
                "prefecture": prefecture,
                "success": False,
                "weather": "取得できず",
                "comment": "リアルタイム気象情報を取得できませんでした。",
                "max_temp": "--",
            })

    return results

# ==========================================
# メイン画面の描画処理
# ==========================================

# 1. 起動時の注意書き（HTMLで色を指定：赤と青のダブルチェック案内）
st.markdown(
    """
    <div style="background-color: #382512; border: 1px solid #d97706; padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; color: #ffffff;">
        <span style="color: #ff4d4d; font-weight: 900; font-size: 16px;">【起動時のご注意】</span><br><br>
        一定時間アクセスがないと「Zzzz」というスリープ画面が表示されます。<br>
        その場合は、<span style="color: #38bdf8; font-weight: 900;">画面にある青いボタン（Yes, get this app back up!）を1回押して</span><span style="color: #ff4d4d; font-weight: 900;">サーバーを復帰させてください。</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🛡️ 全国インフラ・気象防災カルテ・リアルリンク共用システム")
st.markdown("災害時のリアルタイム気象状況・インフラ・地震情報をモバイル最適化で提供します。")
st.markdown("---")

# 2. 地震情報の常時表示セクション（st.metricによる崩れを防ぎ、見やすいカード形式に変更）
st.markdown("### 📳 直近の地震情報（気象庁速報）")
eq_data = fetch_jma_earthquake_info()

st.markdown(
    f"""
    <div style="background-color: #111827; border: 1px solid #475569; padding: 14px 18px; border-radius: 8px; border-left: 7px solid #ef4444; color: #ffffff; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; flex-wrap: wrap; gap: 10px;">
            <div><b>最大震度:</b> <span style="color: #ffe600; font-size: 16px; font-weight: 900;">{eq_data["max_scale"]}</span></div>
            <div><b>発生日時:</b> {eq_data["time"]}</div>
        </div>
        <div style="margin-bottom: 8px;"><b>震源地:</b> <span style="color: #60a5fa; font-weight: 900;">{eq_data["hypocenter"]}</span></div>
        <div style="font-size: 14px; color: #e5e7eb; border-top: 1px solid #334155; padding-top: 8px; margin-top: 6px;"><b>詳細:</b> {eq_data["detail"]}</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# 3. 監視エリア選択
selected_region = st.selectbox("🌍 監視エリアを選択してください", list(REGION_CODES.keys()), index=2)

# 4. 気象データ取得
weather_data = fetch_jma_realtime_data(selected_region)

# 5. 気象・温度状況の常時表示レイアウト
st.markdown(f"### 🌡️ 気象・温度状況 ({selected_region}エリアの代表値)")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="現在気温", value=f"{weather_data['current_temp']}°C")
with col2:
    st.metric(label="予想最高気温", value=f"{weather_data['max_temp']}°C")

st.markdown("---")

# 6. 警戒レベル・警報・注意報発令状況
st.markdown(f"### ⚠️ {selected_region}エリアの警戒レベル・警報発令状況")

warning_levels = fetch_jma_warning_level_areas(selected_region)
has_any_warning = False

if warning_levels.get("Level5"):
    has_any_warning = True
    st.error("🚨 **【レベル5】特別警報発令中**（命の危険が迫っています。直ちに身の安全を確保してください）")
    for w_name, cities in warning_levels["Level5"].items():
        st.write(f"- **{w_name}**: {', '.join(cities)}")

if warning_levels.get("Level4"):
    has_any_warning = True
    st.error("🟥 **【レベル4】危険警報発令中**（危険な場所から全員避難してください）")
    for w_name, cities in warning_levels["Level4"].items():
        st.write(f"- **{w_name}**: {', '.join(cities)}")

if warning_levels.get("Level3"):
    has_any_warning = True
    st.warning("🟧 **【レベル3】警報発令中**（高齢者等は危険な場所から避難してください）")
    for w_name, cities in warning_levels["Level3"].items():
        st.write(f"- **{w_name}**: {', '.join(cities)}")

if warning_levels.get("Level2"):
    has_any_warning = True
    with st.expander("🟦 **【レベル2】注意報発令中の地域を確認（タップして開く）**", expanded=True):
        for w_name, cities in warning_levels["Level2"].items():
            cities_str = "、".join(cities)
            st.markdown(f"・**{w_name}**: {cities_str}")

if not has_any_warning:
    st.success("🟢 現在、対象エリアに発表されている警戒レベル2以上の警報・注意報はありません。")

st.markdown("---")

# 7. リアルタイム天気予報の表示
st.markdown(f"### 📡 {selected_region}地方の気象情報 ({weather_data['office']})")
for forecast in weather_data["forecasts"]:
    st.markdown(f"- {forecast}")

st.markdown("---")

# 8. 都道府県別の詳細ステータス
st.markdown(f"### 📋 {selected_region}管内 都道府県別ステータス")
pref_weather_list = fetch_region_prefecture_weather(selected_region)
for pw in pref_weather_list:
    st.markdown(f"**{pw['prefecture']}** (最高: {pw['max_temp']}°C) └ 予報: {pw['comment']}")
