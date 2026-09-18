import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import json
import re

st.set_page_config(
    page_title="防災カルテ（全国インフラ・気象防災システム）", 
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
.link-card {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    border-left: 7px solid #10b981 !important;
    padding: 16px;
    border-radius: 8px;
    margin-top: 10px;
    margin-bottom: 20px;
}
div[data-testid="stExpander"] {
    background-color: #111827 !important;
    border: 1px solid #475569 !important;
    border-left: 7px solid #10b981 !important;
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
    "23": "低温注意報", "24": "霜注意報", "25": "着氷注意報", "26": "着雪注意報", "27": "そのほかの注意報",
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
    p2p_url = "https://api.p2pquake.net/v2/history?codes=551&limit=15"
    try:
        req = urllib.request.Request(p2p_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            p2p_data = json.loads(response.read().decode('utf-8'))
        
        if p2p_data and isinstance(p2p_data, list):
            quake_list = []
            p2p_scale_map = {
                10: "震度1", 20: "震度2", 30: "震度3", 40: "震度4",
                45: "震度5弱", 50: "震度5強", 55: "震度6弱", 60: "震度6強", 70: "震度7"
            }
            for item in p2p_data:
                eq = item.get("earthquake", {})
                hypo = eq.get("hypocenter", {})
                scale = eq.get("maxScale", -1)
                quake_list.append({
                    "time": eq.get("time", "日時不明"),
                    "hypocenter": hypo.get("name", "震源地不明"),
                    "max_scale": p2p_scale_map.get(scale, "不明"),
                    "magnitude": eq.get("magnitude", "--"),
                    "depth": hypo.get("depth", "--")
                })
            return {"success": True, "quakes": quake_list}
    except Exception:
        pass
    return {"success": False, "quakes": []}

@st.cache_data(ttl=300)
def fetch_jma_typhoon_info():
    url = "https://www.jma.go.jp/bosai/information/data/typhoon.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data if isinstance(data, list) else [data]
            if not items or (len(items) == 1 and not items[0]):
                return {"success": True, "data": []}
            return {"success": True, "data": items}
    except Exception:
        return {"success": False, "data": []}

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
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            office = data[0].get("publishingOffice", "気象庁")
            weather_forecasts = []
            
            pref_codes = list(REGION_PREFECTURES.get(region_name, {}).values())
            temps_list = []
            for p_code in pref_codes[:3]:
                p_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{p_code}.json"
                try:
                    p_req = urllib.request.Request(p_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(p_req, timeout=2) as p_res:
                        p_data = json.loads(p_res.read().decode('utf-8'))
                        for series in p_data[0].get("timeSeries", []):
                            for temp_area in series.get("areas", []):
                                t_vals = temp_area.get("temps", [])
                                for tv in t_vals:
                                    if tv != "":
                                        try: temps_list.append(float(tv))
                                        except: pass
                except:
                    pass
            
            if temps_list:
                current_temp = f"{sum(temps_list)/len(temps_list):.1f}"
                max_temp = f"{max(temps_list):.1f}"
            else:
                current_temp, max_temp = "--", "--"

            for series in data[0].get("timeSeries", []):
                for area in series.get("areas", []):
                    weathers = area.get("weathers", [])
                    if weathers:
                        w_text = re.sub(r'([雨曇晴雷])', r' &nbsp; \1 &nbsp; ', weathers[0])
                        weather_forecasts.append(f"【{area.get('area', {}).get('name', region_name)}】 &nbsp; {w_text}")
            return {"success": True, "office": office, "forecasts": weather_forecasts[:4], "current_temp": current_temp, "max_temp": max_temp}
    except Exception:
        return {"success": False, "office": "気象庁（オフライン）", "forecasts": [f"【{region_name}】 接続確認中"], "current_temp": "--", "max_temp": "--"}

@st.cache_data(ttl=300)
def fetch_region_prefecture_weather(region_name):
    results = []
    for prefecture, code in REGION_PREFECTURES.get(region_name, {}).items():
        url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
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
st.markdown("災害時のリアルタイム気象状況・インフラ・地震・台風情報を一元管理します。**※スマホ等でご利用の際は、画面を「横向き」にしていただくと全体がより見やすくなります。**")

with st.expander("📱 【タップして展開】 スマホ操作解説・横向き推奨・ご利用案内"):
    st.markdown("""
### 🎯 開発コンセプト
本システムは、大規模災害発生時におけるインフラ状況、気象警報、地震、台風などの重要情報を一元化し、迅速な初動対応と的確な意思決定を支援することを目的として開発されています。専門的な防災情報をシンプルかつ直感的に集約し、現場や行政、一般利用者の安全確保に貢献します。
""")

    # サーバー仕様を明記した警告ボックス
    st.markdown("""
    <div style="background-color: #1e293b; border: 1px solid #f59e0b; padding: 14px; border-radius: 8px; border-left: 6px solid #f59e0b; margin: 10px 0;">
        <div style="color: #fde047; font-weight: 900; font-size: 14px; margin-bottom: 6px;">
            ⏳ サーバー仕様によるスリープ復帰について（半日ほどアクセスがない場合）
        </div>
        <p style="color: #f8fafc; font-size: 13px; margin: 0; line-height: 1.6;">
            半日（約12時間）ほどアクセスがない状態が続くと、無料クラウドサーバーの仕様により自動的に一時的なスリープ状態になるため、再アクセス時に復帰処理が入ります。その際、画面に<b>クルクルと回る読み込み中のマークや進行状況を表すバー</b>が表示され、<b>起動に10〜30秒ほどかかる</b>ことがあります。<br>
            これはシステムの<b>サーバー仕様</b>による正常な動作ですので、画面が切り替わるまでそのままお待ちください（何度も再読み込みボタンを押すと、かえって時間がかかる場合があります）。
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
### 🔄 画面を横向きにすると見やすくなります
スマホの自動回転をオンにして**画面を横にしていただく**と、地図や各データが広く表示され、操作しやすくなります。

### 📲 フリーズ・スリープした時
長時間放置等で動かなくなった場合は、画面内の青い復帰ボタン（**「Yes, reload this page」**等）をタップして再読み込みしてください。

### 📌 基本的な使い方
中段のセレクトボックスで地域（関東・関西など）を切り替えると、地震・警戒レベル・温度が自動で切り替わります。最下部のリンク集から各種外部公式情報へアクセスできます。
""")

st.markdown("---")

# 🌀 台風情報カテゴリ
st.markdown("### 🌀 台風情報・進路 最新速報")

st.markdown("""
<div style="border-left: 7px solid #c2410c; padding-left: 14px; margin-top: 14px; margin-bottom: 12px; color: #fca5a5; font-size: 16px; font-weight: 900; text-align: left; line-height: 1.5;">
    🔴 【警戒】現在発表されている台風情報および今後の気象情報に厳重に警戒してください。
</div>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="link-card" style="margin-top: 4px; margin-bottom: 15px;">
        <b>🗺️ 気象庁 公式「台風情報（マルチリンガル対応）」</b><br>
        <p style="font-size:13px; color:#cbd5e1; margin: 6px 0 10px 0;">現在の中心位置・勢力・今後の進路予報を気象庁公式サイトで直接確認できます。</p>
        <a href="https://www.data.jma.go.jp/multi/cyclone/index.html?lang=jp" target="_blank">👉 気象庁 地図で台風情報</a>
    </div>
    """,
    unsafe_allow_html=True
)

typhoon_res = fetch_jma_typhoon_info()
if typhoon_res["success"] and typhoon_res["data"]:
    with st.expander("📁 台風データの詳細文面を確認（タップして展開）"):
        for i, item in enumerate(typhoon_res["data"]):
            head_title = item.get("headTitle", item.get("controlTitle", f"台風に関する情報 #{i+1}"))
            pub_office = item.get("publishingOffice", "気象庁")
            datetime_str = item.get("targetDateTime", item.get("dateTime", "直近の発表"))
            
            body_text = item.get("body", item.get("text", ""))
            if not body_text or len(str(body_text).strip()) < 5:
                body_text = "現在発表されている台風情報詳細です。気象庁公式サイトや最新の進路情報をご確認ください。"
            
            st.markdown(f"""
            <div style="background-color: #111827; border: 1px solid #475569; padding: 14px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #ef4444; text-align: left;">
                <div style="color: #fde047; font-weight: 900; font-size: 15px; margin-bottom: 6px;">{head_title}</div>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; color: #94a3b8; font-size: 12px; margin-bottom: 10px;">
                    <div><b>発表官署:</b> {pub_office}</div>
                    <div><b>情報日時:</b> {datetime_str}</div>
                </div>
                <hr style="border-color: #334155; margin: 8px 0;">
                <div style="color: #f8fafc; font-size: 13px; line-height: 1.6;">
                    {body_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background-color: #111827; border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; border-left: 5px solid #10b981; color: #e2e8f0; font-size: 13px; margin-bottom: 15px;">
        🟢 <b>現在発表されている台風情報はありません。</b>（平常時は詳細データ非表示）
    </div>
    """, unsafe_allow_html=True)

# 🚄 鉄道・道路インフラ情報のクイック案内セクション
st.markdown("### 🚄 鉄道・道路インフラの運行・規制状況")
st.markdown("""
<div style="background-color: #111827; border: 1px solid #334155; padding: 14px; border-radius: 8px; border-left: 7px solid #3b82f6; margin-bottom: 20px;">
    <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 12px; margin-top: 0;">
        台風や大雨などの気象レーダー・警報発令時は、交通機関に大きな影響が出る恐れがあります。お出かけ前や避難時には必ず最新の運行・規制情報をご確認ください。
    </p>
    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
        <a href="https://transit.yahoo.co.jp/diainfo/" target="_blank" style="background: #1e3a8a; color: #ffffff !important; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold;">
            🚆 Yahoo! 鉄道運行情報
        </a>
        <a href="https://www.jartic.or.jp/" target="_blank" style="background: #1e3a8a; color: #ffffff !important; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold;">
            🚗 JARTIC 道路交通情報
        </a>
        <a href="https://www.c-nexco.co.jp/" target="_blank" style="background: #1e3a8a; color: #ffffff !important; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold;">
            🛣️ NEXCO高速道路規制
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 📳 直近の地震情報 ＆ 本日の履歴")
eq_data = fetch_jma_earthquake_info()
if eq_data["success"] and eq_data["quakes"]:
    latest = eq_data["quakes"][0]
    st.markdown(f"""
    <div style="background-color: #1e293b; border: 1px solid #475569; padding: 14px; border-radius: 8px; border-left: 7px solid #ef4444; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div><b style="color: #ffffff;">最大震度:</b> <span style="color: #fde047; font-weight: 900; font-size: 1.1em;">{latest['max_scale']}</span></div>
            <div><b style="color: #ffffff;">発生日時:</b> <span style="color: #f8fafc;">{latest['time']}</span></div>
        </div>
        <div style="margin-top:6px;"><b style="color: #ffffff;">震源地:</b> <span style="color: #93c5fd; font-weight: 900; font-size: 1.1em;">{latest['hypocenter']}</span> <span style="font-size:12px; color:#cbd5e1;">(M{latest['magnitude']} / 深さ:{latest['depth']}km)</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    if len(eq_data["quakes"]) > 1:
        with st.expander("🔽 過去の地震履歴をさらに表示（タップして展開）"):
            for q in eq_data["quakes"][1:]:
                st.markdown(f"""
                <div style="background-color: #1e293b; border: 1px solid #475569; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #3b82f6;">
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                        <div><b style="color: #ffffff;">最大震度:</b> <span style="color: #fde047; font-weight: 900;">{q['max_scale']}</span></div>
                        <div><b style="color: #ffffff;">発生日時:</b> <span style="color: #f8fafc;">{q['time']}</span></div>
                    </div>
                    <div style="margin-top:4px;"><b style="color: #ffffff;">震源地:</b> <span style="color: #93c5fd; font-weight: 900;">{q['hypocenter']}</span> <span style="font-size:12px; color:#cbd5e1;">(M{q['magnitude']} / 深さ:{q['depth']}km)</span></div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.markdown('<div style="background-color: #1e293b; border: 1px solid #475569; padding: 14px; border-radius: 8px; border-left: 7px solid #ef4444; color: #ffffff;">サーバー混雑中・自動再試行待機中</div>', unsafe_allow_html=True)

st.markdown("---")

selected_region = st.selectbox("🌍 監視エリアを選択してください（地域を切り替えると各データが連動します）", list(REGION_CODES.keys()), index=2)

st.markdown("---")

st.markdown(f"### ⚠️ {selected_region}エリアの緊急警戒レベル（レベル3〜5）発令状況")
warnings = fetch_jma_warning_level_areas(selected_region)
has_warn = False
for lvl, color, title in [("Level5", "error", "🚨 【Level5】特別警報発令中（直ちに命を守る行動を）"), ("Level4", "error", "🟥 【Level4】危険警報発令中（危険な場所から全員避難）"), ("Level3", "warning", "🟧 【Level3】警報発令中（高齢者等は避難準備）")]:
    if warnings.get(lvl):
        has_warn = True
        getattr(st, color)(title)
        for w_name, cities in warnings[lvl].items(): st.write(f"- **{w_name}**: {', '.join(cities)}")
if not has_warn: st.success("🟢 現在、対象エリアに緊急警戒レベル（レベル3〜5）の警報は発表されていません。最新の気象情報にご注意ください。")

st.markdown("---")

st.markdown(f"### 🌡️ 気象・温度状況 ({selected_region}エリア・地域平均値)")
w_data = fetch_jma_realtime_data(selected_region)
c1, c2 = st.columns(2)
with c1: st.metric(label="エリア平均現在気温", value=f"{w_data['current_temp']}°C" if w_data['current_temp'] != "--" else "--")
with c2: st.metric(label="エリア予想最高気温", value=f"{w_data['max_temp']}°C" if w_data['max_temp'] != "--" else "--")

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
st.markdown("<p style='font-size:13px; color:#cbd5e1;'>選択した管内各県の天気概況と予想最高気温を一覧で確認できます。</p>", unsafe_allow_html=True)
for pw in fetch_region_prefecture_weather(selected_region):
    st.markdown(f"**{pw['prefecture']}** (最高: {pw['max_temp']}°C) └ {pw['comment']}")

st.markdown("---")

st.markdown(
    """
    <div class="link-card">
        <b>🔗 インフラ・交通・防災関連リンク集（公式リアルタイム情報）</b><br>
        <ul>
            <li><b>【台風情報】</b> <a href="https://www.data.jma.go.jp/multi/cyclone/index.html?lang=jp" target="_blank">気象庁 台風情報ページ</a></li>
            <li><b>【鉄道運行】</b> <a href="https://transit.yahoo.co.jp/diainfo/" target="_blank">Yahoo!路線情報（運行情報）</a></li>
            <li><b>【道路規制】</b> <a href="https://www.jartic.or.jp/" target="_blank">JARTIC 日本道路交通情報センター</a></li>
            <li><b>【雨雲ズーム】</b> <a href="https://weather.yahoo.co.jp/weather/zoomradar/" target="_blank">Yahoo!天気（雨雲ズームレーダー）</a></li>
            <li><b>【防災情報】</b> <a href="https://www.jma.go.jp/bosai/" target="_blank">気象庁 防災情報ポータル</a></li>
            <li><b>【河川水位】</b> <a href="https://www.river.go.jp/" target="_blank">川の防災情報（国土交通省）</a></li>
            <li><b>【危険度分布】</b> <a href="https://www.jma.go.jp/bosai/map.html" target="_blank">気象庁 キキクル</a></li>
            <li><b>【ハザード】</b> <a href="https://disaportal.gsi.go.jp/" target="_blank">ハザードマップポータルサイト</a></li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94a3b8; font-size: 12px; padding: 10px 0;">
        <p style="margin: 0;"><b>💻 システム開発・運営:</b> 全国インフラ・気象防災システム開発プロジェクトチーム</p>
        <p style="margin: 4px 0 0 0;">© 2026 National Infrastructure & Meteorological Disaster Prevention System. All Rights Reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)
