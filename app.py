import streamlit as st
import folium
from streamlit_folium import st_folium
import urllib.request
import json
import re

# ====================================================
# 1. 統合判定・リスク管理ロジック（フェイルセーフ対応）
# ====================================================
def get_integrated_safety_level(region_name: str):
    """
    一般警報データとキキクル（危険度分布）の判定を統合し、
    実態リスク（キキクル側での高まり）を優先して安全側に引き上げる関数。
    万が一のエラー時もアプリが落ちないようtry-exceptで完全保護します。
    """
    level = 0
    is_kikikuru_triggered = False
    
    # --- 通常の一般警報データの取得・判定処理 ---
    try:
        # ※ここに一般警報取得ロジック（JMA API等）が入ります
        general_warning_detected = False  # サンプル用の初期値
        
        if general_warning_detected:
            level = 3
    except Exception as e:
        print(f"一般警報データの取得エラー（通常継続します）: {e}")

    # --- キキクル（危険度分布）の優先判定・実態リスク統合 ---
    try:
        # ※ここにキキクルAPIやメッシュデータから危険度を取得する処理を記述
        # サンプルとして「キキクル側で危険（レベル3相当以上）が検知された」状態を想定
        kikikuru_danger_detected = True  # ← 実際のキキクル判定結果（True/False）に置き換えてください
        
        if kikikuru_danger_detected:
            # キキクル優先でレベルを最低でも3以上に引き上げ、フラグをONにする
            level = max(level, 3)
            is_kikikuru_triggered = True
            
    except Exception as e:
        # キキクル連携部分でエラーが起きても、通常の一般警報判定を維持してアプリを継続
        print(f"キキクル連携データ取得エラー（フォールバックします）: {e}")

    return level, is_kikikuru_triggered


# ====================================================
# 2. メイン処理・画面レイアウト (UI)
# ====================================================
def main():
    # ページ全体の設定
    st.set_page_config(page_title="運行規制・キキクルリアル状況", layout="wide")
    
    # タイトル表示
    st.title("鉄道・道路インフラの運行規制・キキクル・放射線リアル状況")

    # 【UI】青枠＋赤系文字のカスタムボタン（別タブで詳細キキクルへ遷移）
    st.markdown("""
    <div style="margin: 15px 0;">
        <button onclick="window.open('https://www.jma.go.jp/bosai/map.html', '_blank')" 
                style="background-color: transparent; color: #f87171; padding: 10px 18px; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer; border: 2px solid #3b82f6; display: inline-flex; align-items: center; gap: 8px;">
            <span style="color: #ef4444;">🔴</span>
            <span style="color: #f87171 !important;">詳細なキキクル情報（危険度分布）を気象庁サイトで確認する</span>
        </button>
    </div>
    """, unsafe_allow_html=True)

    # 対象エリアの指定
    region = "関東"
    
    # 統合レベルおよびキキクル検知フラグの取得
    current_level, kikikuru_triggered = get_integrated_safety_level(region)

    # サブタイトルと判定結果の表示
    st.subheader(f"⚠️ {region}エリアの緊急警戒レベル（レベル3〜5・キキクル統合判定）")

    # 状態に応じたアラート・メッセージの切り替え表示
    if current_level >= 3:
        if kikikuru_triggered:
            # キキクルによって危険度が高まったことを明示する警告表示（白文字・高コントラスト）
            st.markdown(f"""
            <div style="background-color: #7f1d1d; border-left: 6px solid #dc2626; padding: 15px; border-radius: 4px; color: #ffffff; margin-top: 10px;">
                <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; color: #ffffff;">
                    ⚠️ 【キキクル検知】対象エリアで実態リスクが高まっています（レベル{current_level}相当）
                </div>
                <ul style="margin: 0; padding-left: 20px; color: #f3f4f6; font-size: 14px;">
                    <li>気象庁キキクル（危険度分布）の優先判定により、警戒レベルが引き上げられています。</li>
                    <li>上記のボタンから詳細な危険度マップをご確認ください。</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ 対象エリアに緊急警戒レベル（レベル{current_level}）の警戒情報が検出されています。")
    else:
        st.info(f"🟢 現在、{region}エリアに緊急警戒レベル（レベル3〜5）の発表およびキキクル安全側シフトの発表はありません。")

    # ----------------------------------------------------
    # 3. マップ表示エリア（Folium連携）
    # ----------------------------------------------------
    st.markdown("### 🗺️ リアルタイム位置・インフラ状況マップ")
    
    # サンプルとして関東周辺を中心にしたFoliumマップを生成
    m = folium.Map(location=[36.0, 139.5], zoom_start=8, tiles="CartoDB dark_matter")
    
    # マップの描画
    st_folium(m, width="100%", height=400)

if __name__ == "__main__":
    main()
