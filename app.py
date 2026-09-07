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
        "river_name": "木曽川（きそがわ）", "lat": 35.38
