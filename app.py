import streamlit as st

# ページ全体の基本設定
st.set_page_config(
    page_title="アプリの使い方・仕様",
    page_icon="📌",
    layout="centered"
)

# --- CSSによるスタイリング（タイトルに下線を追加し、視認性を向上） ---
st.markdown("""
<style>
/* ページ全体の背景や文字色の調整 */
.stApp {
    background-color: #0f172a;
    color: #f8fafc;
}

/* expander全体の枠組み */
div[data-testid="stExpander"] {
    background-color: #1e293b !important;
    border: 1px solid #475569 !important;
    border-left: 7px solid #10b981 !important;
    border-radius: 8px !important;
    margin-bottom: 12px !important;
}

/* expanderのタイトル部分（ここに下線とパディングを追加して立体感を演出） */
div[data-testid="stExpander"] summary p {
    font-weight: 900 !important;
    color: #ffffff !important;
    font-size: 16px !important;
    border-bottom: 2px solid #3b82f6 !important; /* 目立つ青い下線 */
    padding-bottom: 6px !important;            /* 文字と下線の間の隙間 */
}

/* 展開された中身のテキスト色 */
div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] p {
    color: #cbd5e1 !important;
}
</style>
""", unsafe_allow_html=True)

# --- アプリのメインコンテンツ ---
st.title("📌 アプリのご案内・仕様")
st.write("各項目をタップして詳細をご確認ください。")

st.markdown("---")

# 各アコーディオン（expander）
with st.expander("🎯 開発コンセプト"):
    st.write("このアプリは、日々の情報確認を素早く、ストレスなく行えるように設計されています。シンプルで直感的な操作性を最優先に開発しています。")

with st.expander("⏳ サーバー仕様によるスリープ復帰について（半日ほどアクセスがない場合）"):
    st.write("無料サーバーで運用しているため、半日ほどアクセスがないとサーバーが自動的にスリープ状態（休止）に入ります。\n\n**【復帰方法】**\nアクセスした際に画面が少し読み込み中になりますが、そのまま10〜20秒ほどお待ちいただくと自動で復帰します。")

with st.expander("🔄 画面を横向きにすると見やすくなります"):
    st.write("スマホやタブレットをご利用の際、表や細かいデータが見づらい場合は、**画面を横向き（ランドスケープ）**にしていただくと、より広く快適に表示されます。")

with st.expander("📲 フリーズ・スリープした時"):
    st.write("もし画面が固まったり反応しなくなった場合は、お手数ですが**ブラウザの再読み込み（更新ボタン）**を行ってください。最新の状態で再度スムーズにご利用いただけます。")

with st.expander("📌 基本的な使い方"):
    st.write("1. 気になる項目をタップして開きます。\n2. 必要に応じて条件を切り替えて情報を確認してください。\n3. 自動で最新データに更新されます。")
