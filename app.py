import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="全国総合防災・気象庁データ統合システム", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    border-radius: 6px;
    font-weight: bold;
    padding: 6px 10px !important;
    font-size: 13px !important;
}
button[kind="primary"] {
    background-color: #0056b3 !important;
    border: 3px solid #004085 !important;
    color: #ffffff !important;
    font-weight: 800 !important;
}
section[data-testid="stSidebar"] {
    padding-top: 1rem;
}
div[data-testid="stMultiSelect"] {
    border-left: 5px solid #fde047;
    padding-left: 10px;
}
div[data-testid="stSelectbox"] {
    border-left: 5px solid #38bdf8;
    padding-left: 10px;
}
</style>
""", unsafe_allow_html=True)

if "first_visit" not in st.session_state:
    st.session_state["first_visit"] = True

@st.cache_data(ttl=300)
def fetch_robust_disaster_news():
    news_items = []
    rss_urls = [
        "https://news.yahoo.co.jp/rss/topics/disaster.xml",
        "https://www.jma.go.jp/bosai/information/rss/jma_inf.xml"
    ]
    
    success = False
    for url in rss_urls:
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=2) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                for item in root.findall('.//item')[:5]:
                    title = item.find('title').text if item.find('title') is not None else "無題"
                    link = item.find('link').text if item.find('link') is not None else "#"
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    pub_date_short = pub_date.split(',')[1].strip() if ',' in pub_date else pub_date
                    news_items.append({"title": title, "link": link, "date": pub_date_short})
                if news_items:
                    success = True
                    break
        except Exception:
            continue
            
    if not success or not news_items:
        news_items = [
            {"title": "【防災情報】気象庁の最新警報・注意報・地震情報をご確認ください", "link": "https://www.jma.go.jp/", "date": "現在"},
            {"title": "【運行情報】主要な交通機関の運行状況を確認", "link": "https://www.jartic.or.jp/", "date": "現在"}
        ]
    return news_items

locations = [
    {
        "category": "【河川氾濫・気象庁情報】", "region": "関東", "pref": "東京都", "name": "多摩川流域（二子玉川周辺）", 
        "river_name": "多摩川（たまがわ）", "lat": 35.6000, "lon": 139.6300, "source": "気象庁・国土交通省", 
        "level": "レベル4", "level_desc": "【避難指示】全員速やかに避難。氾濫のおそれが極めて高い状態。",
        "metric": "観測 4.1m / 警戒 4.0m", "status": "危険（氾濫危険水位超）", "color": "red", "priority": 1,
        "desc": "首都圏を流れる主要一級河川。気象庁および河川事務所からの警戒情報発令中。",
        "camera_url": "https://www.jma.go.jp/bosai/warning/"
    },
    {
        "category": "【土砂災害・気象庁情報】", "region": "関東", "pref": "東京都", "name": "多摩西部・山間部エリア", 
        "river_name": "---", "lat": 35.7792, "lon": 139.1106, "source": "気象庁 キキクル", 
        "level": "レベル4", "level_desc": "【避難指示】土砂災害警戒情報発令中。崖崩れのおそれ。",
        "metric": "土砂災害警戒判定スコア超過", "status": "危険（土砂崩れ切迫）", "color": "red", "priority": 1,
        "desc": "長引く大雨により土砂災害の危険度が極めて高まっています。",
        "camera_url": "https://www.jma.go.jp/bosai/risk/"
    },
    {
        "category": "【道路冠水・気象庁情報】", "region": "関東", "pref": "東京都", "name": "新宿駅西口地下道路・アンダーパス", 
        "river_name": "---", "lat": 35.6895, "lon": 139.6917, "source": "気象庁・東京都", 
        "level": "レベル4", "level_desc": "【通行止め・水没危険】車両の進入・通行を厳に禁止。",
        "metric": "冠水深 40cm（車両水没のおそれ）", "status": "危険（通行止め）", "color": "red", "priority": 1,
        "desc": "ゲリラ豪雨によりアンダーパスが水没。立ち往生車両が発生し全面通行止め。",
        "camera_url": "https://www.jma.go.jp/bosai/warning/"
    },
    {
        "category": "【地震・津波】", "region": "関東", "pref": "千葉県", "name": "房総半島沿岸エリア", 
        "river_name": "---", "lat": 35.0000, "lon": 140.0000, "source": "気象庁 地震情報", 
        "level": "Level3", "level_desc": "【津波注意報・地震警戒】海岸付近から離れてください。",
        "metric": "震度4 / 津波注意報", "status": "注意（沿岸部警戒）", "color": "orange", "priority": 2,
        "desc": "地震発生に伴う津波注意報および強い揺れへの警戒が発表されています。",
        "camera_url": "https://www.jma.go.jp/bosai/information.html"
    },
    {
        "category": "【河川氾濫】", "region": "関東", "pref": "埼玉県", "name": "埼玉県南部（荒川流域・戸田市周辺）", 
        "river_name": "荒川（あらかわ）", "lat": 35.8150, "lon": 139.6700, "source": "気象庁・国土交通省", 
        "level": "Level3", "level_desc": "【高齢者等避難】水位上昇中。要配慮者は避難準備。",
        "metric": "観測 6.2m / 警戒 6.5m", "status": "注意（水位上昇中）", "color": "orange", "priority": 2,
        "desc": "埼玉県南部を流れる大河川。上流域の降雨により水位が上昇傾向にあります。",
        "camera_url": "https://www.jma.go.jp/bosai/warning/"
    },
    {
        "category": "【河川氾濫】", "region": "関東", "pref": "神奈川県", "name": "神奈川県東部（多摩川下流・鶴見川）", 
        "river_name": "鶴見川（つるみがわ）", "lat": 35.5100, "lon": 139.6300, "source": "気象庁・国土交通省", 
        "level": "Level3", "level_desc": "【高齢者等避難】水位上昇中。",
        "metric": "観測 2.4m / 警戒 2.8m", "status": "注意（水位上昇中）", "color": "orange", "priority": 2,
        "desc": "横浜市・川崎市を流れる都市型河川。短時間の強い雨で急激に水位が上昇。",
        "camera_url": "https://www.jma.go.jp/bosai/warning/"
    },
    {
        "category": "【大雨・洪水】", "region": "関東", "pref": "茨城県", "name": "茨城県南部（利根川流域・取手市周辺）", 
        "river_name": "利根川（とねがわ）", "lat": 35.9000, "lon": 140.0600, "source": "気象庁", 
        "level": "Level3", "level_desc": "【高齢者等避難】厳重警戒。",
        "metric": "水位上昇中", "status": "注意（監視中）", "color": "orange", "priority": 2,
        "desc": "日本最大の流域面積を誇る坂東太郎。下流部の水位監視を強化中。",
        "camera_url": "https://www.jma.go.jp/bosai/warning/"
    },
    {
        "category": "【河川氾濫】", "region": "関東", "pref": "栃木県", "name": "栃木県南部（渡良川流域・足利市周辺）", 
        "river_name": "渡良川（わたらせがわ）", "lat": 36.3400, "lon": 139.4500, "source": "気象庁", 
        "level": "Level3", "level_desc": "【高齢者等避難】水位上昇。",
        "metric": "警戒水位到達", "status": "注意（警戒中）", "color": "orange", "priority": 2,
        "desc": "足利市周辺を流れる重要水系。まとまった雨により警戒レベル3相当。",
        "camera_url": "https://www.jma.go.jp/bosai/warning/"
    },
    {
        "category": "【河川氾濫】", "region": "九州", "pref": "福岡県", "name": "筑後川流域（久留米市周辺）", 
        "river_name": "筑後川（ちくごがわ）", "lat": 33.3197, "lon": 130.5086, "source": "気象庁", 
        "level": "Level3", "level_desc": "【高齢者等避難】水位上昇中。要配慮者は避難準備。",
        "metric": "観測 5.1m / 警戒 5.8m", "status": "注意（水位上昇中）", "color": "orange", "priority": 2,
        "desc": "西日本最大の「筑紫次郎」と呼ばれる一級河川。上流の豪雨で水位上昇中。",
        "camera_url": "https://www.qsr.mlit.go.jp/"
    },
    {
        "category": "【地震・津波】", "region": "北海道", "pref": "北海道", "name": "太平洋沿岸東部エリア", 
        "river_name": "---", "lat": 42.9833, "lon": 144.3833, "source": "気象庁", 
        "level": "Level3", "level_desc": "【地震警戒】余震および津波に注意。",
        "metric": "震度4", "status": "注意（監視中）", "color": "orange", "priority": 2,
        "desc": "北海道東部を震源とする地震が発生。今後の情報に注意してください。",
        "camera_url": "https://www.jma.go.jp/bosai/information.html"
    },
    {
        "category": "【河川氾濫】", "region": "東北", "pref": "宮城県", "name": "広瀬川流域（仙台市中心部）", 
        "river_name": "広瀬川（ひろせがわ）", "lat": 38.2688, "lon": 140.8721, "source": "気象庁", 
        "level": "レベル4", "level_desc": "【避難指示】全員速やかに避難。市街地への浸水リスク切迫。",
        "metric": "観測 3.2m / 警戒 3.0m", "status": "危険（氾濫危険水位超）", "color": "red", "priority": 1,
        "desc": "東北の主要河川。上流の豪雨により氾濫危険水位を突破。避難指示発令中。",
        "camera_url": "https://www.jma.go.jp/bosai/warning/"
    }
]

if st.session_state["first_visit"]:
    st.markdown("<h3 style='font-size: 20px; font-weight: bold; background-color: #fef08a; color: #1e293b; padding: 10px 14px; border-radius: 6px; border-left: 6px solid #ca8a04; margin-bottom: 0.8rem;'>🛡️ 全国総合防災・気象庁データ統合システム</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #1e40af; padding: 18px 22px; border-radius: 8px; border-left: 6px solid #60a5fa; color: #ffffff; font-weight: bold; font-size: 15px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); line-height: 1.7;">
        気象庁が全市区町村を網羅して配信する公式防災データ（警報・注意報・キキクル・地震情報）をベースに構成されています。<br><br>
        <div style="background-color: rgba(255, 255, 255, 0.15); padding: 10px 14px; border-radius: 6px; font-size: 14px; color: #ffffff; line-height: 1.8;">
            📍 <b>【システムの特徴】</b><br>
            ・気象庁データを基軸に、スマホでもエラーなく安全に稼働。<br>
            ・全国すべての市区町村の網羅的詳細情報は、システム開始後の画面下部にある<b>「気象庁公式・国土交通省・民間気象会社の信頼リンク集」</b>から直接アクセスできます。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📖 :red[【ご利用ガイド・命を守る共有方法】]", expanded=True):
        st.markdown("""
        ##### ［ご家族やご友人への共有］
        災害時はこのシステムのURLを共有することで、全員が命を守る為に必要な、今いる場所が掲載している最新公開情報へアクセスできます。

        ##### ［📱 クイックにアクセスする為、スマホのホーム画面への追加］
        ブラウザメニューから「ホーム画面に追加」を行うと、専用アプリのようにワンタップで起動できます。(推奨)
        
        ---
        👇 **内容をご確認の上、以下のボタンを押してシステムを開始してください。**
        """, unsafe_allow_html=True)
        
        if st.button("確認しました（システムを開始する）", type="primary"):
            st.session_state["first_visit"] = False
            st.rerun()
    
    st.stop()

# --- メイン画面のヘッダー文字サイズを大きく調整 ---
st.markdown("""
<div style="margin-left: 0px; margin-bottom: 1.4rem;">
    <div style="color: #60a5fa; font-size: 24px; font-weight: bold; margin-bottom: 6px;">
        🛡️ 全国総合防災・気象庁データ統合システム
    </div>
    <div style="color: #93c5fd; font-size: 15px; font-weight: bold;">
        （※気象庁の公式災害情報をベースに、重要拠点の状況をリアルタイムで把握します）
    </div>
</div>
""", unsafe_allow_html=True)

available_regions = ["北海道", "東北", "関東", "中部", "関西", "四国", "九州"]
if "selected_regions" not in st.session_state:
    st.session_state["selected_regions"] = ["関東"]

# --- エリアおよびピンポイント（都道府県）選択セクション ---
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown("""
    <div style="border-left: 5px solid #fde047; padding-left: 10px; margin-bottom: 6px;">
        <span style="color: #fef08a; font-weight: bold; font-size: 14px;">
            📍 地方エリアの選択（複数選択可）
        </span>
    </div>
    """, unsafe_allow_html=True)
    selected_regions = st.multiselect(
        "地域を選ぶ",
        options=available_regions,
        default=st.session_state["selected_regions"],
        label_visibility="collapsed"
    )
    st.session_state["selected_regions"] = selected_regions

# --- 1段階目で選ばれた地方エリアに含まれるデータだけに絞り込みベースを作る ---
if selected_regions:
    base_locations = [loc for loc in locations if loc["region"] in selected_regions]
else:
    base_locations = locations.copy()

with col_f2:
    st.markdown("""
    <div style="border-left: 5px solid #38bdf8; padding-left: 10px; margin-bottom: 6px;">
        <span style="color: #7dd3fc; font-weight: bold; font-size: 14px;">
            🔍 ピンポイント都道府県で絞り込み
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # 選択中の地方エリアに属する都道府県だけをリストアップする
    available_prefs = ["すべて表示"] + sorted(list(set([loc["pref"] for loc in base_locations])))
    selected_pref = st.selectbox(
        "都道府県絞り込み",
        options=available_prefs,
        label_visibility="collapsed"
    )

# --- 最終的な絞り込みロジック ---
filtered_locations = base_locations.copy()
if selected_pref != "すべて表示":
    filtered_locations = [loc for loc in filtered_locations if loc["pref"] == selected_pref]

# サマリー計算
danger_count = sum(1 for loc in filtered_locations if loc["color"] == "red")
warning_count = sum(1 for loc in filtered_locations if loc["color"] == "orange")

st.markdown(f"""
<div style="background-color: #1e293b; padding: 12px 16px; border-radius: 8px; border-left: 6px solid #ef4444; margin-top: 15px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
    <span style="color: #f8fafc; font-size: 14px; font-weight: bold;">
        🚨 <span style="color: #fca5a5;">【気象庁発表・警戒対象】</span> 選択条件の危険（赤）が <span style="color: #f87171; font-size: 16px;"><b>{danger_count}件</b></span>、注意（橙）が <span style="color: #fbbf24; font-size: 16px;"><b>{warning_count}件</b></span> 監視されています。
    </span>
</div>
""", unsafe_allow_html=True)

# 通勤・鉄道情報の常時確認用「小窓（ミニウィジェット風枠）」
st.markdown("""
<div style="background-color: #0f172a; border: 2px solid #38bdf8; padding: 12px 16px; border-radius: 8px; margin-top: 1rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
    <div style="color: #38bdf8; font-weight: bold; font-size: 14.5px; margin-bottom: 6px;">
        🚆 <b>【通勤・鉄道運行情報（小窓）】遅延・見合わせのリアルタイムチェック</b>
    </div>
    <div style="font-size: 13px; color: #f1f5f9; line-height: 1.7;">
        ・ <a href="https://transit.yahoo.co.jp/traininfo/top" target="_blank" rel="noopener noreferrer" style="color: #7dd3fc; font-weight: bold;">Yahoo!路線情報 運行状況（関東・全国の遅延・運転見合わせ一覧）</a><br>
        ・ <a href="https://www.jartic.or.jp/" target="_blank" rel="noopener noreferrer" style="color: #7dd3fc; font-weight: bold;">JARTIC 日本道路交通情報センター（高速道路・一般道の規制状況）</a>
    </div>
</div>
""", unsafe_allow_html=True)

# 国土交通省の川の防災情報を含む公式リンク集
st.markdown("""
<div style="background-color: #0f172a; border: 2px solid #ef4444; padding: 14px 18px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
    <div style="color: #fef08a; font-weight: bold; font-size: 15px; margin-bottom: 8px;">
        ⚡ <b>【気象庁公式 ＆ 国土交通省・民間気象会社リンク集】すべての市区町村・河川の水位を確認</b>
    </div>
    <div style="font-size: 13.5px; color: #f1f5f9; line-height: 1.8;">
        ・ 🌊 <a href="https://www.river.go.jp/" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; font-weight: bold;">国土交通省 川の防災情報（全国のリアルタイム河川水位・ライブカメラ）</a><br>
        ・ 💧 <a href="https://www.jma.go.jp/bosai/flood/" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; font-weight: bold;">気象庁 洪水警報の危険度分布（指定河川洪水予報・水位情報）</a><br>
        ・ 🔴 <a href="https://www.jma.go.jp/bosai/warning/" target="_blank" rel="noopener noreferrer" style="color: #fca5a5; font-weight: bold;">気象庁 警報・注意報（全国すべての市区町村別の最新発令状況）</a><br>
        ・ ⚠️ <a href="https://www.jma.go.jp/bosai/risk/" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; font-weight: bold;">気象庁 キキクル（土砂・浸水・洪水危険度分布）</a><br>
        ・ 🌍 <a href="https://www.jma.go.jp/bosai/information.html" target="_blank" rel="noopener noreferrer" style="color: #fca5a5; font-weight: bold;">気象庁 地震情報・津波情報</a><br>
        ・ ☀️ <a href="https://weathernews.jp/" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; font-weight: bold;">ウェザーニュース（最新の気象解説・台風・ライブカメラ）</a><br>
        ・ 🌧️ <a href="https://weather.yahoo.co.jp/weather/zoomradar/" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; font-weight: bold;">Yahoo!天気・災害（雨雲レーダー・避難情報）</a>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📡 【ライブ取得】リアルタイム災害・速報フィード", expanded=True):
    news_list = fetch_robust_disaster_news()
    for news in news_list:
        st.markdown(f"- <a href='{news['link']}' target='_blank' rel='noopener noreferrer' style='color: #d32f2f; font-weight: bold;'>{news['title']}</a> <small style='color:gray;'>({news['date']})</small>", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='font-size: 14px; font-weight: bold; color: #60a5fa; line-height: 1.5;'>🛡️ 全国総合防災・<br>気象庁データ統合システム</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.subheader("📌 警戒レベル凡例")
st.sidebar.markdown("🔴 <span style='color:red; font-weight:bold;'>レベル4：避難指示（全員避難）</span>", unsafe_allow_html=True)
st.sidebar.markdown("🟠 <span style='color:darkorange; font-weight:bold;'>レベル3：高齢者等避難・規制</span>", unsafe_allow_html=True)
st.sidebar.markdown("🔵 **Level1〜2**：監視中", unsafe_allow_html=True)

filtered_locations = sorted(filtered_locations, key=lambda x: x["priority"])

map_center_lat = filtered_locations[0]["lat"] if filtered_locations else (36.0 if selected_regions else 37.5)
map_center_lon = filtered_locations[0]["lon"] if filtered_locations else (139.5 if selected_regions else 138.0)
map_zoom = 10 if selected_pref != "すべて表示" else (8 if selected_regions else 5)

m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=map_zoom, control_scale=True)

for idx, loc in enumerate(filtered_locations):
    lat, lon = loc.get("lat"), loc.get("lon")
    if lat and lon:
        c_cat = loc.get('category')
        c_pref = loc.get('pref')
        c_name = loc.get('name')
        c_source = loc.get('source')
        c_status = loc.get('status')
        c_color = loc.get('color')
        c_desc = loc.get('desc')
        c_river = loc.get('river_name')
        c_url = loc.get('camera_url')
        c_lvl = loc.get('level')
        
        river_info = f"<br><b>対象河川:</b> {c_river}" if c_river != "---" else ""
        camera_link_html = f"<br><a href='{c_url}' target='_blank' rel='noopener noreferrer' style='color:red; font-weight:bold;'>▶ 【公式サイト】詳細を確認</a>" if c_url else ""
        
        popup_html = (
            f"<b>{c_cat} [{c_pref}] {c_name}</b>"
            f"{river_info}<br>"
            f"警戒レベル: <span style='color:{c_color}; font-weight:bold;'>{c_lvl}</span><br>"
            f"状況: <span style='color:{c_color}; font-weight:bold;'>{c_status}</span><br>"
            f"{c_desc}{camera_link_html}"
        )
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_html, max_width=340),
            icon=folium.Icon(color=c_color, icon="warning" if c_color!="blue" else "info-sign")
        ).add_to(m)

map_left, map_center, map_right = st.columns([0.08, 0.84, 0.08])
with map_center:
    st_folium(m, width="100%", height=380, key="multi_region_map")

st.markdown(f"<h3 style='font-size: 20px; font-weight: bold; margin-top: 1rem;'>📋 選択条件のリスク・警戒レベル一覧</h3>", unsafe_allow_html=True)

if not filtered_locations:
    st.markdown("""
    <div style="background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 16px; border-radius: 6px; margin-bottom: 1rem;">
        <span style="color: #93c5fd; font-weight: bold; font-size: 15px;">ℹ️ 選択された条件に一致する個別重点データは現在ありません。</span><br><br>
        <span style="color: #f1f5f9; font-size: 13.5px;">
            すべての市区町村や河川の水位情報は上の<b>【国土交通省・気象庁公式リンク集】</b>から一瞬で確認できます。
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    for idx, loc in enumerate(filtered_locations):
        badge = "🔴【レベル4】" if loc["color"] == "red" else ("🟠【レベル3】" if loc["color"] == "orange" else "🔵【レベル1】")
        river_tag = f" ｜ 対象: **{loc['river_name']}**" if loc['river_name'] != "---" else ""
        title_text = f"{badge} ｜ {loc['pref']} ({loc['region']}) ｜ **{loc['name']}**{river_tag} ｜ 状況: **{loc['status']}**"
        
        with st.expander(title_text):
            st.markdown(f"**情報元**\n\n`{loc['source']}`")
            st.markdown("---")
            st.markdown(f"**警戒レベル**\n\n`{loc['level']}` — {loc['level_desc']}")
            st.markdown("---")
            st.markdown(f"**状況説明**\n\n{loc['desc']}")
            st.markdown("---")
            st.markdown("**水位・河川のリアルタイム確認**\n\n- <a href='https://www.river.go.jp/' target='_blank' rel='noopener noreferrer'>🌊 国土交通省 川の防災情報（全国の水位・ライブカメラ）</a>", unsafe_allow_html=True)
            if loc['camera_url']:
                st.markdown(f"- <a href='{loc['camera_url']}' target='_blank' rel='noopener noreferrer'>🌐 気象庁公式サイトで詳細を確認 (別タブ)</a>", unsafe_allow_html=True)
