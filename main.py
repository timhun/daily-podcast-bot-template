from openai import OpenAI
import os
from datetime import datetime

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

today = datetime.now().strftime("%Y/%m/%d")

prompt = """
你是一位有經驗的中文 Podcast 播報員，語氣像親切的中年大叔。
請用口語化方式，播報以下主題的內容，總長度約 12 分鐘：

- 今天凌晨美股四大指數（道瓊、那斯達克、標普500、費城半導體）收盤與分析
- QQQ、SPY ETF 走勢與分析，包含比特幣與黃金報價
- 資金流向與熱門產業類股
- 今日 Top 5 熱門股解析
- 一則最新 AI 技術或新聞解讀
- 每日投資金句，作為結尾

今天日期為 {today}
請以親切、口語風格完成播報稿。
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "你是一位資深 Podcast 播報員"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.8
)

script_text = response.choices[0].message.content

# 存稿
with open("script.txt", "w", encoding="u
