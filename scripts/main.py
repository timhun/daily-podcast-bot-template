import yfinance as yf
from elevenlabs import ElevenLabs
import requests
import datetime
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import os
import time
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def fetch_market_data():
    indices = {
        "DJIA": "^DJI",
        "NASDAQ": "^IXIC",
        "S&P 500": "^GSPC",
        "PHLX Semiconductor": "^SOX",
        "QQQ": "QQQ",
        "SPY": "SPY",
        "BTC": "BITO",
        "Gold": "GLD"
    }
    data = {}
    for attempt in range(3):
        try:
            for name, ticker in indices.items():
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                data[name] = {
                    "close": round(hist["Close"].iloc[-1], 2),
                    "change": round((hist["Close"].iloc[-1] - hist["Open"].iloc[-1]) / hist["Open"].iloc[-1] * 100, 2)
                }
            return data
        except Exception as e:
            logger.error(f"市場數據獲取第 {attempt + 1} 次失敗: {e}")
            time.sleep(2)
    logger.error("市場數據獲取失敗，已重試 3 次")
    return {}  # 後備：返回空數據

def generate_script(data):
    prompt = f"""
    為《每大叔說財經科技與投資》生成一個12分鐘的中文Podcast腳本，語氣為親切的中年大叔風格，語速為正常1.2倍，約1800字。包含以下內容：
    1. 美股四大指數（道瓊、那斯達克、標普500、費城半導體）收盤與分析，數據：{data}。
    2. QQQ、SPY ETF走勢，比特幣ETF：{data.get('BTC', '無數據')}，黃金ETF：{data.get('Gold', '無數據')}。
    3. 資金流向與熱門產業類股（模擬：科技和半導體吸金12億美元，消費品6億美元）。
    4. Top 5熱門股解析（模擬：輝達+3%、特斯拉+2.8%、蘋果+0.6%、微軟-0.2%、亞馬遜+2.2%）。
    5. 最新AI技術或美國總體經濟新聞（模擬：輝達發布Rubin平台，效能提升35%）。
    6. 每日投資金句：市場如人生，穩中求進才能走得遠。
    開場：早安，歡迎收聽《每大叔說財經科技與投資》！我是你們的老朋友，今天又是充滿機會的一天！準備好你的咖啡，咱們來看看昨晚美股的表現，還有那些值得關注的市場動態！
    結尾：感謝收聽，明天同一時間再見，祝你一天投資順心，早安！
    """
    for attempt in range(3):
        try:
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",  # 更新為新端點
                headers={"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "grok-4",  # 明確指定 Grok 4
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000
                }
            )
            # 檢查 HTTP 狀態碼
            if response.status_code != 200:
                logger.error(f"API 請求失敗，狀態碼 {response.status_code}: {response.text}")
                time.sleep(2)
                continue
            # 解析 JSON 回應
            response_json = response.json()
            logger.info(f"API 回應: {response_json}")
            # 檢查是否存在 'choices'
            if "choices" not in response_json:
                logger.error(f"回應中無 'choices' 鍵: {response_json}")
                time.sleep(2)
                continue
            return response_json["choices"][0]["message"]["content"]  # 更新為 message.content
        except Exception as e:
            logger.error(f"API 請求第 {attempt + 1} 次失敗: {e}")
            time.sleep(2)
    # 後備腳本
    logger.error("生成腳本失敗，已重試 3 次，使用後備腳本")
    return """
    早安，歡迎收聽《每大叔說財經科技與投資》！我是你們的老朋友，今天又是充滿機會的一天！
    很抱歉，今天的市場數據無法即時更新，但讓我們來聊聊投資的長期思維。市場如人生，穩中求進才能走得遠。
    今天我們談談科技趨勢，輝達近期發布了Rubin平台，效能提升35%，顯示AI產業的強勁動能。
    感謝收聽，明天同一時間再見，祝你一天投資順心，早安！
    """

def text_to_speech(script):
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.generate(
            text=script,
            voice="D9bZgM9Er0PhIxuW9Jqa",
            model="eleven_multilingual_v2",
            voice_settings={"stability": 0.4, "similarity_boost": 0.75, "speed": 1.2}
        )
        today = datetime.date.today().strftime("%Y%m%d")
        with open(f"audio/daily_podcast_{today}.mp3", "wb") as f:
            f.write(audio)
    except Exception as e:
        logger.error(f"語音轉換失敗: {e}")
        raise

def update_rss():
    today = datetime.date.today().strftime("%Y%m%d")
    rss_url = f"https://your-username.github.io/daily-podcast-bot-template/audio/daily_podcast_{today}.mp3"
    pub_date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")
    try:
        tree = ET.parse("feed.xml")
        channel = tree.getroot().find("channel")
    except FileNotFoundError:
        rss = ET.Element("rss", version="2.0", attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"})
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "每大叔說財經科技與投資"
        ET.SubElement(channel, "description").text = "每日美股及科技財經播報，涵蓋指數、ETF、比特幣、黃金及AI新聞。"
        ET.SubElement(channel, "link").text = "https://your-username.github.io/daily-podcast-bot-template/"
        ET.SubElement(channel, "language").text = "zh-tw"
        ET.SubElement(channel, "itunes:author").text = "每大叔"
        ET.SubElement(channel, "itunes:category", attrib={"text": "Business"})
        ET.SubElement(channel, "itunes:image", attrib={"href": "https://your-username.github.io/daily-podcast-bot-template/cover.jpg"})
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = f"美股播報 {today}"
    ET.SubElement(item, "description").text = "每日美股及科技財經播報，涵蓋指數、ETF、比特幣、黃金及AI新聞。"
    ET.SubElement(item, "pubDate").text = pub_date
    ET.SubElement(item, "enclosure", attrib={"url": rss_url, "length": "12000000", "type": "audio/mpeg"})
    ET.SubElement(item, "guid").text = rss_url
    tree = ET.ElementTree(ET.Element("rss", version="2.0", attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}))
    tree.getroot().append(channel)
    tree.write("feed.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    data = fetch_market_data()
    script = generate_script(data)
    text_to_speech(script)
    update_rss()