# main.py
import os
import openai
import requests
from datetime import datetime

# === 環境變數 ===
OPENAI_KEY = os.getenv("OPENAI_KEY")
ELEVEN_KEY = os.getenv("ELEVEN_KEY")
VOICE_ID = os.getenv("VOICE_ID")

# === Step 1: 撰寫播報稿（12分鐘左右） ===
openai.api_key = OPENAI_KEY

today = datetime.now().strftime("%Y/%m/%d")
prompt = f"""
你是一位有經驗的中文 Podcast 播報員，語氣像親切的中年大叔。
請用口語化方式，播報以下主題的內容，總長度約 12 分鐘：

- 今天凌晨美股四大指數（道瓊、那斯達克、標普500、費城半導體）收盤與分析
- QQQ、SPY ETF 走勢與分析，包含比特幣與黃金報價
- 資金流向與熱門產業類股
- 今日 Top 5 熱門股解析
- 一則最新 AI 技術或熱門總體經濟，財經重要新聞解讀
- 每日投資金句，作為結尾

今天日期為 {today}
請以親切、自然口語風格完成播報稿。
"""

response = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[{"role": "user", "content": prompt}]
)

script_text = response.choices[0].message.content

with open("script.txt", "w", encoding="utf-8") as f:
    f.write(script_text)

# === Step 2: 語音合成 ===
headers = {
    "xi-api-key": ELEVEN_KEY,
    "Content-Type": "application/json"
}
data = {
    "text": script_text,
    "voice_id": VOICE_ID,
    "model_id": "eleven_multilingual_v2",
    "output_format": "mp3"
}

response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
    headers=headers,
    json={"text": script_text}
)

with open("daily_podcast.mp3", "wb") as f:
    f.write(response.content)

# === Step 3: 輸出路徑提示 ===
print("✅ 播報稿已完成：script.txt")
print("✅ 語音檔已生成：daily_podcast.mp3")
print("🔊 請登入 RSS.com 並手動上傳該音檔。")
