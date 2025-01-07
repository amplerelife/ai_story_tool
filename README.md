# ai_story_tool
資料檢索期末專題 AI創作平台

# AI驅動的個性化故事生成器

使用者輸入或選定一些關於故事的特色
我們用某種方法優化使用者給的提示詞，讓提示詞變得更好更精確
Ai根據提示生成第一階段的故事
接著使用一些分數指標評估故事分數
讓分數配合使用者給的喜歡或不喜歡（也可以文字回饋），給出新的提示
Ai根據新的提示重新寫好故事
以上的對話內容要存在資料庫裡

## 功能特點

- 通過命令行界面輸入故事偏好
- 支持多種主題和類型的故事生成
- 自動優化提示詞以提升生成質量
- 本地存儲生成的故事內容
- 支持查看歷史生成的故事

## 安裝說明

1. 克隆項目並進入項目目錄
2. 創建並激活虛擬環境（推薦）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
4. 配置環境變量：
   創建 `.env` 文件並添加：
   ```
   OPENAI_API_KEY=你的OpenAI API密钥
   ```

## 使用方法

1. 生成新故事：
   ```bash
   python src/main.py create-story
   ```

2. 查看已生成的故事：
   ```bash
   python src/main.py view-story [故事ID]
   ```

## 注意事項 

- 使用前請確保已配置正確的OpenAI API密钥
- 生成的故事會保存在本地資料庫中
- 建議在虛擬環境中運行項目 