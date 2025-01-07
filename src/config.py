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
