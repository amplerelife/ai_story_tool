# ai_story_tool
資料檢索期末專題 AI創作平台

## ⚠️ 重要版本說明
此專案依賴以下特定版本的套件，請勿更改版本以確保功能正常：
```
openai==1.55.3
httpx==0.27.2
```

## 專案簡介
這是一個基於 GPT-4o-mini 模型的智慧故事生成工具。使用者可以通過輸入故事偏好和特徵，讓 AI 生成個性化的故事內容。系統會通過思考鏈分析和評估機制，持續優化故事品質。

## 核心功能

- 🎯 智慧故事生成
  - 支援多種主題和類型
  - 自動優化提示詞
  - 思考鏈分析確保故事品質
  
- 📝 故事評估與優化
  - 自動評估故事品質
  - 根據使用者反饋優化
  - 支援多版本迭代生成

- 💾 本地資料管理
  - SQLite 資料庫存儲
  - 支援查看歷史記錄
  - 完整的故事版本追蹤

## 安裝說明

1. 克隆專案：
   ```bash
   git clone [專案網址]
   cd ai_story_tool
   ```

2. 建立虛擬環境（強烈建議）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. 安裝依賴（請確保版本正確）：
   ```bash
   pip install -r requirements.txt
   ```

4. 環境設定：
   - 建立 `.env` 檔案
   - 加入 OpenAI API 金鑰：
     ```
     OPENAI_API_KEY=你的OpenAI API金鑰
     ```

## 使用方法

1. 生成新故事：
   ```bash
   python src/main.py create-story
   ```
   依照提示輸入：
   - 故事主題（如：AI/科幻/奇幻/愛情）
   - 類型（如：短文/對話/小說）
   - 語氣（如：樂觀/陰沉/幽默）
   - 關鍵元素（用逗號分隔）

## 技術細節

- 使用 GPT-4o-mini 模型生成故事
- 實作思考鏈（Chain of Thought）分析
- SQLite 本地資料庫儲存
- Click 命令行介面
- Jieba 中文分詞支援

## 注意事項 

- 請確保 OpenAI API 金鑰設定正確
- 建議在虛擬環境中運行
- 首次運行時會自動初始化資料庫
- 所有生成的故事都會保存在本地資料庫中

## 授權說明

本專案僅供學術研究使用。 