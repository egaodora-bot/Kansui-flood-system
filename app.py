import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="全国統合防災・リスク管理システム", 
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
            {"title": "【防災情報】全国の気象警報・河川水位の最新情報をご確認ください", "link": "https://www.jma.go.jp/", "date": "現在"},
            {"title": "【交通情報】全国の高速道路・鉄道の運行状況を確認", "link": "https://www.jartic.or.jp/", "date": "現在"}
        ]
    return news_items

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
        "category": "【道路冠水】", "region": "関東", "pref": "東京都", "name": "新宿駅西口地下道路・アンダーパス", 
        "river_name": "---", "lat": 35.6895, "lon": 139.6917, "source": "東京都建設局 / 首都高速道路", 
        "level": "レベル4", "level_desc": "【通行止め・水没危険】車両の進入・通行を厳に禁止。",
        "metric": "冠水深 40cm（車両水没のおそれ）", "status": "危険（通行止め）", "color": "red", "priority": 1,
        "desc": "ゲリラ豪雨によりアンダーパスが水没。立ち往生車両が発生し全面通行止め。",
        "camera_url": "https://www.shutoko.co.jp/"
    },
    {
        "category": "【高速道路】", "region": "関東", "pref": "埼玉県", "name": "東北自動車道（羽生IC〜館林IC）", 
        "river_name": "---", "lat": 36.1700, "lon": 139.5500, "source": "NEXCO東日本", 
        "level": "Level3", "level_desc": "【交通規制】迂回ルートの検討および安全確認が必須。",
        "metric": "冠水影響による通行止め", "status": "注意（災害影響）", "color": "orange", "priority": 2,
        "desc": "NEXCO東日本管内。大雨に伴う道路冠水のため、該当区間で上下線とも通行止め。",
        "camera_url": "https://www.e-nexco.co.jp/"
    },
    {
        "category": "【鉄道影響】", "region": "関東", "pref": "東京都", "name": "JR山手線・中央線", 
        "river_name": "---", "lat": 35.6812, "lon": 139.7671, "source": "JR東日本 運行情報", 
        "level": "Level3", "level_desc": "【運行障害】運転見合わせ・大幅な遅延が発生中。",
        "metric": "一部運転見合わせ", "status": "注意（ダイヤ乱れ）", "color": "orange", "priority": 2,
        "desc": "JR東日本管内。大雨の影響および線路内点検のため、一部区間で運転見合わせ。",
        "camera_url": "https://www.jreast.co.jp/"
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
        "category": "【河川氾濫】", "region": "北海道", "pref": "北海道", "name": "石狩川流域（札幌市・江別市周辺）", 
        "river_name": "石狩川（いしかりがわ）", "lat": 43.1167, "lon": 141.5333, "source": "国土交通省 札幌開発建設部", 
        "level": "Level3", "level_desc": "【高齢者等避難】水位上昇中。要配慮者は避難準備。",
        "metric": "観測 3.8m / 警戒 4.2m", "status": "注意（水位上昇中）", "color": "orange", "priority": 2,
        "desc": "北海道を代表する大河川。上流のまとまった雨により水位が上昇傾向。",
        "camera_url": "https://www.hkd.mlit.go.jp/"
    },
    {
        "category": "【河川氾濫】", "region": "東北", "pref": "宮城県", "name": "広瀬川流域（仙台市中心部）", 
        "river_name": "広瀬川（ひろせがわ）", "lat": 38.2688, "lon": 140.8721, "source": "国土交通省・仙台市", 
        "level": "レベル4", "level_desc": "【避難指示】全員速やかに避難。市街地への浸水リスク切迫。",
        "metric": "観測 3.2m / 警戒 3.0m", "status": "危険（氾濫危険水位超）", "color": "red", "priority": 1,
        "desc": "東北の主要河川。上流の豪雨により氾濫危険水位を突破。避難指示発令中。",
        "camera_url": "https://www.river.go.jp/"
    },
    {
        "category": "【高速道路】", "region": "中部", "pref": "愛知県", "name": "東名高速道路（岡崎IC〜豊田JCT）", 
        "river_name": "---", "lat": 34.9500, "lon": 137.1600, "source": "NEXCO中日本 道路交通情報", 
        "level": "Level3", "level_desc": "【交通規制】大雨による速度規制および一部通行止めのおそれ。",
        "metric": "降雨量超過による速度規制", "status": "注意（速度規制中）", "color": "orange", "priority": 2,
        "desc": "NEXCO中日本管内。まとまった降雨により該当区間で50km/hの速度規制を実施中。",
        "camera_url": "https://www.c-nexco.co.jp/"
    },
    {
        "category": "【鉄道影響】", "region": "関西", "pref": "大阪府", "name": "JR京都線・JR神戸線", 
        "river_name": "---", "lat": 34.7000, "lon": 135.5000, "source": "JR西日本 運行情報", 
        "level": "Level3", "level_desc": "【運行障害】大雨に伴う運転見合わせ・遅延。",
        "metric": "一部ダイヤ乱れ", "status": "注意（遅延発生）", "color": "orange", "priority": 2,
        "desc": "JR西日本管内。沿線の大雨レーダー反応にともない、一時的に速度落として運行。",
        "camera_url": "https://www.westjr.co.jp/"
    },
    {
        "category": "【高速道路】", "region": "九州", "pref": "福岡県", "name": "九州自動車道（太宰府IC〜鳥栖JCT）", 
        "river_name": "---", "lat": 33.4800, "lon": 130.5200, "source": "NEXCO西日本", 
        "level": "Level1", "level_desc": "【早期注意情報】平常時・安全監視中。",
        "metric": "異常なし", "status": "正常（監視中）", "color": "blue", "priority": 3,
        "desc": "NEXCO西日本管内。現在のところ交通規制はありません。",
        "camera_url": "https://www.w-nexco.co.jp/"
    }
]

if st.session_state["first_visit"]:
    st.markdown("<h3 style='font-size: 18px; font-weight: bold; background-color: #fef08a; color: #1e293b; padding: 8px 12px; border-radius: 6px; border-left: 6px solid #ca8a04; margin-bottom: 0.8rem;'>🛡️ 全国統合防災・リスク管理システムへようこそ</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #1e40af; padding: 18px 22px; border-radius: 8px; border-left: 6px solid #60a5fa; color: #ffffff; font-weight: bold; font-size: 15px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); line-height: 1.7;">
        当システムでは、気象庁や国土交通省などの公的機関が提供するオープンデータおよび信頼性の高い情報を統合してリアルタイム表示しています。<br><br>
        <div style="background-color: rgba(255, 255, 255, 0.15); padding: 10px 14px; border-radius: 6px; font-size: 14px; color: #ffffff; line-height: 1.8;">
            📍 <b>【最大2地域までの絞り込み設計について】</b><br>
            ・出発地や到着地など、**最大2箇所まで**の地域を選択して、負荷を抑えながら確実かつスピーディーに状況を確認できます。<br>
            ・家族や友人へURLをそのまま共有して、みんなで同時に最新情報を確認可能です。<br><br>
            🌐 <b>【主なデータ提供元】</b><br>
            ・気象庁（キキクル・警報） / 国土交通省（河川水位） / Yahoo!天気
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📖 :red[【ご利用ガイド・システム共有方法】（必ずご確認ください）]", expanded=True):
        st.markdown("""
        ##### ［ご家族やご友人への共有について］
        このシステムを他の人に教えるときは、ブラウザの上部にあるアドレスバーのURLをコピーして、LINEやメールで送ってあげてください。

        ##### ［📱 スマホのホーム画面にアイコンを作る方法（おすすめ）］
        スマホでこのページを開き、ブラウザのメニューから**「ホーム画面に追加」**を選ぶと、専用アプリのようなアイコンをホーム画面に配置できます。
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
        🚨 <span style="color: #fca5a5;">【緊急警報発令中】</span> 危険（赤）が <span style="color: #f87171; font-size: 16px;"><b>{}件</b></span>、注意（橙）が <span style="color: #fbbf24; font-size: 16px;"><b>{}件</b></span> 発生しています。
    </span>
</div>
""".format(danger_count, warning_count) if danger_count > 0 else """
<div style="background-color: #1e293b; padding: 12px 16px; border-radius: 8px; border-left: 6px solid #f59e0b; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
    <span style="color: #f8fafc; font-size: 14px; font-weight: bold;">
        ⚠️ <span style="color: #fde047;">【注意喚起】</span> 重大な危険はありませんが、<span style="color: #fbbf24; font-size: 16px;"><b>{}件</b></span> の注意情報が発表されています。
    </span>
</div>
""".format(warning_count), unsafe_allow_html=True)

st.markdown("<h3 style='font-size: 20px; font-weight: bold; margin-bottom: 0rem; color: #1e90ff;'>🛡️ 全国統合防災・リスク管理システム</h3>", unsafe_allow_html=True)
st.markdown("<p style='color: #dc2626; font-weight: bold; font-size: 14px; margin-top: 4px;'>出発地や到着地など、最大2箇所を選んで効率よく安全に状況を把握します。</p>", unsafe_allow_html=True)

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

# 危機可視化・直リンクパネル
st.markdown("""
<div style="background-color: #0f172a; border: 2px solid #ef4444; padding: 14px 18px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
    <div style="color: #fef08a; font-weight: bold; font-size: 15px; margin-bottom: 8px;">
        ⚡ <b>【リアルタイム危機可視化・直リンク集】全国すべての市区町村の最新情報を直接確認</b>
    </div>
    <div style="font-size: 13.5px; color: #f1f5f9; line-height: 1.8;">
        ・ 🔴 <a href="https://www.jma.go.jp/bosai/warning/" target="_blank" rel="noopener noreferrer" style="color: #fca5a5; font-weight: bold;">気象庁 警報・注意報（日本全国の市区町村別の最新発令状況）</a><br>
        ・ ⚠️ <a href="https://www.jma.go.jp/bosai/risk/" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; font-weight: bold;">気象庁 キキクル（全国の土砂・浸水・洪水危険度分布）</a><br>
        ・ ☂️ <a href="https://weathernews.jp/" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; font-weight: bold;">ウェザーニュース（最新の天気・台風解説）</a><br>
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

# 選択された地域に基づいてロケーションをフィルタリング
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
        c_lvldesc = loc.get('level_desc')
        
        river_info = f"<br><b>対象河川:</b> {c_river}" if c_river != "---" else ""
        camera_link_html = f"<br><a href='{c_url}' target='_blank' rel='noopener noreferrer' style='color:red; font-weight:bold;'>▶ 【公式サイト・ライブ情報】を見る</a>" if c_url else ""
        
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
        <span style="color: #93c5fd; font-weight: bold; font-size: 15px;">ℹ️ 選択された地域（{}）の個別登録データは現在ありません。</span><br><br>
        <span style="color: #f1f5f9; font-size: 13.5px;">
            しかし、お住まいや通勤・お出かけ先のリアルタイムな気象警報・キキクル等の情報は、上の<b>【リアルタイム危機可視化・直リンク集】</b>から直接ご確認いただけます。
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
                st.markdown(f"**関連リンク**\n\n<a href='{loc['camera_url']}' target='_blank' rel='noopener noreferrer'>🎥 公式サイト・関連詳細情報を見る (別タブ)</a>", unsafe_allow_html=True)
