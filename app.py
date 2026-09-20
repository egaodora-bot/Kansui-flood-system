import streamlit as st
import urllib.request
import json

st.set_page_config(page_title="デバッグモード", layout="wide")
st.title("🛠️ 警告データ 取得デバッグ画面")

office_code = "130000" # 関東（東京地方）のコード
warning_url = f"https://www.jma.go.jp/bosai/warning/data/warning/{office_code}.json"

st.write(f"取得先URL: `{warning_url}`")

try:
    req = urllib.request.Request(warning_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as response:
        raw_data = response.read().decode('utf-8')
        data = json.loads(raw_data)
        st.success("✅ 気象庁JSONデータの取得に成功しました！")
        
        # データの構造を一部表示
        area_types = data.get("areaTypes", [])
        st.write(f"取得した areaTypes の数: {len(area_types)}")
        
        # 生データの最初の部分を表示
        st.json(data if len(raw_data) < 5000 else {"info": "データ量が大きいため最初の構造のみ省略表示します", "keys": list(data.keys())})
        
        # 警告ステータスの詳細チェック
        warnings_found = []
        for area_type in area_types:
            for area in area_type.get("areas", []):
                for w in area.get("warnings", []):
                    status = w.get("status")
                    code = w.get("code")
                    if status not in ["解除", "発表警報・注意報はなし", "", None]:
                        warnings_found.append({"area_code": area.get("code"), "code": code, "status": status})
        
        if warnings_found:
            st.warning(f"⚠️ 検出された有効な警告・注意報アイテム数: {len(warnings_found)}")
            st.write(warnings_found[:10])
        else:
            st.info("ℹ️ フィルター条件に合致する有効な警告（解除以外）は見つかりませんでした。")

except Exception as e:
    st.error(f"❌ データ取得エラーが発生しました: {e}")
