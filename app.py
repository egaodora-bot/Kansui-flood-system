import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import json
import re

st.set_page_config(
    page_title="気象防災カルテ・インフラリアルリンクシステム", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 最初のデザインにあった「左側のカラーバー」「タイトルサイズ」「見出し」を綺麗に再現するカスタムCSS
st.markdown("""
<style>
    /* メインタイトルを大きく目立たせる */
    .custom-main-title {
        font-size: 28px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .custom-sub-title {
        font-size: 14px;
        color: #cbd5e1;
        margin-top: 4px;
        margin-bottom: 15px;
    }
    /* ガイドボックスの左側に青・緑のアクセントラインを引くスタイリッシュなデザイン */
    .guide-box-blue {
        border-left: 4px solid #60a5fa;
        background-color: rgba(96, 165, 250, 0.08);
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 0 4px 4px 0;
    }
    .guide-title {
        font-size: 13px;
        font-weight: bold;
        color: #60a5fa;
        margin-bottom: 4px;
    }
    .guide-text {
        font-size: 13px;
        color: #e2e8f0;
        line-height: 1.6;
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

@st.cache_data(ttl=0)
def fetch_jma_warning_level_areas_robust(region_name: str):
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
                        w_text = re.sub(r'([雨曇晴雷])', r' \1 ', weathers[0])
                        weather_forecasts.append(f"【{area.get('area', {}).get('name', region_name)}】 {w_text}")
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

# 画面描画（タイトルとサブタイトル）
st.markdown('<p class="custom-main-title">🛡️ 気象防災カルテ・インフラリアルリンクシステム</p>', unsafe_allow_html=True)
st.markdown('<p class="custom-sub-title">災害時のリアルタイム気象状況・インフラ・地震・台風・キキクル（危険度分布）連動情報を一元管理します。</p>', unsafe_allow_html=True)

# 操作ガイド（折りたたみ可能な展開表示 ＆ 左側の青いアクセントライン付きボックス）
with st.expander("📖 2軸表示システム設計仕様 & 操作ガイドのご案内", expanded=True):
    st.markdown("""
    <div class="guide-box-blue">
        <div class="guide-title">🛡️ 1. 警報とキキクルの独立同時表示（2軸並列設計）</div>
        <div class="guide-text">監視エリアを選択すると、「市区町村単位の気象庁警報・注意報ベース」と、実況・解析に基づく「キキクル（危険度分布）の現象別リアルタイム評価」の両方を同時に切り替え連動して表示します。</div>
    </div>
    
    <div class="guide-box-blue">
        <div class="guide-title">🗺️ 2. 地図およびエリア連動の操作方法について</div>
        <div class="guide-text">上のセレクトボックスでエリアを選択するか、あるいは地図上の各地域や都道府県を選択・クリックしていただくことで、連動して下部の詳細な防災データや機器ステータスが切り替わります。</div>
    </div>
    
    <div class="guide-box-blue">
        <div class="guide-title">📱 3. スマートフォン等でのご利用時の注意</div>
        <div class="guide-text">端末を「横向き」にしていただくと、地図および各詳細データやリンクがより一覧しやすくなります。ぜひお試しください。</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 監視エリア選択
selected_region = st.selectbox("🌍 監視エリアを選択してください（地域を切り替えると各データが連動します）", list(REGION_CODES.keys()), index=2, key="region_selector")

st.markdown("---")

# 2軸並列ダッシュボード
st.markdown(f"## 📊 【{selected_region}エリア】 2軸リアルタイム警戒ダッシュボード")
st.markdown("選択されたエリアに対応する「気象庁の警報レベル」と「キキクルの危険度」を並列で確認できます。")

col_axis1, col_axis2 = st.columns(2, gap="medium")

# 軸1：市区町村単位の気象庁 警戒レベル情報
with col_axis1:
    st.markdown("### ⚠️ 1. 気象庁 警戒レベル")
    st.caption("市区町村ごとの警報・注意報ベース")
    
    warnings = fetch_jma_warning_level_areas_robust(selected_region)
    has_warn = False
    
    warning_texts = []
    for lvl, title in [("Level5", "🚨 Level5特別警報"), ("Level4", "🟥 Level4危険警報")]:
        if warnings.get(lvl):
            has_warn = True
            warning_texts.append(f"**{title}**")
            for w_name, cities in warnings[lvl].items():
                warning_texts.append(f"- {w_name}: {', '.join(cities)}")

    if not has_warn:
        level3_exist = warnings.get("Level3", {})
        if level3_exist:
            warning_texts.append("**🟧 Level3警報発表中**")
            for w_name, cities in level3_exist.items():
                warning_texts.append(f"- {w_name}: {', '.join(cities)}")
        else:
            warning_texts.append(f"🟢 {selected_region}エリアの市区町村においてレベル3以上の警報発表はありません。")

    with st.container(border=True):
        for line in warning_texts:
            st.markdown(line)

# 軸2：キキクル（危険度分布）の連動エリア評価
with col_axis2:
    st.markdown("### 🔴 2. キキクル危険度")
    st.caption("メッシュ・実況解析ベース（現象別）")
    
    with st.container(border=True):
        st.markdown("**【キキクル解説】**")
        st.markdown("選択したエリアにおける大雨時の災害発生危険度をメッシュ単位で評価した気象庁の危険度分布です。")
        st.markdown(f"**{selected_region}のキキクル実況確認：**")
        
        st.markdown("[🔴 土砂キキクル（土砂災害）を開く](https://www.jma.go.jp/bosai/map.html#6/35.252/136.245/&elem=warning)")
        st.markdown("[🔵 浸水キキクル（浸水害）を開く](https://www.jma.go.jp/bosai/map.html#6/35.252/136.245/&elem=inundation)")
        st.markdown("[🟢 洪水キキクル（洪水災害）を開く](https://www.jma.go.jp/bosai/map.html#6/35.252/136.245/&elem=flood)")

# 共通凡例ガイド
with st.container(border=True):
    st.markdown("**💡 警戒レベルおよびキキクルの色別の意味（共通凡例）：**")
    st.markdown("""
    * **🟣 紫 (レベル5):** 命の危険・緊急安全確保
    * **🔴 赤 (Level4):** 極めて危険・避難指示
    * **🟡 黄 (Level3):** 警戒・高齢者等避難
    * **🔵 青/白:** 注意・安全
    """)

st.markdown("---")

# 地図表示セクション
reg_info = REGION_CODES.get(selected_region, REGION_CODES["関東"])
st.markdown(f"### 🗺️ {selected_region}エリアの中心地図（中心：{reg_info['center_name']}）")
st.caption("※地図上のピンや都道府県を選択すると、下部の管内都道府県別ステータス等の詳細データが連動して表示されます。")
m = folium.Map(location=[reg_info["lat"], reg_info["lon"]], zoom_start=7, tiles="OpenStreetMap")
folium.Marker([reg_info["lat"], reg_info["lon"]], popup=selected_region, icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
st_folium(m, width="100%", height=300, key=f"map_{selected_region}")

st.markdown("---")

# 気象情報・地震セクション
st.markdown("### 📳 直近の地震情報 ＆ 気象状況")
eq_data = fetch_jma_earthquake_info()
if eq_data["success"] and eq_data["quakes"]:
    latest = eq_data["quakes"][0]
    with st.container(border=True):
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown(f"**最大震度:** :red[**{latest['max_scale']}**]")
            st.markdown(f"**震源地:** {latest['hypocenter']}")
        with col_e2:
            st.markdown(f"**発生日時:** {latest['time']}")
            st.markdown(f"**規模:** M{latest['magnitude']} / 深さ:{latest['depth']}km")
else:
    st.info("地震情報取得中...")

c1, c2 = st.columns(2)
w_data = fetch_jma_realtime_data(selected_region)
with c1: st.metric(label="エリア平均現在気温", value=f"{w_data['current_temp']}°C" if w_data['current_temp'] != "--" else "--")
with c2: st.metric(label="エリア予想最高気温", value=f"{w_data['max_temp']}°C" if w_data['max_temp'] != "--" else "--")

st.markdown("---")

st.markdown(f"### 📡 {selected_region}地方の気象解説 ({w_data['office']})")
for fc in w_data["forecasts"]: st.markdown(f"- {fc}")

st.markdown("---")

st.markdown(f"### 📋 {selected_region}管内 都道府県別ステータス")
for pw in fetch_region_prefecture_weather(selected_region):
    st.markdown(f"- **{pw['prefecture']}** (最高: {pw['max_temp']}°C) └ {pw['comment']}")

st.markdown("---")

# インフラ・防災リンク集
with st.container(border=True):
    st.markdown("**🔗 インフラ・交通・防災・キキクル・放射線関連リンク集（公式リアルタイム情報）**")
    st.markdown("""
    * **【キキクル総合】** [気象庁 キキクル（危険度分布ポータル）](https://www.jma.go.jp/bosai/map.html)
    * **【台風情報】** [気象庁 台風情報ページ](https://www.jma.go.jp/bosai/multi/cyclone/index.html?lang=jp)
    * **【道路規制】** [JARTIC 日本道路交通情報センター](https://www.jartic.or.jp/)
    * **【雨雲ズーム】** [Yahoo!天気（雨雲ズームレーダー）](https://weather.yahoo.co.jp/weather/zoomradar/)
    * **【防災情報】** [気象庁 防災情報ポータル](https://www.jma.go.jp/bosai/)
    * **【河川水位】** [川の防災情報（国土交通省）](https://www.river.go.jp/)
    * **【放射線状況】** [原子力規制庁 放射線モニタリング情報 (RAMIS)](https://www.ramis.nra.go.jp/)
    """)

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94a3b8; font-size: 12px; padding: 10px 0;">
        <p style="margin: 0;"><b>💻 システム開発・運営:</b> 気象防災カルテ・インフラリアルリンクシステム開発プロジェクトチーム</p>
        <p style="margin: 4px 0 0 0;">© 2026 Meteorological Disaster Prevention & Infrastructure Real-Link System. All Rights Reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)
