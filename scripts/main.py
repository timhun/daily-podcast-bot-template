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
一句話測試即可。
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
    import datetime
    import logging
    import os
    import requests

    logger = logging.getLogger(__name__)

    try:
        # 分段處理腳本以避免字符限制
        def split_text(text, max_length=1000):
            segments = []
            current_segment = ""
            for sentence in text.split("。"):
                if len(current_segment) + len(sentence) + 1 <= max_length:
                    current_segment += sentence + "。"
                else:
                    segments.append(current_segment)
                    current_segment = sentence + "。"
            if current_segment:
                segments.append(current_segment)
            return segments

        # 分割腳本
        segments = split_text(script, max_length=1000)
        audio_files = []

        # 設置語音參數
        voice_id = "D9bZgM9Er0PhIxuW9Jqa"
        voice_settings = {
            "stability": 0.4,
            "similarity_boost": 0.75,
            "speed": 1.2
        }

        # 生成每段音頻
        for i, segment in enumerate(segments):
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
                "Content-Type": "application/json"
            }
            data = {
                "text": segment,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": voice_settings
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                temp_file = f"audio/temp_segment_{i+1}.mp3"
                with open(temp_file, "wb") as f:
                    f.write(response.content)
                audio_files.append(temp_file)
            else:
                logger.error(f"HTTP API 請求失敗 (段 {i+1}): {response.status_code} - {response.text}")
                raise Exception(f"HTTP API 請求失敗: {response.text}")

        # 合併音頻（無需 pydub）
        today = datetime.date.today().strftime("%Y%m%d")
        output_path = f"audio/daily_podcast_{today}.mp3"
        with open(output_path, "wb") as outfile:
            for audio_file in audio_files:
                with open(audio_file, "rb") as infile:
                    outfile.write(infile.read())

        # 清理臨時檔案
        for audio_file in audio_files:
            os.remove(audio_file)

        return output_path
    except Exception as e:
        logger.error(f"語音轉換失敗: {e}")
        raise

def update_rss():
    today = datetime.date.today().strftime("%Y%m%d")
    rss_url = f"https://timhun.github.io/daily-podcast-bot-template/audio/daily_podcast_{today}.mp3"
    pub_date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")
    try:
        tree = ET.parse("feed.xml")
        channel = tree.getroot().find("channel")
    except FileNotFoundError:
        rss = ET.Element("rss", version="2.0", attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"})
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "大叔說財經科技與投資"
        ET.SubElement(channel, "description").text = "每日美股及科技財經播報，涵蓋指數、ETF、比特幣、黃金及AI新聞。"
        ET.SubElement(channel, "link").text = "https://timhun.github.io/daily-podcast-bot-template/"
        ET.SubElement(channel, "language").text = "zh-tw"
        ET.SubElement(channel, "itunes:author").text = "大叔"
        ET.SubElement(channel, "itunes:category", attrib={"text": "Business"})
        ET.SubElement(channel, "itunes:image", attrib={"href": "https://timhun.github.io/daily-podcast-bot-template/cover.jpg"})
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
