import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="全国一級河川・道路交通 リアルタイムモニタリング",
    page_icon="🌧️",
    layout="wide",
)

# インラインスタイルで確実にサイズを小さく固定
st.markdown(
    """
    <div style="font-size: 1.25rem; font-weight: bold; color: #FFFFFF; margin-bottom: 0.3rem;">
        🌧️ 全国一級河川・道路交通 リアルタイムモニタリング
    </div>
    <div style="font-size: 0.95rem; color: #CCCCCC; margin-bottom: 1rem;">
        主要一級河川や道路冠水情報を警戒レベル・ライブ映像リンク付きで一元管理するシステムです。
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

tab1, tab2 = st.tabs(["🗺️ マップ", "📋 リンク"])

with tab1:
  m = folium.Map(location=[35.6812, 139.7671], zoom_start=13)
  st_folium(m, width="100%", height=350)

with tab2:
  st.markdown("""
    - [x] **ハザードマップポータルサイト**
    - [x] **気象庁 警報・注意報**
    """)
