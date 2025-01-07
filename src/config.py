import os
from pathlib import Path
import sqlite3

# 基礎配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'stories.db'

# 打印路径
print(f"專案根目錄 (BASE_DIR): {str(BASE_DIR)}")
print(f"資料目錄 (DATA_DIR): {str(DATA_DIR)}")
print(f"資料庫路徑 (DB_PATH): {str(DB_PATH)}")

# 故事生成提示詞模板
STORY_PROMPT_TEMPLATE = """
請創作一個符合以下要求的故事：
- 主題：{theme}
- 類型：{genre}
- 語氣：{tone}
- 需要包含的元素：{elements}

請確保故事有完整的結構和吸引人的情節。
"""

# 根據反饋重新生成的提示詞模板
REGENERATE_PROMPT_TEMPLATE = """
請根據以下反饋修改故事：

原始故事：
{original_story}

用戶反饋：
{feedback}

請保持以下原始要求：
- 主題：{theme}
- 類型：{genre}
- 語氣：{tone}
- 需要包含的元素：{elements}

請根據用戶反饋調整故事內容，創作一個新的版本。
"""

# System prompt
SYSTEM_PROMPT = "你是一個專業的故事創作者，善於根據用戶反饋改進故事。"

# 資料庫初始化SQL
INIT_DB = """
DROP TABLE IF EXISTS story_records;

CREATE TABLE story_records (
    version INTEGER PRIMARY KEY,        -- 版本號作為主鍵
    theme TEXT NOT NULL,               -- 主題
    genre TEXT NOT NULL,               -- 類型
    tone TEXT NOT NULL,                -- 語氣
    elements TEXT NOT NULL,            -- 關鍵元素 (JSON字符串)
    prompt TEXT NOT NULL,              -- 使用的提示詞
    content TEXT NOT NULL,             -- 生成的內容
    feedback TEXT,                     -- 用戶反饋
    rating INTEGER,                    -- 用戶評分 (1-5)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
