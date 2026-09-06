import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="全国一級河川・道路交通 リアルタイムモニタリング",
    page_icon="🌧️",
    layout="wide",
)

# 1. 災害アラート（上部バナー）
st.markdown(
    """
    <div style="background-color: #5c1d1d; color: #ffcccc; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 0.9rem;">
        🚨 <b>【緊急警報発令中】</b> 危険（赤）が3件、注意（橙）が5件発生しています。警戒レベルを確認し、速やかな避難・安全確保を行ってください。
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. タイトル（インラインスタイルで確実に小さくコンパクトに）
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

# 3. サイドバー（フィルターや凡例）
with st.sidebar:
  st.markdown("### 🔍 表示フィルター")
  st.checkbox("危険・注意（赤・橙）のみ表示", value=False)

  st.markdown("### 🗺️ 防災警戒レベル凡例")
  st.markdown(
      '<span style="color:red; font-weight:bold;">■</span> レベル4：避難指示',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<span style="color:orange; font-weight:bold;">■</span>'
      " レベル3：高齢者等避難",
      unsafe_allow_html=True,
  )
  st.markdown(
      '<span style="color:blue; font-weight:bold;">■</span> レベル1～2：早期注意',
      unsafe_allow_html=True,
  )

# 4. 地域選択ボタン
st.markdown("### 📍 表示地域の選択")
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5, col_btn6, col_btn7 = (
    st.columns(7)
)
with col_btn1:
  st.button("🇯🇵 日本全国", use_container_width=True, type="primary")
with col_btn2:
  st.button("北海道", use_container_width=True)
with col_btn3:
  st.button("東北", use_container_width=True)
with col_btn4:
  st.button("関東", use_container_width=True)
with col_btn5:
  st.button("関西", use_container_width=True)
with col_btn6:
  st.button("四国", use_container_width=True)
with col_btn7:
  st.button("九州", use_container_width=True)

st.divider()

# 5. メインタブ（マップ・リンク）
tab1, tab2 = st.tabs(["🗺️ マップ", "📋 リンク"])

with tab1:
  m = folium.Map(location=[35.6812, 139.7671], zoom_start=13)
  st_folium(m, width="100%", height=450)

with tab2:
  st.markdown("""
    - [x] **ハザードマップポータルサイト**（国土交通省）
    - [x] **気象庁 警報・注意報**
    """)