import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="全国一級河川・道路交通 リアルタイムモニタリング",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded",
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

# 2. タイトル（コンパクト表示）
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

# 3. サイドバー（フィルターと凡例）
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

# 5. マップ表示
m = folium.Map(location=[35.6812, 139.7671], zoom_start=13)
st_folium(m, width="100%", height=400)

st.divider()

# 6. レベル別地点リスト＆各種リンク（カメラ・ネクスコ等）の統合表示
st.markdown("### 📊 警戒レベル別 該当地点・ライブ映像リンク")

st.markdown(
    '<span style="color:red; font-weight:bold;">🔴 レベル5・4（避難指示等）</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "- [A河川 〇〇地点] 警戒水位超え ［[ライブカメラ映像](https://example.com)"
    " / [川の防災情報](https://www.river.go.jp/)］"
)
st.markdown(
    "- [B高速道路 〇〇区間] 冠水通行止め ［[NEXCO 道路交通情報](https://www.c-nexco.co.jp/)"
    " / [JARTIC](https://www.jartic.or.jp/)］"
)

st.markdown(
    '<span style="color:orange; font-weight:bold;">🟠 レベル3（高齢者等避難）</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "- [C河川 △△地点] 水位上昇中 ［[ライブカメラ映像](https://example.com)］"
)

st.markdown(
    '<span style="color:blue; font-weight:bold;">🔵 レベル1・2（早期注意）</span>',
    unsafe_allow_html=True,
)
st.markdown("- [D河川 □□地点] 通常監視中")

st.divider()

# 7. 外部お役立ちリンク集
st.markdown("### 📋 防災・交通インフラリンク集")
st.markdown("""
- 🌐 **[ハザードマップポータルサイト](https://disaportal.gsi.go.jp/)**（国土交通省）
- 📡 **[気象庁 警報・注意報](https://www.jma.go.jp/bosai/)**
- 🚗 **[JARTIC 道路交通情報センター](https://www.jartic.or.jp/)**
- 📷 **[川の防災情報（ライブカメラ等）](https://www.river.go.jp/)**
""")
