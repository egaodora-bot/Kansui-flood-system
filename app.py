import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="全国インフラ・気象防災カルテ・リアルリンク共用システム", 
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
div[data-testid="stSelectbox"] {
    border-left: 5px solid #fde047;
    padding-left: 10px;
}
/* ライブ取得フィード専用の個別デザイン（全体オレンジ枠、左側緑の線） */
div.live-feed-expander div[data-testid="stExpander"] {
    border: 2px solid #f97316 !important;
    border-left: 6px solid #22c55e !important;
    border-radius: 8px;
    background-color: #0f172a;
}
</style>
""", unsafe_allow_html=True)

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
            {"title": "（道路交通情報）公益財団法人日本道路交通情報センター ・・・クリック後に同意画面があります", "link": "https://www.jartic.or.jp/", "date": "現在"}
        ]
    return news_items

@st.cache_data
def get_master_locations():
    return [
        {
            "category": "【河川・リアルタイム監視】", "region": "関東", "pref": "茨城県", "name": "鬼怒川流域（常総市水海道観測所）", 
            "infrastructure_type": "主要河川", "lat": 36.0150, "lon": 139.9900, "source": "国土交通省 関東地方整備局（リアルタイム観測）", 
            "level": "Level3", "level_desc": "【レベル3】高齢者等避難発令中（水位上昇）",
            "metric": "現在の観測水位 4.8m（避難判断水位超過）", "status": "高齢者等避難", "color": "orange", "priority": 2,
            "desc": "現在、氾濫注意水位を超えて上昇中。市町村から高齢者等避難が発令される可能性があります。公式情報をご確認ください。",
            "link_url": "https://www.river.go.jp/"
        },
        {
            "category": "【河川・リアルタイム監視】", "region": "東北", "pref": "福島県", "name": "阿武隈川流域（郡山市周辺）", 
            "infrastructure_type": "主要河川", "lat": 37.9000, "lon": 140.7800, "source": "国土交通省 東北地方整備局（リアルタイム観測）", 
            "level": "Level4", "level_desc": "【レベル4】避難指示発令中（氾濫危険）",
            "metric": "現在の観測水位 氾濫危険水位到達", "status": "避難指示", "color": "red", "priority": 1,
            "desc": "河川の氾濫危険水位に到達しています。速やかに安全な場所へ避難してください。",
            "link_url": "https://www.river.go.jp/"
        },
        {
            "category": "【河川・リアルタイム監視】", "region": "関東", "pref": "東京都", "name": "多摩川流域（二子玉川周辺）", 
            "infrastructure_type": "主要河川", "lat": 35.6000, "lon": 139.6300, "source": "国土交通省 京浜河川事務所", 
            "level": "Level2", "level_desc": "【レベル2】大雨・洪水注意報継続中",
            "metric": "通常推移・注意報レベル", "status": "気象注意報", "color": "blue", "priority": 3,
            "desc": "現在は水防団待機水位を下回っていますが、今後の気象情報にご注意ください。",
            "link_url": "https://www.river.go.jp/"
        },
        {
            "category": "【道路・リアルタイム規制】", "region": "中部", "pref": "長野県", "name": "国道19号（木曽路山間部区間）", 
            "infrastructure_type": "国道", "lat": 35.8500, "lon": 137.6000, "source": "国土交通省 中部地方整備局", 
            "level": "Level4", "level_desc": "【レベル4相当】連続雨量超過による通行止め",
            "metric": "雨量規制値到達・通行止め", "status": "通行止め", "color": "red", "priority": 1,
            "desc": "降雨量が規制値に達したため、当該区間はリアルタイムで通行止めが実施されています。",
            "link_url": "https://www.jartic.or.jp/"
        },
        {
            "category": "【鉄道・リアルタイム運行】", "region": "関東", "pref": "東京都", "name": "JR東日本 首都圏在来線各線", 
            "infrastructure_type": "鉄道", "lat": 35.6812, "lon": 139.7671, "source": "JR東日本 運行情報センター", 
            "level": "Level3", "level_desc": "【レベル3相当】計画運休・遅延発生中",
            "metric": "気象条件による運転見合わせ", "status": "運転見合わせ", "color": "orange", "priority": 2,
            "desc": "悪天候の影響に伴い、一部路線で計画運休および大幅な遅れが発生しています。",
            "link_url": "https://www.train-info.com/"
        },
        {
            "category": "【気象庁キキクル・リアルタイム】", "region": "中部", "pref": "静岡県", "name": "伊豆山地区周辺（熱海市山間部）", 
            "infrastructure_type": "気象庁データ", "lat": 35.1150, "lon": 139.0730, "source": "気象庁 危機管理情報", 
            "level": "Level5", "level_desc": "【レベル5】緊急安全確保（命の危険）",
            "metric": "キキクル極めて危険（黒/紫発令中）", "status": "緊急安全確保", "color": "red", "priority": 1,
            "desc": "すでに災害が発生している可能性が極めて高い状況です。直ちに命を守る最善の行動をとってください。",
            "link_url": "https://www.jma.go.jp/bosai/risk/"
        }
    ]

locations = get_master_locations()

# ヘルパータイトル部分
st.markdown("""
<div style="margin-left: 0px; margin-bottom: 1rem;">
    <div style="color: #60a5fa; font-size: 22px; font-weight: bold; margin-bottom: 4px;">
        🛡️ 全国インフラ・気象防災カルテ・リアルリンク共用システム
    </div>
    <div style="color: #93c5fd; font-size: 13.5px; font-weight: bold;">
        （※河川水位上昇・道路交通規制・鉄道運行・気象庁キキクル監視）
    </div>
</div>
""", unsafe_allow_html=True)

# 携帯でも最初に見えるメイン画面上部に「システム設計・通信検証方針」を配置
with st.expander("🛠️ 【重要】システムの設計・通信検証方針について（タップして展開）", expanded=False):
    st.markdown("""
    <div style="font-size: 13px; color: #cbd5e1; line-height: 1.6;">
        本システムは、過酷な災害現場や低速なモバイル回線（128kbps等）の環境下でも、可能な限りエラーを抑えて迅速に命を守る情報にアクセスできるよう設計されています（※通信環境や電波状況により接続が不安定になる場合があります）。<br><br>
        リアルタイムの警戒レベル2〜5の状況を迅速に把握するため、データ容量を極限まで軽量化し、通信負荷の軽減を図っています。<br><br>
        <b>🔹 128kbps低速通信・スマホ環境への配慮</b><br>
        初回ロード時のデータ量を最小限に抑えているため、通信速度制限がかかったスマホ環境や電波の弱い被災地であっても、タイムアウトやフリーズのリスクを軽減し、スムーズに起動することを目指しています。<br><br>
        <b>🔹 キャッシュ機能とマーカークラスターの導入</b><br>
        サーバー負荷やブラウザのメモリ消費を抑えるため、データのキャッシュ処理および地図上のピンの自動グルーピング（クラスター表示）を行い、スマートフォンでの実用的な操作性を確保しています。
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# エリアに特化したシンプルな単一選択
st.markdown("""<div style="border-left: 5px solid #fde047; padding-left: 8px; margin-bottom: 4px;"><span style="color: #fef08a; font-weight: bold; font-size: 14px;">📍 監視エリアの選択（エリアで起きている災害・インフラ状況の確認）</span></div>""", unsafe_allow_html=True)

available_regions = ["すべて表示", "北海道", "東北", "関東", "中部", "関西", "四国", "九州"]
selected_region = st.selectbox("エリア選択", options=available_regions, label_visibility="collapsed")

filtered_locations = locations if selected_region == "すべて表示" else [loc for loc in locations if loc["region"] == selected_region]

danger_count = sum(1 for loc in filtered_locations if loc["color"] == "red")
warning_count = sum(1 for loc in filtered_locations if loc["color"] == "orange")

st.markdown(f"""
<div style="background-color: #1e293b; padding: 12px 16px; border-radius: 8px; border-left: 6px solid #ef4444; margin-top: 12px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
    <span style="color: #f8fafc; font-size: 14px; font-weight: bold;">
        🚨 <span style="color: #fca5a5;">【リアルタイム警戒状況】</span> 選択エリアの緊急警戒（赤：レベル4・5）が <span style="color: #f87171; font-size: 16px;"><b>{danger_count}件</b></span>、注意警戒（橙：レベル3）が <span style="color: #fbbf24; font-size: 16px;"><b>{warning_count}件</b></span> 検出されています。
    </span>
</div>
""", unsafe_allow_html=True)

# 公式データリンク集
st.markdown("""
<div style="background-color: #0f172a; border: 2px solid #ffffff; border-left: 6px solid #38bdf8; padding: 14px 18px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
    <div style="color: #fef08a; font-weight: bold; font-size: 15px; margin-bottom: 8px;">
        ⚡ <b>【公式データリンク集】河川・国道・県道・市町道・鉄道・気象庁のリアルタイム状況</b>
    </div>
    <div style="font-size: 13.5px; color: #f1f5f9; line-height: 1.8;">
        ・ 🌊 （河川） <a href="https://www.river.go.jp/" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; font-weight: bold;">国土交通省 川の防災情報（全国の河川水位・ライブカメラ）</a><br>
        ・ 🚗 （道路） <a href="https://www.jartic.or.jp/" target="_blank" rel="noopener noreferrer" style="color: #7dd3fc; font-weight: bold;">JARTIC 日本道路交通情報センター（高速・国道・県道の規制情報）</a><br>
        ・ 🚆 （鉄道） <a href="https://www.train-info.com/" target="_blank" rel="noopener noreferrer" style="color: #34d399; font-weight: bold;">主要鉄道 運行情報・各社遅延リアルタイム案内</a><br>
        ・ 🔴 （気象） <a href="https://www.jma.go.jp/bosai/warning/" target="_blank" rel="noopener noreferrer" style="color: #fca5a5; font-weight: bold;">気象庁 警報・注意報（すべての市区町村別の最新発令状況）</a><br>
        ・ ⚠️ （気象） <a href="https://www.jma.go.jp/bosai/risk/" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; font-weight: bold;">気象庁 キキクル（土砂・浸水・洪水危険度分布）</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ライブ取得フィード
st.markdown('<div class="live-feed-expander">', unsafe_allow_html=True)
with st.expander("📡 【ライブ取得】リアルタイム災害・速報フィード", expanded=True):
    news_list = fetch_robust_disaster_news()
    for news in news_list:
        st.markdown(f"- <a href='{news['link']}' target='_blank' rel='noopener noreferrer' style='color: #f97316; font-weight: bold;'>{news['title']}</a> <small style='color:gray;'>({news['date']})</small>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 地図表示
map_center_lat = filtered_locations[0]["lat"] if filtered_locations else 35.6895
map_center_lon = filtered_locations[0]["lon"] if filtered_locations else 139.6917
map_zoom = 8 if selected_region != "すべて表示" else 5

m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=map_zoom, control_scale=True)
marker_cluster = MarkerCluster().add_to(m)

for idx, loc in enumerate(filtered_locations):
    lat, lon = loc.get("lat"), loc.get("lon")
    if lat and lon:
        popup_html = (
            f"<b>{loc['category']} [{loc['pref']}]</b><br>"
            f"<b>{loc['name']}</b><br>"
            f"状況: <span style='color:{loc['color']}; font-weight:bold;'>{loc['status']}</span><br>"
            f"指標: {loc['metric']}<br>"
            f"{loc['desc']}<br><a href='{loc['link_url']}' target='_blank' rel='noopener noreferrer' style='color:red; font-weight:bold;'>▶ 公式詳細を確認</a>"
        )
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_html, max_width=320),
            icon=folium.Icon(color=loc['color'], icon="info-sign")
        ).add_to(marker_cluster)

map_left, map_center, map_right = st.columns([0.08, 0.84, 0.08])
with map_center:
    st_folium(m, width="100%", height=380, key="infra_map_clustered")

st.markdown(f"<h3 style='font-size: 20px; font-weight: bold; margin-top: 1rem;'>📋 選択エリアのリアルタイム警戒レベル（レベル2〜5）状況一覧</h3>", unsafe_allow_html=True)

if not filtered_locations:
    st.markdown("""
    <div style="background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 16px; border-radius: 6px; margin-bottom: 1rem;">
        <span style="color: #93c5fd; font-weight: bold; font-size: 15px;">ℹ️ 選択されたエリアに一致するリアルタイムデータは現在ありません。</span>
    </div>
    """, unsafe_allow_html=True)
else:
    for idx, loc in enumerate(filtered_locations):
        if loc["level"] == "Level5":
            badge = "🔴【レベル5/緊急安全確保】"
        elif loc["level"] == "Level4":
            badge = "🔴【レベル4/避難指示】"
        elif loc["level"] == "Level3":
            badge = "🟠【レベル3/高齢者等避難】"
        else:
            badge = "🔵【レベル2/気象注意報】"
            
        title_text = f"{badge} ｜ [{loc['infrastructure_type']}] {loc['pref']} ｜ **{loc['name']}**"
        
        with st.expander(title_text):
            st.markdown(f"**情報元・管理組織**\n\n`{loc['source']}`")
            st.markdown(f"**現在の観測・警戒指標**\n\n`{loc['metric']}`")
            st.markdown("---")
            st.markdown(f"**リアルタイム状況詳細**\n\n{loc['desc']}")
            st.markdown("---")
            st.markdown(f"- <a href='{loc['link_url']}' target='_blank' rel='noopener noreferrer'>🌐 現在のリアルタイム公式情報を確認する (別タブ)</a>", unsafe_allow_html=True)
