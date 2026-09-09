import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import urllib.request
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="全国インフラ・気象防災統合システム", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 128kbpsなどの低速環境でも視認性を保つための軽量かつ洗練されたスタイリング
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
            {"title": "【道路・交通情報】主要なインフラ・交通規制状況を確認", "link": "https://www.jartic.or.jp/", "date": "現在"}
        ]
    return news_items

# --- 【A基盤データ】2000年以降（過去25年）の重要被災・インフラ監視マスターデータ ---
@st.cache_data
def get_master_locations():
    return [
        # --- 🌊 主要河川 ---
        {
            "category": "【主要河川・氾濫危険】", "region": "関東", "pref": "茨城県", "name": "鬼怒川流域（常総市水海道周辺）", 
            "infrastructure_type": "主要河川", "lat": 36.0150, "lon": 139.9900, "source": "国土交通省", 
            "level": "レベル4", "level_desc": "【避難指示】過去の堤防決壊教訓地",
            "metric": "H27関東・東北豪雨 被災地", "status": "歴史的警戒地（堤防強化区間）", "color": "red", "priority": 1,
            "desc": "平成27年（2015年）9月関東・東北豪雨で堤防が決壊し大規模浸水が発生した歴史的教訓エリア。",
            "link_url": "https://www.river.go.jp/"
        },
        {
            "category": "【主要河川・氾濫危険】", "region": "東北", "pref": "福島県", "name": "阿武隈川流域（郡山市・丸森町周辺）", 
            "infrastructure_type": "主要河川", "lat": 37.9000, "lon": 140.7800, "source": "国土交通省", 
            "level": "レベル4", "level_desc": "【避難指示】氾濫・浸水多発流域",
            "metric": "R1東日本台風 被災地", "status": "要警戒（河川改修・水位監視）", "color": "red", "priority": 1,
            "desc": "令和元年東日本台風（台風19号）で各地で氾濫・決壊が発生し甚大な被害が出た重要流域。",
            "link_url": "https://www.river.go.jp/"
        },
        {
            "category": "【主要河川・水位上昇】", "region": "関東", "pref": "東京都", "name": "多摩川流域（二子玉川・武蔵小杉周辺）", 
            "infrastructure_type": "主要河川", "lat": 35.6000, "lon": 139.6300, "source": "国土交通省・気象庁", 
            "level": "Level3", "level_desc": "【高齢者等避難】水位急上昇リスク",
            "metric": "観測 4.1m / 警戒 4.0m", "status": "注意（水位上昇監視）", "color": "orange", "priority": 2,
            "desc": "令和元年台風19号で下水道逆流（内水氾濫）や越水スレスレの危険を記録した重要ポイント。",
            "link_url": "https://www.river.go.jp/"
        },
        {
            "category": "【主要河川・氾濫危険】", "region": "中部", "pref": "長野県", "name": "千曲川流域（長野市長沼周辺）", 
            "infrastructure_type": "主要河川", "lat": 36.6800, "lon": 138.2500, "source": "国土交通省", 
            "level": "レベル4", "level_desc": "【避難指示】大規模決壊跡地",
            "metric": "R1東日本台風 決壊地点", "status": "危険（厳重警戒）", "color": "red", "priority": 1,
            "desc": "令和元年台風19号により大規模な堤防決壊が発生し、新幹線車両基地等が水没した重要監視地点。",
            "link_url": "https://www.river.go.jp/"
        },

        # --- 🛣️ 国道・高速道路 ---
        {
            "category": "【国道・土砂崩落】", "region": "中部", "pref": "長野県", "name": "国道19号（木曽路山間部区間）", 
            "infrastructure_type": "国道", "lat": 35.8500, "lon": 137.6000, "source": "国土交通省 地方整備局", 
            "level": "レベル4", "level_desc": "【通行止め】法面崩落頻発区間",
            "metric": "連続雨量超過規制", "status": "危険（土砂崩落警戒）", "color": "red", "priority": 1,
            "desc": "豪雨のたびに法面崩落や土砂流入が発生し、物流の動脈が寸断されるリスクが高い警戒国道。",
            "link_url": "https://www.jartic.or.jp/"
        },
        {
            "category": "【高速道路・規制】", "region": "関東", "pref": "東京都", "name": "首都高速道路（中央環状線・山手トンネル等）", 
            "infrastructure_type": "国道", "lat": 35.6895, "lon": 139.6917, "source": "首都高速道路", 
            "level": "Level3", "level_desc": "【内水流入・一時規制】",
            "metric": "ゲリラ豪雨排水監視", "status": "注意（地下構造物監視）", "color": "orange", "priority": 2,
            "desc": "地下トンネル構造のため、近年の局地的なゲリラ豪雨時に厳重な排水・流入規制監視が行われる重要インフラ。",
            "link_url": "https://www.shutoko.jp/"
        },
        {
            "category": "【国道・通行止め】", "region": "関東", "pref": "神奈川県", "name": "国道1号（箱根峠周辺区間）", 
            "infrastructure_type": "国道", "lat": 35.2000, "lon": 139.0200, "source": "国土交通省", 
            "level": "レベル4", "level_desc": "【大雨・土砂災害通行止め】",
            "metric": "視程不良・降雨量超過", "status": "危険（事前通行規制）", "color": "red", "priority": 1,
            "desc": "台風や線状降水帯による豪雨で土砂崩れや通行止めが過去に何度も発生している主要動脈。",
            "link_url": "https://www.jartic.or.jp/"
        },

        # --- 🛤️ 県道・市町道 ---
        {
            "category": "【県道・アンダーパス冠水】", "region": "関東", "pref": "栃木県", "name": "主要地方道 宇都宮那須子線（河内地区低地）", 
            "infrastructure_type": "県道", "lat": 36.6000, "lon": 139.9000, "source": "栃木県 道路保全課", 
            "Level": "Level3", "level_desc": "【冠水注意】過去車両水没事例あり",
            "metric": "冠水深 30cm超", "status": "注意（冠水・通行注意）", "color": "orange", "priority": 2,
            "desc": "集中豪雨時に数分で水が溜まり、過去に車両の立ち往生が多発している代表的な生活道路の冠水ポイント。",
            "link_url": "https://www.pref.tochigi.lg.jp/"
        },
        {
            "category": "【市町道・高潮冠水】", "region": "中部", "pref": "静岡県", "name": "市道 沼津市平沼線（海岸近接アンダーパス）", 
            "infrastructure_type": "市町道", "lat": 35.1000, "lon": 138.8500, "source": "沼津市 道路課", 
            "level": "レベル4", "level_desc": "【高潮・大雨冠水規制】",
            "metric": "海水冠水リスク", "status": "危険（通行止め基準到達）", "color": "red", "priority": 1,
            "desc": "台風の高潮と豪雨が重なった際に一気に冠水被害を受ける、自治体管理の要注意アンダーパス。",
            "link_url": "https://www.city.numazu.shizuoka.jp/"
        },

        # --- ⚠️ 気象庁データ・土砂災害 ---
        {
            "category": "【気象庁・大規模土砂災害】", "region": "中部", "pref": "静岡県", "name": "伊豆山地区周辺（熱海市山間部）", 
            "infrastructure_type": "気象庁データ", "lat": 35.1150, "lon": 139.0730, "source": "気象庁 キキクル", 
            "level": "レベル4", "level_desc": "【避難指示】土砂災害厳重警戒エリア",
            "metric": "R3大規模土砂災害 教訓地", "status": "危険（土砂崩れ切迫警戒）", "color": "red", "priority": 1,
            "desc": "令和3年（2021年7月）に発生した大規模土砂災害の教訓を踏まえ、キキクル警戒が常時行われるエリア。",
            "link_url": "https://www.jma.go.jp/bosai/risk/"
        },
        {
            "category": "【気象庁・土砂災害警戒】", "region": "関東", "pref": "東京都", "name": "多摩西部・奥多摩町山間部（青梅街道周辺）", 
            "infrastructure_type": "気象庁データ", "lat": 35.7792, "lon": 139.1106, "source": "気象庁 キキクル", 
            "level": "レベル4", "level_desc": "【避難指示】土砂災害警戒情報発令中",
            "metric": "土砂災害リスク 極めて高い", "status": "危険（急傾斜地崩壊警戒）", "color": "red", "priority": 1,
            "desc": "過去の台風やゲリラ豪雨で土砂崩落が相次ぎ、土砂災害警戒区域のベンチマークとされる監視ポイント。",
            "link_url": "https://www.jma.go.jp/bosai/risk/"
        },
        {
            "category": "【気象庁・複合災害警戒】", "region": "関東", "pref": "千葉県", "name": "房総半島南部（館山市・南房総市山間部）", 
            "infrastructure_type": "気象庁データ", "lat": 35.0000, "lon": 139.8500, "source": "気象庁 台風情報", 
            "level": "レベル4", "level_desc": "【暴風・土砂崩れ・長期停電警戒】",
            "metric": "R1房総半島台風 教訓地", "status": "危険（複合災害警戒）", "color": "red", "priority": 1,
            "desc": "令和元年房総半島台風（台風15号）等で甚大な家屋損壊・土砂崩れ・インフラ寸断を経験した特異な被災エリア。",
            "link_url": "https://www.jma.go.jp/"
        }
    ]

locations = get_master_locations()

if st.session_state["first_visit"]:
    st.markdown("<h3 style='font-size: 20px; font-weight: bold; background-color: #fef08a; color: #1e293b; padding: 10px 14px; border-radius: 6px; border-left: 6px solid #ca8a04; margin-bottom: 0.8rem;'>🛡️ 全国インフラ・気象防災統合システム（2000年以降の防災カルテ）</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #1e40af; padding: 18px 22px; border-radius: 8px; border-left: 6px solid #60a5fa; color: #ffffff; font-weight: bold; font-size: 15px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); line-height: 1.7;">
        過去25年（2000年以降）の重大な被災・教訓地および主要インフラデータを網羅した防災統合システムです。<br><br>
        <div style="background-color: rgba(255, 255, 255, 0.15); padding: 10px 14px; border-radius: 6px; font-size: 14px; color: #ffffff; line-height: 1.8;">
            📍 <b>【システムの特徴】</b><br>
            ・軽量設計により低速通信環境（128kbps等）でもスムーズに稼働。<br>
            ・地図上のピンは自動的にクラスタリングされ、スマホでも軽快に操作できます。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📖 :red[【システムの設計・通信検証方針について・ご利用ガイド】]", expanded=True):
        # ユーザー様ご提示のブラッシュアップされた解説文を反映
        st.markdown("""
        ##### 🛠️ このシステムの設計・通信検証方針について
        本システムは、過酷な災害現場や低速なモバイル回線（128kbps等）の環境下でもエラーを起こさず、確実に命を守る情報にアクセスできることを最優先に設計されています。

        そのため、近年の気候変動や激甚化する災害（関東・東北豪雨、東日本台風、熱海市土砂災害など）の教訓が詰まった、2000年以降（過去25年間）の重要マスターデータを基本として注視採用し、厳選された約150〜200件のマスターデータを搭載。データ容量を極限まで軽量化（約1MB未満）しています。

        * **128kbps低速通信・スマホ環境での動作保証（予定）**
          初回ロード時のデータ量を最小限に抑えているため、通信速度制限がかかったスマホ環境や電波の弱い被災地であっても、タイムアウトやフリーズを起こさず数秒でスムーズに起動します。
        * **キャッシュ機能とマーカークラスターの導入**
          サーバー負荷やブラウザのメモリ消費を抑えるため、データのキャッシュ処理および地図上のピンの自動グルーピング（クラスター表示）を徹底し、スマホでの操作性を担保しています。
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        ##### ［ご家族やご友人への共有］
        災害時はこのシステムのURLを共有することで、全員が命を守る為に必要な、今いる場所が掲載している最新公開情報へアクセスできます。

        ##### ［📱 クイックにアクセスする為、スマホのホーム画面への追加］
        ブラウザメニューから「ホーム画面に追加」を行うと、専用アプリのようにワンタップで起動できます。(推奨)
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: rgba(253, 224, 71, 0.15); border-left: 5px solid #fde047; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; margin-top: 10px;">
            <span style="color: #fef08a; font-weight: bold; font-size: 14.5px;">
                👆 内容をご確認の上、以下のボタンを押してシステムを開始してください。
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("確認しました（システムを開始する）", type="primary"):
            st.session_state["first_visit"] = False
            st.rerun()
    
    st.stop()

st.markdown("""
<div style="margin-left: 0px; margin-bottom: 1.4rem;">
    <div style="color: #60a5fa; font-size: 24px; font-weight: bold; margin-bottom: 6px;">
        🛡️ 全国インフラ・気象防災統合システム
    </div>
    <div style="color: #93c5fd; font-size: 15px; font-weight: bold;">
        （※2000年以降の主要被災地・重要インフラ・気象庁データのカルテ）
    </div>
</div>
""", unsafe_allow_html=True)

# --- フィルターセクション ---
col_f1, col_f2, col_f3 = st.columns(3)

available_regions = ["すべて表示", "北海道", "東北", "関東", "中部", "関西", "四国", "九州"]
with col_f1:
    st.markdown("""<div style="border-left: 5px solid #fde047; padding-left: 8px; margin-bottom: 4px;"><span style="color: #fef08a; font-weight: bold; font-size: 13.5px;">📍 地方エリア</span></div>""", unsafe_allow_html=True)
    selected_region = st.selectbox("地方エリア選択", options=available_regions, label_visibility="collapsed")

base_locations = locations if selected_region == "すべて表示" else [loc for loc in locations if loc["region"] == selected_region]

available_infra_types = ["すべて表示", "主要河川", "国道", "県道", "市町道", "気象庁データ"]
with col_f2:
    st.markdown("""<div style="border-left: 5px solid #38bdf8; padding-left: 8px; margin-bottom: 4px;"><span style="color: #7dd3fc; font-weight: bold; font-size: 13.5px;">🏗️ インフラ種別</span></div>""", unsafe_allow_html=True)
    selected_infra = st.selectbox("インフラ種別選択", options=available_infra_types, label_visibility="collapsed")

available_prefs = ["すべて表示"] + sorted(list(set([loc["pref"] for loc in base_locations])))
with col_f3:
    st.markdown("""<div style="border-left: 5px solid #f43f5e; padding-left: 8px; margin-bottom: 4px;"><span style="color: #fda4af; font-weight: bold; font-size: 13.5px;">🔍 都道府県</span></div>""", unsafe_allow_html=True)
    selected_pref = st.selectbox("都道府県選択", options=available_prefs, label_visibility="collapsed")

filtered_locations = base_locations.copy()
if selected_infra != "すべて表示":
    filtered_locations = [loc for loc in filtered_locations if loc["infrastructure_type"] == selected_infra]
if selected_pref != "すべて表示":
    filtered_locations = [loc for loc in filtered_locations if loc["pref"] == selected_pref]

danger_count = sum(1 for loc in filtered_locations if loc["color"] == "red")
warning_count = sum(1 for loc in filtered_locations if loc["color"] == "orange")

st.markdown(f"""
<div style="background-color: #1e293b; padding: 12px 16px; border-radius: 8px; border-left: 6px solid #ef4444; margin-top: 15px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
    <span style="color: #f8fafc; font-size: 14px; font-weight: bold;">
        🚨 <span style="color: #fca5a5;">【2000年以降の防災カルテ・監視対象】</span> 選択条件の危険（赤）が <span style="color: #f87171; font-size: 16px;"><b>{danger_count}件</b></span>、注意（橙）が <span style="color: #fbbf24; font-size: 16px;"><b>{warning_count}件</b></span> 監視されています。
    </span>
</div>
""", unsafe_allow_html=True)

# 公式リンク集
st.markdown("""
<div style="background-color: #0f172a; border: 2px solid #ef4444; padding: 14px 18px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
    <div style="color: #fef08a; font-weight: bold; font-size: 15px; margin-bottom: 8px;">
        ⚡ <b>【公式データリンク集】河川・国道・県道・市町道・気象庁のリアルタイム状況</b>
    </div>
    <div style="font-size: 13.5px; color: #f1f5f9; line-height: 1.8;">
        ・ 🌊 <a href="https://www.river.go.jp/" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; font-weight: bold;">国土交通省 川の防災情報（全国の河川水位・ライブカメラ）</a><br>
        ・ 🚗 <a href="https://www.jartic.or.jp/" target="_blank" rel="noopener noreferrer" style="color: #7dd3fc; font-weight: bold;">JARTIC 日本道路交通情報センター（高速・国道・県道の規制情報）</a><br>
        ・ 🔴 <a href="https://www.jma.go.jp/bosai/warning/" target="_blank" rel="noopener noreferrer" style="color: #fca5a5; font-weight: bold;">気象庁 警報・注意報（すべての市区町村別の最新発令状況）</a><br>
        ・ ⚠️ <a href="https://www.jma.go.jp/bosai/risk/" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; font-weight: bold;">気象庁 キキクル（土砂・浸水・洪水危険度分布）</a>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📡 【ライブ取得】リアルタイム災害・速報フィード", expanded=True):
    news_list = fetch_robust_disaster_news()
    for news in news_list:
        st.markdown(f"- <a href='{news['link']}' target='_blank' rel='noopener noreferrer' style='color: #d32f2f; font-weight: bold;'>{news['title']}</a> <small style='color:gray;'>({news['date']})</small>", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='font-size: 14px; font-weight: bold; color: #60a5fa; line-height: 1.5;'>🛡️ インフラ・気象防災統合システム</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.subheader("📌 警戒レベル凡例")
st.sidebar.markdown("🔴 <span style='color:red; font-weight:bold;'>レベル4：避難指示・通行止め</span>", unsafe_allow_html=True)
st.sidebar.markdown("🟠 <span style='color:darkorange; font-weight:bold;'>Level3：高齢者等避難・規制</span>", unsafe_allow_html=True)
st.sidebar.markdown("🔵 **Level1〜2**：監視中", unsafe_allow_html=True)

# --- マップ描画（MarkerCluster導入でスマホでの負荷を大幅軽減） ---
filtered_locations = sorted(filtered_locations, key=lambda x: x["priority"])

map_center_lat = filtered_locations[0]["lat"] if filtered_locations else 35.6895
map_center_lon = filtered_locations[0]["lon"] if filtered_locations else 139.6917
map_zoom = 11 if selected_pref != "すべて表示" else (8 if selected_region != "すべて表示" else 5)

m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=map_zoom, control_scale=True)
marker_cluster = MarkerCluster().add_to(m)

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
        c_url = loc.get('link_url')
        
        link_html = f"<br><a href='{c_url}' target='_blank' rel='noopener noreferrer' style='color:red; font-weight:bold;'>▶ 公式詳細を確認</a>" if c_url else ""
        
        popup_html = (
            f"<b>{c_cat} [{c_pref}]</b><br>"
            f"<b>{c_name}</b><br>"
            f"状況: <span style='color:{c_color}; font-weight:bold;'>{c_status}</span><br>"
            f"{c_desc}{link_html}"
        )
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_html, max_width=320),
            icon=folium.Icon(color=c_color, icon="info-sign")
        ).add_to(marker_cluster)

map_left, map_center, map_right = st.columns([0.08, 0.84, 0.08])
with map_center:
    st_folium(m, width="100%", height=380, key="infra_map_clustered")

st.markdown(f"<h3 style='font-size: 20px; font-weight: bold; margin-top: 1rem;'>📋 2000年以降の防災カルテ・データ一覧</h3>", unsafe_allow_html=True)

if not filtered_locations:
    st.markdown("""
    <div style="background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 16px; border-radius: 6px; margin-bottom: 1rem;">
        <span style="color: #93c5fd; font-weight: bold; font-size: 15px;">ℹ️ 選択された条件に一致するインフラデータは現在ありません。</span><br><br>
        <span style="color: #f1f5f9; font-size: 13.5px;">
            すべての河川・道路・気象情報は上の<b>【公式データリンク集】</b>から直接ご確認いただけます。
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    for idx, loc in enumerate(filtered_locations):
        badge = "🔴【レベル4/被災教訓】" if loc["color"] == "red" else "🟠【Level3/警戒】"
        title_text = f"{badge} ｜ [{loc['infrastructure_type']}] {loc['pref']} ｜ **{loc['name']}** ｜ 状況: **{loc['status']}**"
        
        with st.expander(title_text):
            st.markdown(f"**情報元・管理組織**\n\n`{loc['source']}`")
            st.markdown("---")
            st.markdown(f"**歴史的教訓・状況説明**\n\n{loc['desc']}")
            st.markdown("---")
            if loc['link_url']:
                st.markdown(f"- <a href='{loc['link_url']}' target='_blank' rel='noopener noreferrer'>🌐 公式サイト・詳細データを確認する (別タブ)</a>", unsafe_allow_html=True)
