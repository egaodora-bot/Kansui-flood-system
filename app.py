import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import xml.etree.ElementTree as ET
import json

st.set_page_config(page_title="全国統合防災・リスク管理システム", layout="wide")

st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    border-radius: 8px;
    font-weight: bold;
    transition: all 0.3s ease;
}
button[kind="primary"] {
    background-color: #0056b3 !important;
    border: 3px solid #004085 !important;
    color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 800 !important;
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
            {"title": "【防災情報】全国の気象警報・河川水位の最新情報をご確認ください", "link": "https://www.jma.go.jp/", "date": "現在"},
            {"title": "【交通情報】道路冠水・公共交通機関の運行状況を確認", "link": "https://www.jartic.or.jp/", "date": "現在"}
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
        "river_name": "---", "lat": 35.6895, "lon": 139.6917, "source": "東京都建設局 道路冠水情報", 
        "level": "レベル4", "level_desc": "【通行止め・水没危険】車両の進入・通行を厳に禁止。",
        "metric": "冠水深 40cm（車両水没のおそれ）", "status": "危険（通行止め）", "color": "red", "priority": 1,
        "desc": "ゲリラ豪雨によりアンダーパスが水没。立ち往生車両が発生し全面通行止め。",
        "camera_url": "https://www.kensetsu.metro.tokyo.lg.jp/"
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
        "level": "レベル3", "level_desc": "【高齢者等避難】水位上昇中。要配慮者は避難準備。",
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
        "category": "【河川氾濫】", "region": "関東", "pref": "新潟県", "name": "信濃川流域（新潟市下流）", 
        "river_name": "信濃川（しなのがわ）", "lat": 37.9161, "lon": 139.0364, "source": "国交省 北陸地方整備局", 
        "level": "レベル3", "level_desc": "【高齢者等避難】災害時要配慮者は避難を開始。一般住民も準備。",
        "metric": "観測 4.8m / 警戒 5.5m", "status": "注意（水位上昇中）", "color": "orange", "priority": 2,
        "desc": "日本最長の大きさを誇る一級河川。上流からの雪解け水と大雨で水位上昇。",
        "camera_url": ""
    },
    {
        "category": "【河川氾濫】", "region": "中部", "pref": "愛知県", "name": "木曽川流域（犬山市周辺）", 
        "river_name": "木曽川（きそがわ）", "lat": 35.3850, "lon": 136.9420, "source": "国交省 中部地方整備局", 
        "level": "レベル1", "level_desc": "【早期注意情報】気象情報に留意し、今後の動向を注視。",
        "metric": "観測 3.0m / 警戒 4.5m", "status": "正常（監視中）", "color": "blue", "priority": 3,
        "desc": "木曽三川の一つ。現在のところ安全水位を維持しています。",
        "camera_url": ""
    },
    {
        "category": "【高速道路】", "region": "関東", "pref": "埼玉県", "name": "東北自動車道（羽生IC〜館林IC）", 
        "river_name": "---", "lat": 36.1700, "lon": 139.5500, "source": "NEXCO東日本", 
        "level": "レベル3", "level_desc": "【交通規制】迂回ルートの検討および安全確認が必須。",
        "metric": "冠水影響による通行止め", "status": "注意（災害影響）", "color": "orange", "priority": 2,
        "desc": "大雨に伴う道路冠水のため、該当区間で上下線とも通行止め。",
        "camera_url": "https://www.c-nexco.co.jp/"
    },
    {
        "category": "【鉄道影響】", "region": "関東", "pref": "東京都", "name": "JR山手線・中央線", 
        "river_name": "---", "lat": 35.6812, "lon": 139.7671, "source": "JR東日本 運行情報", 
        "level": "レベル3", "level_desc": "【運行障害】運転見合わせ・大幅な遅延が発生中。",
        "metric": "一部運転見合わせ", "status": "注意（ダイヤ乱れ）", "color": "orange", "priority": 2,
        "desc": "大雨の影響および線路内点検のため、一部区間で運転見合わせ。",
        "camera_url": ""
    },
    {
        "category": "【河川氾濫】", "region": "関西", "pref": "大阪府", "name": "淀川流域（大阪市北区）", 
        "river_name": "淀川（よどがわ）", "lat": 34.7000, "lon": 135.5000, "source": "国交省 近畿地方整備局", 
        "level": "レベル1", "level_desc": "【早期注意情報】平常時・安全監視中。",
        "metric": "観測 2.1m / 警戒 5.0m", "status": "正常（監視中）", "color": "blue", "priority": 3,
        "desc": "関西の主要一級水系。安全水位を維持中。",
        "camera_url": ""
    },
    {
        "category": "【河川氾濫】", "region": "四国", "pref": "高知県", "name": "四万十川流域（中下流）", 
        "river_name": "四万十川（しまんとがわ）", "lat": 33.0000, "lon": 132.9333, "source": "国交省 四国地方整備局", 
        "level": "レベル1", "level_desc": "【早期注意情報】平常時・安全監視中。",
        "metric": "観測 5.2m / 警戒 6.5m", "status": "正常（監視中）", "color": "blue", "priority": 3,
        "desc": "日本最後の清流。現在のところ水位に異常なし。",
        "camera_url": ""
    }
]

danger_count = sum(1 for loc in locations if loc["color"] == "red")
warning_count = sum(1 for loc in locations if loc["color"] == "orange")

if danger_count > 0:
    st.error(f"🚨 【緊急警報発令中】 危険（赤）が **{danger_count}件**、注意（橙）が **{warning_count}件** 発生しています。警戒レベルを確認し、速やかな避難・安全確保を行ってください。")
else:
    st.warning(f"⚠️ 【注意喚起】 重大な危険（赤）はありませんが、**{warning_count}件** の注意情報が発表されています。")

st.markdown("<h3 style='font-size: 20px; font-weight: bold; margin-bottom: 0rem; color: #1e90ff; text-shadow: 1px 1px 2px rgba(0,0,0,0.3), 0 0 10px rgba(30,144,255,0.4);'>🛡️ 全国統合防災・リスク管理システム</h3>", unsafe_allow_html=True)
st.write("主要一級河川や道路冠水情報を警戒レベル・ライブ映像リンク付きで一元管理するシステムです。")

with st.expander("📡 【ライブ取得】リアルタイム災害・速報フィード（公的RSS連携）", expanded=True):
    news_list = fetch_robust_disaster_news()
    for news in news_list:
        st.markdown(f"- <a href='{news['link']}' target='_blank' style='color: #d32f2f; font-weight: bold;'>{news['title']}</a> <small style='color:gray;'>({news['date']})</small>", unsafe
