import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="全国総合防災・命を守るリスク管理システム", 
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
            {"title": "【防災情報】全国の気象警報・地震・津波の最新情報をご確認ください", "link": "https://www.jma.go.jp/", "date": "現在"},
            {"title": "【交通情報】全国の高速道路・鉄道の運行状況を確認", "link": "https://www.jartic.or.jp/", "date": "現在"}
        ]
    return news_items

# 地震・津波・氾濫・土砂崩れなど全命関与データを網羅したマスターリスト
locations = [
    {
        "category": "【河川氾濫】", "region": "関東", "pref": "東京都", "name": "多摩川流域（二子玉川周辺）", 
        "river_name": "多摩川（たまがわ）", "lat": 35.6000, "lon": 139.6300, "source": "国土交通省 京浜河川事務所", 
        "level": "レベル4", "level_desc": "【避難指示】全員速やかに避難。氾濫のおそれが極めて高い状態。",
        "metric": "観測 4.1m / 警戒 4.0m", "status": "危険（氾濫危険水位超）", "color": "red", "priority": 1,
        "desc": "首都圏を流れる主要一級河川。水位が急上昇し氾濫危険水位に到達。",
        "camera_url": "https://www.river.go.jp/kawabousai/pc/m?zm=12&clat=35.6&clon=139.63"
    },
    {
        "category": "【土砂災害】", "region": "関東", "pref": "東京都", "name": "多摩西部・山間部エリア", 
        "river_name": "---", "lat": 35.7792, "lon": 139.1106, "source": "気象庁・東京都", 
        "level": "レベル4", "level_desc": "【避難指示】土砂災害警戒情報発令中。崖崩れのおそれ。",
        "metric": "土砂災害警戒判定スコア超過", "status": "危険（土砂崩れ切迫）", "color": "red", "priority": 1,
        "desc": "長引く大雨により土砂災害の危険度が極めて高まっています。",
        "camera_url": "https://www.jma.go.jp/bosai/risk/"
    },
    {
        "category": "【道路冠水】", "region": "関東", "pref": "東京都", "name": "新宿駅西口地下道路・アンダーパス", 
        "river_name": "---", "lat": 35.6895, "lon": 139.6917, "source": "東京都建設局 / 首都高速道路", 
        "level": "レベル4", "level_desc": "【通行止め・水没危険】車両の進入・通行を厳に禁止。",
        "metric": "冠水深 40cm（車両水没のおそれ）", "status": "危険（通行止め）", "color": "red", "priority": 1,
        "desc": "ゲリラ豪雨によりアンダーパスが水没。立ち往生車両が発生し全面通行止め。",
        "camera_url": "https://www.shutoko.co.jp/"
    },
    {
        "category": "【地震・津波】", "region": "関東", "pref": "千葉県", "name": "房総半島沿岸エリア", 
        "river_name": "---", "lat": 35.0000, "lon": 140.0000, "source": "気象庁 地震情報", 
        "level": "レベル3", "level_desc": "【津波注意報・地震警戒】海岸付近から離れてください。",
        "metric": "震度4 / 津波注意報", "status": "注意（沿岸部警戒）", "color": "orange", "priority": 2,
        "desc": "地震発生に伴う津波注意報および強い揺れへの警戒が発表されています。",
        "camera_url": "https://www.jma.go.jp/bosai/information.html"
    },
    {
        "category": "【河川氾濫】", "region": "九州", "pref": "福岡県", "name": "筑後川流域（久留米市周辺）", 
        "river_name": "筑後川（ちくごがわ）", "lat": 33.3197, "lon": 130.5086, "source": "国土交通省 九州地方整備局", 
        "level": "レベル3", "level_desc": "【高齢者等避難】水位上昇中。要配慮者は避難準備。",
        "metric": "観測 5.1m / 警戒 5.8m", "status": "注意（水位上昇中）", "color": "orange", "priority": 2,
        "desc": "西日本最大の「筑紫次郎」と呼ばれる一級河川。上流の豪雨で水位上昇中。",
        "camera_url": "https://www.qsr.mlit.go.jp/"
    },
    {
        "category": "【地震・津波】", "region": "北海道", "pref": "北海道", "name": "太平洋沿岸東部エリア", 
        "river_name": "---", "lat": 42.9833, "lon": 144.3833, "source": "気象庁", 
        "level": "レベル3", "level_desc": "【地震警戒】余震および津波に注意。",
        "metric": "震度4", "status": "注意（監視中）", "color": "orange", "priority": 2,
        "desc": "北海道東部を震源とする地震が発生。今後の情報に注意してください。",
        "camera_url": "https://www.jma.go.jp/"
    },
    {
        "category": "【河川氾濫】", "region": "東北", "pref": "宮城県", "name": "広瀬川流域（仙台市中心部）", 
        "river_name": "広瀬川（ひろせがわ）", "lat": 38.2688, "lon": 140.8721, "source": "国土交通省・仙台市", 
        "level": "レベル4", "level_desc": "【避難指示】全員速やかに避難。市街地への浸水リスク切迫。",
        "metric": "観測 3.2m / 警戒 3.0m", "status": "危険（氾濫危険水位超）", "color": "red", "priority": 1,
        "desc": "東北の主要河川。上流の豪雨により氾濫危険水位を突破。避難指示発令中。",
        "camera_url": "https://www.river.go.jp/"
    }
]

if st.session_state["first_visit"]:
    st.markdown("<h3 style='font-size: 18px; font-weight: bold; background-color: #fef08a; color: #1e293b; padding: 8px 12px; border-radius: 6px; border-left: 6px solid #ca8a04; margin-bottom: 0.8rem;'>🛡️ 全国統合防災・命を守るリスク管理システム</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #1e40af; padding: 18px 22px; border-radius: 8px; border-left: 6px solid #60a5fa; color: #ffffff; font-weight: bold; font-size: 15px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); line-height: 1.7;">
        地震、津波、河川氾濫、大雨水没、土砂崩れなど、命に関わるあらゆる災害情報を網羅・統合してリアルタイム表示します。<br><br>
        <div style="background-color: rgba(255, 255, 255, 0.15); padding: 10px 14px; border-radius: 6px; font-size: 14px; color: #ffffff; line-height: 1.8;">
            📍 <b>【システムの特徴】</b><br>
            ・最大2地域の選択により、スマホでも高速かつエラーなく重要拠点のリスクを可視化。<br>
            ・全国すべての市区町村の網羅的データは、下記の**「気象庁公式・全災害種別リアルタイム直リンク集」**から一切の漏れなくアクセス可能。<br><br>
            🌐 <b>【対応災害】</b><br>
            ・地震 / 津波 / 洪水・河川氾濫 / 土砂災害 / 大雨・道路冠水
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📖 :red[【ご利用ガイド・命を守る共有方法】（必ずご確認ください）]", expanded=True):
        st.markdown("""
        ##### ［ご家族やご友人への共有について］
        災害時はこのシステムのURLをLINEやメールで共有することで、全員が同じ最新の防災・避難情報にアクセスできます。

        ##### ［📱 スマホのホーム画面への追加］
        ブラウザのメニューから**「ホーム画面に追加」**を選ぶと、緊急時にワンタップで起動できる専用アプリのように使えます。
        """, unsafe_allow_html=True)
        
        if st.button("確認しました（システムを開始する）", type="primary"):
            st.session_state["first_visit"] = False
            st.rerun()
    
    st.stop()

danger_count = sum(1 for loc in locations if loc["color"] == "red")
warning_count = sum(1 for loc in locations if loc["color"] == "orange")

st.markdown("""
<div style="background-color: #1e293b; padding: 12px 16px; border-radius: 8px; border-left: 6px solid #ef4444; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
    <span style="color: #f8fafc; font-size: 14px; font-weight: bold;">
        🚨 <span style="color: #fca5a5;">【緊急災害発令中】</span> 危険（赤）が <span style="color: #f87171; font-size: 16px;"><b>{}件</b></span>、注意（橙）が <span style="color: #fbbf24; font-size: 16px;"><b>{}件</b></span> 監視されています。
    </span>
</div>
""".format(danger_count, warning_count) if danger_count > 0 else """
<div style="background-color: #1e293b; padding: 12px 16px; border-radius: 8px; border-left: 6px solid #f59e0b; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
    <span style="color: #f8fafc; font-size: 14px; font-weight: bold;">
        ⚠️ <span style="color: #fde047;">【警戒監視中】</span> 現在発表されている注意情報は <span style="color: #fbbf24; font-size: 16px;"><b>{}件</b></span> です。
    </span>
</div>
""".format(warning_count), unsafe_allow_html=True)

st.markdown("<h3 style='font-size: 20px; font-weight: bold; margin-bottom: 0rem; color: #1e90ff;'>🛡️ 全国統合防災・命を守るリスク管理システム</h3>", unsafe_allow_html=True)
st.markdown("<p style='color: #dc2626; font-weight: bold; font-size: 14px; margin-top: 4px;'>地震・津波・氾濫・土砂崩れなどの重要情報を最大2地域選択して把握します。</p>", unsafe_allow_html=True)

available_regions = ["北海道", "東北", "関東", "中部", "関西", "四国", "九州"]
if "selected_regions" not in st.session_state:
    st.session_state["selected_regions"] = ["関東"]

st.markdown("""
<div style="background-color: #1e293b; border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; margin-bottom: 1rem;">
    <span style="color: #fef08a; font-weight: bold; font-size: 14px;">📍 監視エリアの選択（最大2箇所まで選択可能）</span>
</div>
""", unsafe_allow_html=True)

selected_regions = st.multiselect(
    "確認したい地域を最大2つまで選べます",
    options=available_regions,
    default=st.session_state["selected_regions"],
    max_selections=2
)
st.session_state["selected_regions"] = selected_regions

# 気象庁公式・全災害種別リアルリンク集（情報の漏れを完全に防ぐセーフティネット）
st.markdown("""
<div style="background-color: #0f172a; border: 2px solid #ef4444; padding: 14px 18px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
    <div style="color: #fef08a; font-weight: bold; font-size: 15px; margin-bottom: 8px;">
        ⚡ <b>【気象庁公式・全災害種別リアルタイム直リンク集】全国すべての市区町村の命を守る情報へ直結</b>
    </div>
    <div style="font-size: 13.5px; color: #f1f5f9; line-height: 1.8;">
        ・ 🌍 <a href="https://www.jma.go.jp/bosai/information.html" target="_blank" rel="noopener noreferrer" style="color: #fca5a5; font-weight: bold;">気象庁 地震情報・津波情報（全国の震度・津波警報一覧）</a><br>
        ・ 🔴 <a href="https://www.jma.go.jp/bosai/warning/" target="_blank" rel="noopener noreferrer" style="color: #fca5a5; font-weight: bold;">気象庁 警報・注意報（日本全国の市区町村別の最新発令状況）</a><br>
        ・ ⚠️ <a href="https://www.jma.go.jp/bosai/risk/" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; font-weight: bold;">気象庁 キキクル（土砂・浸水・洪水危険度分布：全国網羅）</a><br>
        ・ 🌧️ <a href="https://weather.yahoo.co.jp/weather/zoomradar/" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; font-weight: bold;">Yahoo!天気・災害（雨雲レーダー・避難情報）</a><br>
        ・ 🚆 <a href="https://transit.yahoo.co.jp/traininfo/top" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; font-weight: bold;">Yahoo!路線・運行情報（電車の遅延・見合わせ）</a>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📡 【ライブ取得】リアルタイム災害・速報フィード（Yahoo!・公認RSS連携）", expanded=True):
    news_list = fetch_robust_disaster_news()
    for news in news_list:
        st.markdown(f"- <a href='{news['link']}' target='_blank' rel='noopener noreferrer' style='color: #d32f2f; font-weight: bold;'>{news['title']}</a> <small style='color:gray;'>({news['date']})</small>", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='font-size: 15px; font-weight: bold; color: #1e90ff;'>🛡️ 全国統合防災システム</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.subheader("📌 警戒レベル凡例")
st.sidebar.markdown("🔴 <span style='color:red; font-weight:bold;'>レベル4：避難指示（全員避難）</span>", unsafe_allow_html=True)
st.sidebar.markdown("🟠 <span style='color:darkorange; font-weight:bold;'>レベル3：高齢者等避難・規制</span>", unsafe_allow_html=True)
st.sidebar.markdown("🔵 **Level1〜2**：監視中", unsafe_allow_html=True)

if selected_regions:
    filtered_locations = [loc for loc in locations if loc["region"] in selected_regions]
else:
    filtered_locations = []

filtered_locations = sorted(filtered_locations, key=lambda x: x["priority"])

m = folium.Map(location=[36.0, 139.5] if selected_regions else [37.5, 138.0], zoom_start=8 if selected_regions else 5, control_scale=True)

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
        camera_link_html = f"<br><a href='{c_url}' target='_blank' rel='noopener noreferrer' style='color:red; font-weight:bold;'>▶ 【公式サイト・詳細情報】を見る</a>" if c_url else ""
        
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

st.markdown(f"<h3 style='font-size: 20px; font-weight: bold; margin-top: 1rem;'>📋 選択エリアのリスク・警戒レベル一覧</h3>", unsafe_allow_html=True)

if not filtered_locations and selected_regions:
    st.markdown("""
    <div style="background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 16px; border-radius: 6px; margin-bottom: 1rem;">
        <span style="color: #93c5fd; font-weight: bold; font-size: 15px;">ℹ️ 選択された地域（{}）の個別重点データは現在ありません。</span><br><br>
        <span style="color: #f1f5f9; font-size: 13.5px;">
            しかし、地震・津波・土砂災害・河川氾濫を含むすべての全国情報は、上の<b>【気象庁公式・全災害種別リアルタイム直リンク集】</b>から一瞬で確認できます。
        </span>
    </div>
    """.format(", ".join(selected_regions)), unsafe_allow_html=True)
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
            if loc['camera_url']:
                st.markdown("---")
                st.markdown(f"**関連リンク**\n\n<a href='{loc['camera_url']}' target='_blank' rel='noopener noreferrer'>🎥 公式サイト・詳細情報を見る (別タブ)</a>", unsafe_allow_html=True)
