import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'stories.db'

# 確保必要的目錄存在
DATA_DIR.mkdir(exist_ok=True)

# 故事生成提示詞模板
STORY_PROMPT_TEMPLATE = """
請創作一個符合以下要求的故事：
- 主題：{theme}
- 類型：{genre}
- 語氣：{tone}
- 需要包含的元素：{elements}

請確保故事有完整的結構和吸引人的情節。
"""

# System prompt
SYSTEM_PROMPT = "你是一個專業的故事創作者，善於創作有趣的故事。"

# 資料庫初始化SQL
# 使用者偏好
USER_PREFERENCES_TABLE = """
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme TEXT NOT NULL,
    genre TEXT NOT NULL,
    tone TEXT NOT NULL,
    elements TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 故事
STORY_TABLE = """
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme TEXT NOT NULL,
    genre TEXT NOT NULL,
    tone TEXT NOT NULL,
    elements TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""" 
'''


'''