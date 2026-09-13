import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import json
import re

st.set_page_config(
    page_title="全国インフラ・気象防災カルテ・リアルリンク共用システム", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>

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

[data-testid="stAppViewContainer"] h1 {
    color: #ffffff !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
}

[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4 {
    color: #ffffff !important;
    font-weight: 900 !important;
}

@keyframes title-blink {
    0% { opacity: 1.0; }
    50% { opacity: 0.3; }
    100% { opacity: 1.0; }
}

.blinking-title {
    color: #ef4444 !important;
    font-weight: 900;
    font-size: 16px;
    animation: title-blink 2.0s infinite ease-in-out;
    display: inline-block;
}

.notice-card {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    border-left: 7px solid #ffe600 !important;
    padding: 14px 18px;
    border-radius: 8px;
    margin-bottom: 20px;
    color: #ffffff !important;
}

.link-card {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    border-left: 7px solid #10b981 !important;
    padding: 16px;
    border-radius: 8px;
    margin-top: 20px;
    margin-bottom: 20px;
}

div[data-testid="stExpander"] {
    background-color: #111827 !important;
    border: 1px solid #475569 !important;
    border-left: 7px solid #3b82f6 !important;
    border-radius: 8px !important;
}

div[data-testid="stExpander"] summary p {
    font-weight: 900 !important;
    color: #ffffff !important;
    font-size: 15px !important;
}

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

REGION_CODES = {
    "北海道": {"code": "016000", "lat": 43.0642, "lon": 141.3469, "center_name": "札幌（北海道中心）"},
    "東北": {"code": "040000", "lat": 38.2688, "lon": 140.8721, "center_name": "仙台（東北中心）"},
    "関東": {"code": "130000", "lat": 35.6895, "lon": 139.6917, "center_name": "東京（関東中心）"},
    "中部": {"code": "230000", "lat": 35.1802, "lon": 136.9066, "center_name": "名古屋（中部中心）"},
    "関西": {"code": "270000", "lat": 34.6937, "lon": 135.5022, "center_name": "大阪（関西中心）"},
    "四国": {"code": "360000", "lat": 33.8416, "lon": 132.7657, "center_name": "松山（四国中心）"},
    "九州": {"code": "400000", "lat": 33.6064, "lon": 130.4181, "center_name": "福岡（九州中心）"}
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
    "10": "Level2大雨注意報", "03": "Level3大雨警報", "43": "Level4大雨危険警報", "33": "Level5大雨特別警報",
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
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
        mapping = {}
        def walk(obj):
            if isinstance(obj, dict):
                code = obj.get("code")
                name = obj.get("name")
                if code is not None and name:
                    mapping[str(code)] = str(name)
                for value in obj.values(): walk(value)
            elif isinstance(obj, list):
                for value in obj: walk(value)
        walk(data)
        return mapping
    except Exception:
        return {}

@st.cache_data(ttl=60)
def fetch_jma_earthquake_info():
    url = "https://www.jma.go.jp/bosai/information/data/quake.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            quakes = json.loads(response.read().decode('utf-8'))
        if quakes and isinstance(quakes, list):
            latest = quakes[0]
            max_scale = latest.get("maxScale", "不明")
            scale_map = {
                "10": "震度1", "20": "震度2", "30": "震度3", "40": "震度4",
                "45": "震度5弱", "50": "震度5強", "55": "震度6弱", "60": "震度6強", "70": "震度7"
            }
            return {
                "success": True,
                "time": latest.get("at", "日時不明"),
                "hypocenter": latest.get("hypocenter", {}).get("name", "震源地不明"),
                "max_scale": scale_map.get(str(max_scale), f"震度({max_scale})"),
                "detail": latest.get("text", "直近の地震活動に特段の異常はありません。")
            }
    except Exception:
        pass
    return {"success": False, "time": "取得待機中", "hypocenter": "通信制限中", "max_scale": "--", "detail": "接続確認中"}

@st.cache_data(ttl=300)
def fetch_jma_warning_level_areas(region_name):
    office_codes = REGION_WARNING_OFFICES.get(region_name, [REGION_CODES[region_name]["code"]])
    area_names = fetch_jma_area_names()
    level_data = {"Level5": {}, "Level4": {}, "Level3": {}}

    for office_code in office_codes:
        warning_url = f"https://www.jma.go.jp/bosai/warning/data/warning/{office_code}.json"
        try:
            req = urllib.request.Request(warning_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            for area_type in data.get("areaTypes", []):
                for area in area_type.get("areas", []):
                    area_code = str(area.get("code", ""))
                    name = area_names.get(area_code)
                    if not name: continue
                    for w in area.get("warnings", []):
                        if w.get("status") in ["解除", "発表警報・注意報はなし", "", None]: continue
                        w_code = str(w.get("code", "")).zfill(2)
                        lvl = jma_level_from_code(w_code)
                        w_name = JMA_WARNING_NAMES.get(w_code)
                        if lvl in level_data and w_name:
                            level_data[lvl].setdefault(w_name, set()).add(name)
        except Exception:
            continue

    return {lvl: {w: sorted(list(cities)) for w, cities in warnings.items()} for lvl, warnings in level_data.items()}

@st.cache_data(ttl=300)
def fetch_jma_realtime_data(region_name):
    info = REGION_CODES.get(region_name, REGION_CODES["関東"])
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{info['code']}.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            office = data[0].get("publishingOffice", "気象庁")
            weather_forecasts = []
            current_temp, max_temp = "--", "--"

            for series in data[0].get("timeSeries", []):
                for temp_area in series.get("areas", []):
                    temps = temp_area.get("temps", [])
                    if temps:
                        if len(temps) > 0 and temps[0] != "": current_temp = temps[0]
                        if len(temps) > 1 and temps[1] != "": max_temp = temps[1]
                        elif len(temps) > 0 and temps[0] != "": max_temp = temps[0]
                for area in series.get("areas", []):
                    weathers = area.get("weathers", [])
                    if weathers:
                        w_text = re.sub(r'([雨曇晴雷])', r' &nbsp; \1 &nbsp; ', weathers[0])
                        weather_forecasts.append(f"【{area.get('area', {}).get('name', region_name)}】 &nbsp; {w_text}")
            return {"success": True, "office": office, "forecasts": weather_forecasts[:4], "current_temp": current_temp, "max_temp": max_temp}
    except Exception:
        return {"success": False, "office": "気象庁（オフライン）", "forecasts": [f"【{region_name}】 接続確認中"], "current_temp": "28.5", "max_temp": "32.0"}

@st.cache_data(ttl=300)
def fetch_region_prefecture_weather(region_name):
    results = []
    for prefecture, code in REGION_PREFECTURES.get(region_name, {}).items():
        url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
            weather, max_t = "", "--"
            for series in data[0].get("timeSeries", []):
                for area in series.get("areas", []):
                    temps = area.get("temps", [])
                    if temps and max_t == "--": max_t = temps[0] if temps[0] != "" else (temps[1] if len(temps)>1 else "--")
                for area in series.get("areas", []):
                    weathers = area.get("weathers", [])
                    if weathers and not weather: weather = str(weathers[0]).strip()
            wm = re.match(r"(晴|曇|雨|雪|雷|晴れ|曇り|雨時々曇|曇時々雨|雨一時曇|曇一時雨)", weather)
            results.append({"prefecture": prefecture, "weather": wm.group(1) if wm else "気象情報", "comment": weather or "取得完了", "max_temp": max_t})
        except Exception:
            results.append({"prefecture": prefecture, "weather": "取得できず", "comment": "通信エラー", "max_temp": "--"})
    return results

# 画面描画
st.title("🛡️ 全国インフラ・気象防災カルテ・リアルリンク共用システム")
st.markdown("災害時のリアルタイム気象状況・インフラ・地震情報をモバイル最適化で一元管理します。")

# 更新された折り畳み式ガイド（バッジの文字をくっきり太字＆影付きに変更）
with st.expander("📱 【タップして展開】 スマホ操作解説・ご利用案内・開発目的"):
    st.markdown("""
<div style="background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px;">
    <span style="background-color: #1d4ed8; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-weight: 900; font-size: 13px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); display: inline-block;">📲 画面表示の復帰</span>
    <p style="margin-top: 8px; margin-bottom: 0px; color: #f8fafc; line-height: 1.5;">一定時間アクセスがないと「Zzzz」のスリープ画面になります。その際は、画面に表示される青い復帰ボタン（<strong>「Yes, reload this page」</strong>または<strong>「Reconnect」</strong>）を１回押して再開してください。</p>
</div>

<div style="background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px;">
    <span style="background-color: #1d4ed8; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-weight: 900; font-size: 13px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); display: inline-block;">📱 ➡️ 💻 ワイド表示への切り替え</span>
    <p style="margin-top: 8px; margin-bottom: 0px; color: #f8fafc; line-height: 1.5;">スマホを「横向き」にするとデスクトップ表示（ワイド画面）に切り替わり、地図やエリア情報を見渡しやすくなります。</p>
</div>

<div style="background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px;">
    <span style="background-color: #1d4ed8; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-weight: 900; font-size: 13px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); display: inline-block;">📌 ショートカットの活用</span>
    <p style="margin-top: 8px; margin-bottom: 6px; color: #f8fafc; line-height: 1.5;">ホーム画面にショートカットを追加しておくと、いざという時にワンタップで瞬時に起動できます。</p>
    <div style="background-color: #0f172a; border: 1px solid #334155; padding: 8px 12px; border-radius: 4px; font-size: 13px; color: #cbd5e1;">
        <b>【追加のカンタン手順】</b><br>
        1. スマホのブラウザ（Safari / Chrome）のメニューボタン（共有・︙アイコン）をタップ<br>
        2. <b>「ホーム画面に追加」</b>を選択して保存するだけで完了です。
    </div>
</div>

<div style="background-color: #1e293b; border-left: 5px solid #10b981; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px;">
    <span style="background-color: #047857; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-weight: 900; font-size: 13px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); display: inline-block;">🎯 開発の目的</span>
    <p style="margin-top: 8px; margin-bottom: 0px; color: #f8fafc; line-height: 1.5;">気象庁の公式一次情報（地震速報・特別警報・キキクル）と、生活・交通インフラのリアルタイム状況を1つの画面で素早く確認できるように開発しています。</p>
</div>

<div style="background-color: #1e293b; border-left: 5px solid #10b981; padding: 10px 14px; border-radius: 6px; margin-bottom: 0px;">
    <span style="background-color: #047857; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-weight: 900; font-size: 13px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); display: inline-block;">💡 設計思想</span>
    <p style="margin-top: 8px; margin-bottom: 0px; color: #f8fafc; line-height: 1.5;">広告や不要な装飾を削ぎ落とし、災害時や電波が不安定な状況下でもスマホから、軽量かつ直感的に命を守る判断ができるよう最適化しています。</p>
</div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 📳 直近の地震情報（気象庁速報）")
st.markdown("<p style='font-size:13px; color:#94a3b8;'>日本国内で発生した直近の地震の規模、最大震度、および震源地を速報でお伝えします。</p>", unsafe_allow_html=True)
eq = fetch_jma_earthquake_info()
st.markdown(f'<div style="background-color: #111827; border: 1px solid #475569; padding: 14px; border-radius: 8px; border-left: 7px solid #ef4444;"><div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px;"><div><b>最大震度:</b> <span style="color: #ffe600; font-weight: 900;">{eq["max_scale"]}</span></div><div><b>発生日時:</b> {eq["time"]}</div></div><div style="margin-top:6px;"><b>震源地:</b> <span style="color: #60a5fa; font-weight: 900;">{eq["hypocenter"]}</span></div><div style="font-size: 13px; color: #e5e7eb; border-top: 1px solid #334155; margin-top: 6px; padding-top: 6px;"><b>解説:</b> {eq["detail"]}</div></div>', unsafe_allow_html=True)

st.markdown("---")

selected_region = st.selectbox("🌍 監視エリアを選択してください（地域を切り替えると各データが連動します）", list(REGION_CODES.keys()), index=2)

st.markdown("---")

st.markdown(f"### ⚠️ {selected_region}エリアの緊急警戒レベル（レベル3〜5）発令状況")
st.markdown("<p style='font-size:13px; color:#94a3b8;'>気象庁が発表している土砂災害や大雨等の厳戒警報・特別警報をレベル別に集約表示します。</p>", unsafe_allow_html=True)
warnings = fetch_jma_warning_level_areas(selected_region)
has_warn = False
for lvl, color, title in [("Level5", "error", "🚨 【Level5】特別警報発令中（直ちに命を守る行動を）"), ("Level4", "error", "🟥 【Level4】危険警報発令中（危険な場所から全員避難）"), ("Level3", "warning", "🟧 【Level3】警報発令中（高齢者等は避難準備）")]:
    if warnings.get(lvl):
        has_warn = True
        getattr(st, color)(title)
        for w_name, cities in warnings[lvl].items(): st.write(f"- **{w_name}**: {', '.join(cities)}")
if not has_warn: st.success("🟢 現在、対象エリアに緊急警戒レベル（レベル3〜5）の警報は発表されていません。")

st.markdown("---")

st.markdown(f"### 🌡️ 気象・温度状況 ({selected_region}エリア)")
w_data = fetch_jma_realtime_data(selected_region)
c1, c2 = st.columns(2)
with c1: st.metric(label="現在気温", value=f"{w_data['current_temp']}°C")
with c2: st.metric(label="予想最高気温", value=f"{w_data['max_temp']}°C")

st.markdown("---")

reg_info = REGION_CODES.get(selected_region, REGION_CODES["関東"])
st.markdown(f"### 🗺️ {selected_region}エリアの中心地図（中心：{reg_info['center_name']}）")
m = folium.Map(location=[reg_info["lat"], reg_info["lon"]], zoom_start=7, tiles="OpenStreetMap")
folium.Marker([reg_info["lat"], reg_info["lon"]], popup=selected_region, icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
st_folium(m, width="100%", height=300, key=f"map_{selected_region}")

st.markdown("---")

st.markdown(f"### 📡 {selected_region}地方の気象解説 ({w_data['office']})")
for fc in w_data["forecasts"]: st.markdown(f"- {fc}")

st.markdown("---")

st.markdown(f"### 📋 {selected_region}管内 都道府県別ステータス")
st.markdown("<p style='font-size:13px; color:#94a3b8;'>選択した管内各県の天気概況と予想最高気温を一覧で確認できます。</p>", unsafe_allow_html=True)
for pw in fetch_region_prefecture_weather(selected_region):
    st.markdown(f"**{pw['prefecture']}** (最高: {pw['max_temp']}°C) └ {pw['comment']}")

st.markdown("---")

st.markdown(
    """
    <div class="link-card">
        <b>🔗 インフラ・交通・防災関連リンク集（公式リアルタイム情報）</b><br>
        <p style='font-size:13px; color:#94a3b8; margin-top:4px;'>詳細な雨雲の動きや交通・河川情報をピンポイントで確認するための外部公式リンク集です。</p>
        <ul>
            <li><b>【雨雲ズーム】</b> <a href="https://weather.yahoo.co.jp/weather/zoomradar/" target="_blank">Yahoo!天気（雨雲ズームレーダー）</a>：高精度な雨雲の現在地と将来の動きを拡大表示</li>
            <li><b>【防災情報】</b> <a href="https://www.jma.go.jp/bosai/" target="_blank">気象庁 防災情報ポータル</a>：警報・台風・地震情報の総合窓口</li>
            <li><b>【道路規制】</b> <a href="https://www.jartic.or.jp/" target="_blank">JARTIC 日本道路交通情報センター</a>：高速道路・一般道の通行止め情報</li>
            <li><b>【鉄道運行】</b> <a href="https://transit.yahoo.co.jp/diainfo/" target="_blank">Yahoo!路線情報（運行情報）</a>：全国の鉄道遅延・運休状況</li>
            <li><b>【河川水位】</b> <a href="https://www.river.go.jp/" target="_blank">川の防災情報（国土交通省）</a>：河川水位・ライブカメラ・ダム情報</li>
            <li><b>【危険度分布】</b> <a href="https://www.jma.go.jp/bosai/map.html" target="_blank">気象庁 キキクル</a>：土砂災害・浸水害・洪水の危険度マップ</li>
            <li><b>【ハザード】</b> <a href="https://disaportal.gsi.go.jp/" target="_blank">ハザードマップポータルサイト</a>：避難所や災害リスクの全國家屋情報</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)
