import sqlite3
import json  
import os
from config import (
    DB_PATH
)
# 在DB中加入二筆資料，如果沒有db，會創建db
def add_story(version: int, theme: str, genre: str, tone: str, elements: list, prompt: str, content: str, feedback: str, rating: int):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # 將列表轉換為JSON字串
            elements_str = json.dumps(elements)  
            cursor.execute("INSERT INTO story_records (version, theme, genre, tone, elements, prompt, content, feedback, rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (version, theme, genre, tone, elements_str, prompt, content, feedback, rating))
            conn.commit()
            
            # 檢查插入的資料
            cursor.execute("SELECT * FROM story_records WHERE version = ?", (version,))
            inserted_data = cursor.fetchone()
            print("插入的資料:", inserted_data)
            
    except sqlite3.Error as e:
        print(f"資料庫錯誤: {e}")
    except Exception as e:
        print(f"其他錯誤: {e}")

if __name__ == "__main__":
    add_story(1, "AI", "Short Story", "Optimistic", ["AI", "Human"], "Once upon a time, there was an AI who wanted to be human.", "Once upon a time, there was an AI who wanted to be human.", "Good", 5)
    add_story(2,"robot","Short Story","Optimistic",["robot","human"],"Once upon a time, there was a robot who wanted to be human.","Once upon a time, there was a robot who wanted to be human.","Good",5)

'''
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
'''