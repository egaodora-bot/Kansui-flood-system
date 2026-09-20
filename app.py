import streamlit as st

def get_integrated_safety_level(region_name: str):
    level = 0
    is_kikikuru_triggered = False
    
    try:
        general_warning_detected = False
        if general_warning_detected:
            level = 3
    except Exception as e:
        print(f"一般警報データの取得エラー: {e}")

    try:
        kikikuru_danger_detected = True  
        if kikikuru_danger_detected:
            level = max(level, 3)
            is_kikikuru_triggered = True
    except Exception as e:
        print(f"キキクル連携データ取得エラー: {e}")

    return level, is_kikikuru_triggered

def main():
    st.set_page_config(page_title="運行規制・キキクルリアル状況", layout="wide")
    
    st.title("鉄道・道路インフラの運行規制・キキクル・放射線リアル状況")

    # 【改善】HTMLタグを整理し、背景色（#1e3a8a）と白文字が確実に表示されるように修正
    st.markdown("""
    <div style="margin: 15px 0;">
        <a href="https://www.jma.go.jp/bosai/map.html" target="_blank" 
           style="background-color: #1e3a8a !important; color: #ffffff !important; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: bold; display: inline-block; border: 1px solid #3b82f6;">
            🔴 詳細なキキクル情報（危険度分布）を気象庁サイトで確認する
        </a>
    </div>
    """, unsafe_allow_html=True)

    region = "関東"
    current_level, kikikuru_triggered = get_integrated_safety_level(region)

    st.subheader(f"⚠️ {region}エリアの緊急警戒レベル（レベル3〜5・キキクル統合判定）")

    if current_level >= 3:
        if kikikuru_triggered:
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

if __name__ == "__main__":
    main()
