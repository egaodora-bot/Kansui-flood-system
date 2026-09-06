from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Literal
import os

# 1. 構造化データの定義
class MunicipalFloodStatus(BaseModel):
    municipality: str = Field(description="対象の市区町村名 (例: 大阪府大阪市北区)")
    source_type: Literal["IoTセンサー", "公式ライブカメラ", "現地住民レポート"] = Field(description="情報の情報源")
    reliability_score: int = Field(description="情報の信頼度スコア (1〜5)")
    water_level_status: Literal["安全", "注意", "危険 (冠水発生)"] = Field(description="冠水ステータス")
    depth_cm: int = Field(description="推定浸水深（cm）。不明な場合は0")
    summary: str = Field(description="状況の要約")

def analyze_flood_report(text_prompt: str, image_path: str = None):
    client = genai.Client()
    
    contents = [text_prompt]
    
    # 画像ファイルが指定されている場合は、マルチモーダル入力として追加
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # 画像のMIMEタイプを自動判定または指定
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg", 
        )
        contents.append(image_part)

    # Gemini APIの呼び出し（gemini-2.5-flashを使用）
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MunicipalFloodStatus,
            temperature=0.0,
        ),
    )

    return response.parsed

if __name__ == "__main__":
    # テスト実行
    prompt = "以下の現地レポートと添付された写真（もしあれば）を分析し、市区町村ごとの冠水状況を構造化してください。地域は東京都世田谷区と想定します。"
    
    # ※手元にテスト用の画像がある場合はファイルパスを指定できます（なければNone）
    result = analyze_flood_report(prompt, image_path=None)
    
    print("\n--- 解析結果 ---")
    print(result)