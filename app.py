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

/* 💡 ここを追加：ヘッダー（右上のアイコン等があるバー）を表示したままクリックを無効化する */
[data-testid="stHeader"] {
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)
