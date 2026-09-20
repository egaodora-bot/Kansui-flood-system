# ガイドセクション（HTMLを正しく解釈させるための記述）
st.markdown(
    """
    <div class="custom-card">
        <div style="font-size: 15px; font-weight: bold; color: #38bdf8; margin-bottom: 8px;">📱 2軸表示システム設計仕様 & 操作ガイドのご案内</div>
        
        <div style="font-size: 13px; font-weight: bold; color: #60a5fa; margin-top: 10px;">🎯 1. 警報とキキクルの独立同時表示（2軸並列設計）</div>
        <div style="font-size: 13px; color: #ffffff; line-height: 1.6; margin-top: 2px;">
            本システムでは、監視エリアを選択すると、<span style="color: #fde047;">「市区町村単位の気象庁警報・注意報ベース」</span>と、実況・解析に基づく<span style="color: #fde047;">「キキクル（危険度分布）の現象別リアルタイム評価」</span>の両方を同時に切り替え連動して表示します。
        </div>
        
        <div style="font-size: 13px; font-weight: bold; color: #60a5fa; margin-top: 12px;">🗺️ 2. 地図およびエリア連動の操作方法について</div>
        <div style="font-size: 13px; color: #ffffff; line-height: 1.6; margin-top: 2px;">
            上のセレクトボックスでエリアを選択するか、あるいは<span style="color: #fde047;">地図上の各地域や都道府県を選択・クリックしていただくことで、連動して下部の詳細な防災データや機器ステータスが切り替わります。</span>地図単体ではなく、選択操作によって地域ごとの詳細情報を確認できる仕様となっています。
        </div>
        
        <div style="font-size: 13px; font-weight: bold; color: #60a5fa; margin-top: 12px;">📱 3. スマートフォン等でのご利用時の注意</div>
        <div style="font-size: 13px; color: #ffffff; line-height: 1.6; margin-top: 2px;">
            端末を「横向き」にしていただくと、地図および各詳細データやリンクがより一覧しやすくなります。ぜひお試しください。
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
