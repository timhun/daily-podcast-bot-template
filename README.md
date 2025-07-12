# 每大叔說財經科技與投資

這是一個全自動化 Podcast 生成模板，每天早上 6:00（台灣時間）生成 12 分鐘的財經 Podcast，涵蓋美股指數、ETF、比特幣、黃金及 AI 新聞。

## 設置步驟

1. **創建儲存庫**：
   - 將本專案上傳至 GitHub，儲存庫命名為 `daily-podcast-bot-template`。
   - 啟用 GitHub Pages（`Settings > Pages > Source > main branch`）。

2. **設置 API Key**：
   - 獲取 [xAI API Key](https://x.ai/api) 和 [ElevenLabs API Key](https://elevenlabs.io)。
   - 在 GitHub 儲存庫的 `Settings > Secrets and variables > Actions` 添加：
     - `XAI_API_KEY`
     - `ELEVENLABS_API_KEY`（已提供：sk_1e975e64a8ae6caf9aa12f7d44f511b3b97514de733d8619）

3. **上傳封面**：
   - 替換 `cover.jpg`（1400x1400 至 3000x3000 像素，建議 3000x3000，<500KB，無版權問題）。

4. **更新 RSS URL**：
   - 編輯 `scripts/main.py`，將 `rss_url` 中的 `your-username` 替換為你的 GitHub 用戶名。

5. **提交 RSS feed**：
   - 提交 `https://your-username.github.io/daily-podcast-bot-template/feed.xml` 至：
     - [Apple Podcasts Connect](https://podcastsconnect.apple.com)
     - [Spotify for Podcasters](https://podcasters.spotify.com)
   - 使用 [Cast Feed Validator](https://castfeedvalidator.com/) 驗證 feed。

6. **測試**：
   - 在 GitHub Actions 手動運行工作流程，檢查 `audio/` 和 `feed.xml` 是否更新。

## 要求

- Python 3.10+
- GitHub Pages 啟用
- 每日音頻約 12MB（128kbps，12 分鐘）

## 注意事項

- 確保音頻檔案 <100MB（GitHub Pages 限制）。
- 監控 GitHub Pages 每月 100GB 流量限制。
- ElevenLabs 免費方案約 10,000 字/月，足以生成 1,800 字腳本。
