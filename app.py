import streamlit as st

# ====================================================
# 1. 統合判定・リスク管理ロジック
# ====================================================
def get_integrated_safety_level(region_name: str):
    """
    一般警報データとキキクル（危険度分布）の判定を統合し、
    実態リスク（キキクル側での高まり）を優先して安全側に引き上げる関数。
    """
    level = 0
    is_kikikuru_triggered = False
    
    # --- 通常の一般警報データの取得・判定処理 ---
    try:
        general_warning_detected = False # サンプル用の初期値
        if general_warning_detected:
            level = 3
    except Exception as e:
        print(f"一般警報データの取得エラー: {e}")

    # --- キキクル（危険度分布）の優先判定・実態リスク統合 ---
    try:
        # サンプルとして「キキクル側で危険（レベル3相当以上）が検知された」状態を想定
        kikikuru_danger_detected = True  # ← 実際のキキクル判定結果（True/False）に置き換えてください
        
        if kikikuru_danger_detected:
            level = max(level, 3)
            is_kikikuru_triggered = True
            
    except Exception as e:
        print(f"キキクル連携データ取得エラー（フォールバックします）: {e}")

    return level, is_kikikuru_triggered


# ====================================================
# 2. 画面レイアウト・描画部分 (UI)
# ====================================================
def main():
    st.set_page_config(page_title="運行規制・キキクルリアル状況", layout="wide")
    
    st.title("鉄道・道路インフラの運行規制・キキクル・放射線リアル状況")

    # 【改善】ボタン背景をブルー系（#1e3a8a）にし、文字を白（#ffffff）にしてコントラストを確保
    st.markdown("""
    <div style="margin: 15px 0;">
        <a href="https://www.jma.go.jp/bosai/map.html" target="_blank" style="background: #1e3a8a; color: #ffffff !important; padding: 10px 16px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: bold; display: inline-block;">
            🔴 詳細なキキクル情報（危険度分布）を気象庁サイトで確認する
        </a>
    </div>
    """, unsafe_allow_html=True)

    # 対象エリアの指定
    region = "関東"
    
    # 統合レベルおよびキキクル検知フラグの取得
    current_level, kikikuru_triggered = get_integrated_safety_level(region)

    st.subheader(f"⚠️ {region}エリアの緊急警戒レベル（レベル3〜5・キキクル統合判定）")

    # 状態に応じたアラート・メッセージの切り替え表示
    if current_level >= 3:
        if kikikuru_triggered:
            # 【改善】streamlit標準の st.error を利用することで、ダークテーマでも文字が潰れず視認性が向上します
            st.error(f"""
            **【キキクル検知】対象エリアで実態リスクが高まっています（レベル{current_level}相当）**
            
            * 気象庁キキクル（危険度分布）の優先判定により、警戒レベルが引き上げられています。
            * 上記のボタンから詳細な危険度マップをご確認ください。
            """)
        else:
            st.warning(f"⚠️ 対象エリアに緊急警戒レベル（レベル{current_level}）の警戒情報が検出されています。")
    else:
        st.info(f"🟢 現在、{region}エリアに緊急警戒レベル（レベル3〜5）の発表およびキキクル安全側シフトの発表はありません。")

if __name__ == "__main__":
    main()
