import os
from datetime import datetime
from openai import OpenAI
import requests


# ✅ 明確取得環境變數
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVEN_KEY")
VOICE_ID = os.getenv("VOICE_ID")

# ✅ 初始化 OpenAI 客戶端（新版 SDK 必備）
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ 產生播報稿內容
today = datetime.now().strftime("%Y/%m/%d")

prompt = f"""
你是一位有經驗的中文 Podcast 播報員，語氣像親切的中年大叔。
請用口語化方式，播報以下主題的內容，總長度約 12 分鐘：

1. 今天凌晨美股四大指數（道瓊、那斯達克、標普500、費城半導體）收盤與分析
2. QQQ、SPY ETF 走勢與分析，包含比特幣與黃金報價
3. 資金流向與熱門產業類股
4. 今日 Top 5 熱門股解析
5. 一則最新 AI 技術或新聞解讀
6. 每日投資金句，作為結尾

今天日期為 {today}
請用自然親切的口語化方式播報。
"""

# ✅ 使用 GPT-4 生成中文播報稿
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "你是一位中文 Podcast 播報員"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.8
)

script_text = response.choices[0].message.content.strip()

# ✅ 儲存播報稿
with open("script.txt", "w", encoding="utf-8") as f:
    f.write(script_text)

# ✅ 合成語音（ElevenLabs 中文男聲）
headers = {
    "xi-api-key": ELEVEN_KEY,
    "Content-Type": "application/json"
}
data = {
    "text": script_text,
    "model_id": "eleven_multilingual_v2",  # 適用中文語音
    "voice_settings": {
        "stability": 0.4,
        "similarity_boost": 0.8
    }
}

response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
    headers=headers,
    json=data
)

# ✅ 存成 MP3 音檔
with open("daily_podcast.mp3", "wb") as f:
    f.write(response.content)

print("✅ 播報稿完成（script.txt）")
print("✅ 語音檔已輸出（daily_podcast.mp3）")
