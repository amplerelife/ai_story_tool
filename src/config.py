import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'stories.db'

# 确保必要的目录存在
DATA_DIR.mkdir(exist_ok=True)

# 提示词模板
STORY_PROMPT_TEMPLATE = """
请根据以下要求创作一个引人入胜的故事：

基本要求：
- 主题：{theme}
- 类型：{genre}
- 语气：{tone}
- 关键元素：{elements}

创作指南：
1. 故事应当完全符合指定的主题和语气
2. 根据类型调整内容的形式和长度
3. 确保包含所有指定的关键元素
4. 故事要有清晰的开端、发展和结尾
5. 保持情节的连贯性和创意性
6. 使用生动的描写和对话

请直接开始创作故事，无需额外的解释或说明。
"""

# 数据库初始化SQL
INIT_DB_SQL = """
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