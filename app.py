import streamlit as st
import urllib.request
import json
import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="冠水情報・防災システム",
    page_icon="🚨",
    layout="wide"
)

# --- スタイルの適用 ---
st.markdown("""
<style>
    .box-eew-alert {
        border: 2px solid #ef4444;
        background-color: rgba(239, 68, 68, 0.1);
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- P2P地震情報APIからデータ取得（パラメータ修正版） ---
@st.cache_data(ttl=0)
def fetch_p2p_earthquake_and_eew():
    # パラメータを修正（codesではなく、通常の履歴取得エンドポイントを利用）
    p2p_url = "https://api.p2pquake.net/v2/history?limit=10"
    try:
        req = urllib.request.Request(p2p_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            p2p_data = json.loads(response.read().decode('utf-8'))
        
        quakes = []
        eew_alerts = []
        p2p_scale_map = {
            10: "震度1", 20: "震度2", 30: "震度3", 40: "震度4",
            45: "震度5弱", 50: "震度5強", 55: "震度6弱", 60: "震度6強", 70: "震度7"
        }
        
        for item in p2p_data:
            code = item.get("code")
            # 556: 緊急地震速報, 551: 地震情報
            if code == 556:
                eew_alerts.append({
                    "time": item.get("time", "日時不明"),
                    "canceled": item.get("cancelled", False),
                    "message": item.get("issue", {}).get("type", "緊急地震速報発表")
                })
            elif code == 551:
                eq = item.get("earthquake", {})
                hypo = eq.get("hypocenter", {})
                scale = eq.get("maxScale", -1)
                quakes.append({
                    "time": eq.get("time", "日時不明"),
                    "hypocenter": hypo.get("name", "震源地不明"),
                    "max_scale": p2p_scale_map.get(scale, "不明"),
                    "magnitude": eq.get("magnitude", "--"),
                    "depth": hypo.get("depth", "--")
                })
        return {"success": True, "quakes": quakes, "eew": eew_alerts}
    except Exception as e:
        return {"success": False, "quakes": [], "eew": [], "error": str(e)}

# --- メイン画面レイアウト ---
st.title("🚨 冠水情報・防災監視システム")
st.write("地域の冠水状況およびリアルタイムの地震・緊急地震速報を確認できます。")

# --- 緊急地震速報 ＆ 地震情報セクション ---
st.markdown("### 🚨 緊急地震速報 ＆ 直近の地震発生履歴情報")

eq_data = fetch_p2p_earthquake_and_eew()

# 1. 緊急地震速報（EEW）のアラート表示
if eq_data["success"] and eq_data["eew"]:
    latest_eew = eq_data["eew"][0]
    eew_html = f"""
    <div class="box-eew-alert">
        <p style='margin: 0 0 4px 0; color: #ef4444; font-weight: bold; font-size: 16px;'>🚨 【緊急地震速報 検知】</p>
        <p style='margin: 2px 0;'>発表日時: {latest_eew['time']}</p>
        <p style='margin: 2px 0;'>状態: {'キャンセル報' if latest_eew['canceled'] else '速報発表中 (強い揺れに警戒してください)'}</p>
    </div>
    """
    st.markdown(eew_html, unsafe_allow_html=True)
else:
    st.info("現在、緊急地震速報の発表はありません（常時監視中）。")

# 2. 直近の地震履歴を複数件リスト表示
if eq_data["success"] and eq_data["quakes"]:
    st.markdown("#### 📜 直近の地震発生履歴（最大5件）")
    
    for i, eq in enumerate(eq_data["quakes"][:5]):
        border_color = "#ef4444" if i == 0 else "#3b82f6"
        bg_color = "rgba(239, 68, 68, 0.05)" if i == 0 else "rgba(59, 130, 246, 0.03)"
        
        eq_card_html = f"""
        <div style="border: 1px solid {border_color}; background-color: {bg_color}; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 4px;">
                <span>📍 震源地: {eq['hypocenter']}</span>
                <span style="color: {border_color};">最大震度: {eq['max_scale']}</span>
            </div>
            <div style="font-size: 13px; color: #cbd5e1;">
                <span>🕒 発生日時: {eq['time']}</span> | 
                <span>マグニチュード(M): {eq['magnitude']}</span> | 
                <span>深さ: {eq['depth']}km</span>
            </div>
        </div>
        """
        st.markdown(eq_card_html, unsafe_allow_html=True)
else:
    st.warning("地震データの取得に失敗したか、データがありません。")
    if "error" in eq_data:
        st.caption(f"エラー詳細: {eq_data['error']}")

# --- その他の防災リンク・冠水情報セクション ---
st.markdown("---")
st.markdown("### 🗺️ 気象・冠水リンク集")
col1, col2 = st.columns(2)
with col1:
    st.markdown("- [Windy (気象・風速予測)](https://www.windy.com/)")
    st.markdown("- [Yahoo! リアルタイム天気・雨雲レーダー](https://weather.yahoo.co.jp/weather/)")
with col2:
    st.markdown("- [川の防災情報 (国土交通省)](https://www.river.go.jp/)")
    st.markdown("- [P2P地震情報](https://www.p2pquake.net/)")
