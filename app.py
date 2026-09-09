with st.expander("📖 :red[【ご利用ガイド・命を守る共有方法】]", expanded=True):
        st.markdown("""
        ##### ［ご家族やご友人への共有］
        災害時はこのシステムのURLを共有することで、全員が命を守る為に必要な、今いる場所が掲載している最新公開情報へアクセスできます。

        ##### ［📱 クイックにアクセスする為、スマホのホーム画面への追加］
        ブラウザメニューから「ホーム画面に追加」を行うと、専用アプリのようにワンタップで起動できます。(推奨)
        """, unsafe_allow_html=True)
        
        # 目立つように背景色と枠線をつけた案内メッセージ
        st.markdown("""
        <div style="background-color: rgba(253, 224, 71, 0.15); border-left: 5px solid #fde047; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; margin-top: 10px;">
            <span style="color: #fef08a; font-weight: bold; font-size: 14.5px;">
                👆 内容をご確認の上、以下のボタンを押してシステムを開始してください。
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("確認しました（システムを開始する）", type="primary"):
            st.session_state["first_visit"] = False
            st.rerun()
