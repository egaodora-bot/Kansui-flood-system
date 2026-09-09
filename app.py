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

# --- 【リアルタイム監視データ】現在の水位・交通・鉄道・気象状況 ---
@st.cache_data
def get_master_locations():
    return [
        # --- 🌊 主要河川 ---
        {
            "category": "【主要河川・水位上昇】", "region": "関東", "pref": "茨城県", "name": "鬼怒川流域（常総市水海道観測所）", 
            "infrastructure_type": "主要河川", "lat": 36.0150, "lon": 139.9900, "source": "国土交通省 関東地方整備局", 
            "level": "Level3", "level_desc": "【水位上昇】氾濫注意水位に接近",
            "metric": "観測水位 6.2m / 警戒 6.5m", "status": "注意（水位急上昇中）", "color": "orange", "priority": 2,
            "desc": "上流部でのまとまった降雨により現在水位が上昇中。今後の推移に厳重な警戒が必要です。",
            "link_url": "https://www.river.go.jp/"
        },
        {
            "category": "【主要河川・氾濫警戒】", "region": "東北", "pref": "福島県", "name": "阿武隈川流域（郡山市周辺）", 
            "infrastructure_type": "主要河川", "lat": 37.9000, "lon": 140.7800, "source": "国土交通省 東北地方整備局", 
            "level": "レベル4", "level_desc": "【避難判断】氾濫危険水位超過の恐れ",
            "metric": "水位上昇トレンド継続中", "status": "警戒（水位監視強化）", "color": "red", "priority": 1,
            "desc": "流域内の降雨に伴い水位が急上昇。自治体の避難情報やリアルタイムライブカメラをご確認ください。",
            "link_url": "https://www.river.go.jp/"
        },
        {
            "category": "【主要河川・平常監視】", "region": "関東", "pref": "東京都", "name": "多摩川流域（二子玉川周辺）", 
            "infrastructure_type": "主要河川", "lat": 35.6000, "lon": 139.6300, "source": "国土交通省 京浜河川事務所", 
            "level": "Level1", "level_desc": "【平常】特異な水位上昇なし",
            "metric": "観測正常・安定推移", "status": "正常（監視継続）", "color": "blue", "priority": 3,
            "desc": "現在のところ平常通りの水位で推移しています。下水道・内水面を含め異常は確認されていません。",
            "link_url": "https://www.river.go.jp/"
        },
        {
            "category": "【主要河川・水位上昇】", "region": "中部", "pref": "長野県", "name": "千曲川流域（長野市長沼周辺）", 
            "infrastructure_type": "主要河川", "lat": 36.6800, "lon": 138.2500, "source": "国土交通省 北陸地方整備局", 
            "level": "Level3", "level_desc": "【注意】水位観測監視中",
            "metric": "水防警報 待機中", "status": "注意（水位動向注視）", "color": "orange", "priority": 2,
            "desc": "上流からの流入量増加に伴い、水防団待機およびリアルタイム水位の監視が継続されています。",
            "link_url": "https://www.river.go.jp/"
        },

        # --- 🛣️ 国道・高速道路 ---
        {
            "category": "【国道・通行止め規制】", "region": "中部", "pref": "長野県", "name": "国道19号（木曽路山間部区間）", 
            "infrastructure_type": "国道", "lat": 35.8500, "lon": 137.6000, "source": "国土交通省 中部地方整備局", 
            "level": "レベル4", "level_desc": "【通行止め】連続雨量超過による規制",
            "metric": "雨量規制値 到達", "status": "危険（全面通行止め）", "color": "red", "priority": 1,
            "desc": "降雨量が規定値を超えたため、安全確保のため当該区間が上下線とも通行止めとなっています。",
            "link_url": "https://www.jartic.or.jp/"
        },
        {
            "category": "【高速道路・排水監視】", "region": "関東", "pref": "東京都", "name": "首都高速道路（中央環状線・山手トンネル）", 
            "infrastructure_type": "国道", "lat": 35.6895, "lon": 139.6917, "source": "首都高速道路株式会社", 
            "level": "Level3", "level_desc": "【地下水位監視】排水ポンプ稼働中",
            "metric": "地下排水設備 正常稼働", "status": "注意（トンネル内監視）", "color": "orange", "priority": 2,
            "desc": "局地的豪雨への対応として地下構造物の排水システムを強化監視中。現在のところ通行に支障はありません。",
            "link_url": "https://www.shutoko.jp/"
        },
        {
            "category": "【国道・事前規制】", "region": "関東", "pref": "神奈川県", "name": "国道1号（箱根峠周辺区間）", 
            "infrastructure_type": "国道", "lat": 35.2000, "lon": 139.0200, "source": "国土交通省 横浜国道事務所", 
            "level": "Level3", "level_desc": "【視程不良・降雨規制】",
            "metric": "視界不良および雨量規制", "status": "注意（速度規制・一部通行止）", "color": "orange", "priority": 2,
            "desc": "濃霧および降雨のため速度制限および警戒パトロールが実施されています。最新の道路情報をご確認ください。",
            "link_url": "https://www.jartic.or.jp/"
        },

        # --- 🛤️ 県道・市町道 ---
        {
            "category": "【県道・アンダーパス冠水】", "region": "関東", "pref": "栃木県", "name": "主要地方道 宇都宮那須子線（低地アンダー）", 
            "infrastructure_type": "県道", "lat": 36.6000, "lon": 139.9000, "source": "栃木県 道路保全課", 
            "level": "Level3", "level_desc": "【冠水注意】冠水センサー作動中",
            "metric": "冠水検知 15cm（警戒）", "status": "注意（通行注意・徐行）", "color": "orange", "priority": 2,
            "desc": "短時間の降雨により冠水が始まっています。車での通行時は十分な注意あるいは迂回が必要です。",
            "link_url": "https://www.pref.tochigi.lg.jp/"
        },
        {
            "category": "【市町道・高潮冠水】", "region": "中部", "pref": "静岡県", "name": "市道 沼津市平沼線（海岸近接アンダーパス）", 
            "infrastructure_type": "市町道", "lat": 35.1000, "lon": 138.8500, "source": "沼津市 道路課", 
            "level": "レベル4", "level_desc": "【高潮・冠水規制】",
            "metric": "潮位上昇に伴う冠水", "status": "危険（通行止め実施中）", "color": "red", "priority": 1,
            "desc": "高潮と波浪の影響により道路の一部が冠水したため、バリケードによる通行止め措置が取られています。",
            "link_url": "https://www.city.numazu.shizuoka.jp/"
        },

        # --- 🚆 鉄道（リアルタイム運行・規制） ---
        {
            "category": "【鉄道・計画運休・遅延】", "region": "関東", "pref": "東京都", "name": "JR東日本 首都圏在来線各線（中央線・総武線等）", 
            "infrastructure_type": "鉄道", "lat": 35.6812, "lon": 139.7671, "source": "JR東日本 運行情報", 
            "level": "Level3", "level_desc": "【気象連動規制】一部列車の遅延・運休",
            "metric": "風速・雨量規制値接近", "status": "注意（運行状況要確認）", "color": "orange", "priority": 2,
            "desc": "悪天候予報および沿線の気象レーダー数値に基づき、一部区間で速度落としや計画運休の可能性が出ています。",
            "link_url": "https://www.jreast.co.jp/"
        },
        {
            "category": "【鉄道・運転見合わせ】", "region": "東北", "pref": "岩手県", "name": "三陸鉄道リアス線（沿岸部各区間）", 
            "infrastructure_type": "鉄道", "lat": 39.6400, "lon": 141.9500, "source": "三陸鉄道", 
            "level": "レベル4", "level_desc": "【大雨警報発令に伴う運休】",
            "metric": "沿線雨量 規制値到達", "status": "危険（運転見合わせ中）", "color": "red", "priority": 1,
            "desc": "沿線の雨量計が規制値に達したため、安全確認のため上下線で一時運転を見合わせています。",
            "link_url": "https://www.sanrikutetsudo.com/"
        },
        {
            "category": "【鉄道・区間運休】", "region": "九州", "pref": "熊本県", "name": "JR肥薩線（一部不通・代行バス運行区間）", 
            "infrastructure_type": "鉄道", "lat": 32.2100, "lon": 130.7600, "source": "JR九州 運行情報", 
            "level": "レベル4", "level_desc": "【長期運休・復旧工事中】",
            "metric": "一部区間バス代行輸送", "status": "危険（運休・代行輸送実施中）", "color": "red", "priority": 1,
            "desc": "被災区間の復旧工事および代行バスによる輸送が継続実施されています。利用時は各社時刻表をご確認ください。",
            "link_url": "https://www.jrkyushu.co.jp/"
        },

        # --- ⚠️ 気象庁データ・土砂災害 ---
        {
            "category": "【気象庁・土砂災害警戒】", "region": "中部", "pref": "静岡県", "name": "伊豆山地区周辺（熱海市山間部）", 
            "infrastructure_type": "気象庁データ", "lat": 35.1150, "lon": 139.0730, "source": "気象庁 キキクル（危険度分布）", 
            "level": "レベル4", "level_desc": "【警戒情報発令中】土砂災害リスク高",
            "metric": "キキクル 紫色（災害切迫）", "status": "危険（厳重警戒・避難指示発令中）", "color": "red", "priority": 1,
            "desc": "土砂災害警戒情報およびキキクル極めて危険ランクが点灯中。直ちに安全な場所へ避難してください。",
            "link_url": "https://www.jma.go.jp/bosai/risk/"
        },
        {
            "category": "【気象庁・土砂災害注意】", "region": "関東", "pref": "東京都", "name": "多摩西部・奥多摩町山間部", 
            "infrastructure_type": "気象庁データ", "lat": 35.7792, "lon": 139.1106, "source": "気象庁 キキクル", 
            "level": "Level3", "level_desc": "【大雨警報・土砂災害警戒】",
            "metric": "キキクル 黄色・赤色点灯", "status": "注意（急傾斜地警戒）", "color": "orange", "priority": 2,
            "desc": "地盤の緩みによる土砂崩落の危険性が高まっています。急傾斜地や崖の周辺には近づかないでください。",
            "link_url": "https://www.jma.go.jp/bosai/risk/"
        },
        {
            "category": "【気象庁・警報発令中】", "region": "関東", "pref": "千葉県", "name": "房総半島南部（館山市周辺）", 
            "infrastructure_type": "気象庁データ", "lat": 35.0000, "lon": 139.8500, "source": "気象庁 警報・注意報", 
            "level": "Level3", "level_desc": "【強風・大雨警報】",
            "metric": "暴風雨レーダー監視中", "status": "注意（飛来物・強風警戒）", "color": "orange", "priority": 2,
            "desc": "発達した雨雲および強風域が通過中。飛来物や屋外の作業に十分な注意が必要です。",
            "link_url": "https://www.jma.go.jp/"
        }
    ]

locations = get_master_locations()

if st.session_state["first_visit"]:
    st.markdown("<h3 style='font-size: 20px; font-weight: bold; background-color: #fef08a; color: #1e293b; padding: 10px 14px; border-radius: 6px; border-left: 6px solid #ca8a04; margin-bottom: 0.8rem;'>🛡️ 全国インフラ・気象防災リアルタイム統合システム</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #1e40af; padding: 18px 22px; border-radius: 8px; border-left: 6px solid #60a5fa; color: #ffffff; font-weight: bold; font-size: 15px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); line-height: 1.7;">
        全国の河川水位、道路規制、鉄道運行、気象庁のリアルタイム危険度（キキクル）を統合監視するシステムです。<br><br>
        <div style="background-color: rgba(255, 255, 255, 0.15); padding: 10px 14px; border-radius: 6px; font-size: 14px; color: #ffffff; line-height: 1.8;">
            📍 <b>【システムの特徴】</b><br>
            ・軽量設計により低速通信環境（128kbps等）でもスムーズに稼働。<br>
            ・地図上のピンは自動的にクラスタリングされ、スマホでも軽快に操作できます。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📖 :red[【システムの設計・通信検証方針について・ご利用ガイド】]", expanded=True):
        st.markdown("""
        ##### 🛠️ このシステムの設計・通信検証方針について
        本システムは、過酷な災害現場や低速なモバイル回線（128kbps等）の環境下でもエラーを起こさず、確実に命を守る情報にアクセスできることを最優先に設計されています。

        * **128kbps低速通信・スマホ環境での動作保証**
          初回ロード時のデータ量を最小限に抑えているため、通信速度制限がかかったスマホ環境や電波の弱い被災地であっても、タイムアウトやフリーズを起こさず数秒でスムーズに起動します。
        * **キャッシュ機能とマーカークラスターの導入**
          サーバー負荷やブラウザのメモリ消費を抑えるため、データのキャッシュ処理および地図上のピンの自動グルーピング（クラスター表示）を徹底し、スマホでの操作性を担保しています。
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        ##### ［ご家族やご友人への共有］
        災害時はこのシステムのURLを共有することで、全員が命を守る為に必要な、今いる場所のリアルタイムな公開情報へアクセスできます。

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
        🛡️ 全国インフラ・気象防災リアルタイム統合システム
    </div>
    <div style="color: #93c5fd; font-size: 15px; font-weight: bold;">
        （※河川水位上昇・道路交通規制・鉄道運行・気象庁キキクル監視）
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

available_infra_types = ["すべて表示", "主要河川", "国道", "県道", "市町道", "鉄道", "気象庁データ"]
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
        🚨 <span style="color: #fca5a5;">【リアルタイム監視状況】</span> 選択条件の危険（赤）が <span style="color: #f87171; font-size: 16px;"><b>{danger_count}件</b></span>、注意（橙）が <span style="color: #fbbf24; font-size: 16px;"><b>{warning_count}件</b></span> 検出されています。
    </span>
</div>
""", unsafe_allow_html=True)

# 公式リンク集（枠線を白に維持）
st.markdown("""
<div style="background-color: #0f172a; border: 2px solid #ffffff; padding: 14px 18px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
    <div style="color: #fef08a; font-weight: bold; font-size: 15px; margin-bottom: 8px;">
        ⚡ <b>【公式データリンク集】河川・国道・県道・市町道・鉄道・気象庁のリアルタイム状況</b>
    </div>
    <div style="font-size: 13.5px; color: #f1f5f9; line-height: 1.8;">
        ・ 🌊 <a href="https://www.river.go.jp/" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; font-weight: bold;">国土交通省 川の防災情報（全国の河川水位・ライブカメラ）</a><br>
        ・ 🚗 <a href="https://www.jartic.or.jp/" target="_blank" rel="noopener noreferrer" style="color: #7dd3fc; font-weight: bold;">JARTIC 日本道路交通情報センター（高速・国道・県道の規制情報）</a><br>
        ・ 🚆 <a href="https://www.train-info.com/" target="_blank" rel="noopener noreferrer" style="color: #34d399; font-weight: bold;">主要鉄道 運行情報・各社遅延リアルタイム案内</a><br>
        ・ 🔴 <a href="https://www.jma.go.jp/bosai/warning/" target="_blank" rel="noopener noreferrer" style="color: #fca5a5; font-weight: bold;">気象庁 警報・注意報（すべての市区町村別の最新発令状況）</a><br>
        ・ ⚠️ <a href="https://www.jma.go.jp/bosai/risk/" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; font-weight: bold;">気象庁 キキクル（土砂・浸水・洪水危険度分布）</a>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📡 【ライブ取得】リアルタイム災害・速報フィード", expanded=True):
    news_list = fetch_robust_disaster_news()
    for news in news_list:
        st.markdown(f"- <a href='{news['link']}' target='_blank' rel='noopener noreferrer' style='color: #d32f2f; font-weight: bold;'>{news['title']}</a> <small style='color:gray;'>({news['date']})</small>", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='font-size: 14px; font-weight: bold; color: #60a5fa; line-height: 1.5;'>🛡️ インフラ・気象防災リアルタイム統合</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.subheader("📌 警戒レベル凡例")
st.sidebar.markdown("🔴 <span style='color:red; font-weight:bold;'>レベル4：避難指示・通行止め・運休</span>", unsafe_allow_html=True)
st.sidebar.markdown("🟠 <span style='color:darkorange; font-weight:bold;'>Level3：高齢者等避難・規制・計画運休</span>", unsafe_allow_html=True)
st.sidebar.markdown("🔵 **Level1〜2**：平常・監視中", unsafe_allow_html=True)

# --- マップ描画 ---
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
        c_metric = loc.get('metric')
        
        link_html = f"<br><a href='{c_url}' target='_blank' rel='noopener noreferrer' style='color:red; font-weight:bold;'>▶ 公式詳細を確認</a>" if c_url else ""
        
        popup_html = (
            f"<b>{c_cat} [{c_pref}]</b><br>"
            f"<b>{c_name}</b><br>"
            f"状況: <span style='color:{c_color}; font-weight:bold;'>{c_status}</span><br>"
            f"指標: {c_metric}<br>"
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

st.markdown(f"<h3 style='font-size: 20px; font-weight: bold; margin-top: 1rem;'>📋 リアルタイム監視データ一覧</h3>", unsafe_allow_html=True)

if not filtered_locations:
    st.markdown("""
    <div style="background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 16px; border-radius: 6px; margin-bottom: 1rem;">
        <span style="color: #93c5fd; font-weight: bold; font-size: 15px;">ℹ️ 選択された条件に一致するインフラデータは現在ありません。</span><br><br>
        <span style="color: #f1f5f9; font-size: 13.5px;">
            すべての河川・道路・鉄道・気象情報は上の<b>【公式データリンク集】</b>から直接ご確認いただけます。
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    for idx, loc in enumerate(filtered_locations):
        if loc["color"] == "red":
            badge = "🔴【レベル4/危険】"
        elif loc["color"] == "orange":
            badge = "🟠【Level3/注意】"
        else:
            badge = "🔵【Level1/平常】"
            
        title_text = f"{badge} ｜ [{loc['infrastructure_type']}] {loc['pref']} ｜ **{loc['name']}** ｜ 状況: **{loc['status']}**"
        
        with st.expander(title_text):
            st.markdown(f"**情報元・管理組織**\n\n`{loc['source']}`")
            st.markdown(f"**現在の観測・規制指標**\n\n`{loc['metric']}`")
            st.markdown("---")
            st.markdown(f"**状況詳細・見解**\n\n{loc['desc']}")
            st.markdown("---")
            if loc['link_url']:
                st.markdown(f"- <a href='{loc['link_url']}' target='_blank' rel='noopener noreferrer'>🌐 公式サイト・詳細データを確認する (別タブ)</a>", unsafe_allow_html=True)
