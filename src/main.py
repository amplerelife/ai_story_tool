import os
import click
import sqlite3
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from config import (
    STORY_PROMPT_TEMPLATE, 
    REGENERATE_PROMPT_TEMPLATE, 
    SYSTEM_PROMPT, 
    INIT_DB,
    BASE_DIR,
    DATA_DIR,
    DB_PATH
)
import json

# 加載環境變量和初始化客戶端
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def init_db():
    """初始化資料庫"""
    # 確保data目錄存在
    DATA_DIR.mkdir(exist_ok=True)
    # 連接資料庫並創建、初始化資料庫
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(INIT_DB)


def save_story(version: int, theme: str, genre: str, tone: str, elements: list, 
               prompt: str, content: str, feedback: str = None, rating: int = None):
    #第一次生成(version=1)時feedback與rating為None
    """
    保存故事記錄
    
    Raises:
        ValueError: 當輸入參數驗證失敗時
        sqlite3.Error: 當資料庫操作失敗時
    """
    # 1. 輸入驗證
    if not all([version, theme, genre, tone, elements, prompt, content]):
        raise ValueError("必填欄位不能為空")
    
    if rating is not None and not (1 <= rating <= 5):
        raise ValueError("評分必須在1-5之間")
    
    if not isinstance(elements, list):
        raise ValueError("elements必須是列表類型")
    
    # 2. 資料預處理
    try:
        elements_json = json.dumps(elements, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"elements轉換JSON失敗: {str(e)}")
    
    # 3. 資料庫操作
    try:
        # 連接資料庫
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                # 檢查版本是否已存在
                existing = cursor.execute(
                    "SELECT version FROM story_records WHERE version = ?",
                    (version,)
                ).fetchone()
                if existing:
                    # 如果存在，則更新
                    cursor.execute("""
                        UPDATE story_records 
                        SET theme = ?, genre = ?, tone = ?, elements = ?,
                            prompt = ?, content = ?, feedback = ?, rating = ?
                        WHERE version = ?
                    """, (theme, genre, tone, elements_json, prompt, content, 
                          feedback, rating, version))
                    print(f"覆寫版本 {version} 的故事記錄")
                else:
                    # 如果不存在，則插入
                    cursor.execute("""
                        INSERT INTO story_records 
                        (version, theme, genre, tone, elements, prompt, 
                         content, feedback, rating)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (version, theme, genre, tone, elements_json, prompt,
                          content, feedback, rating))
                    print(f"新增版本 {version} 的故事記錄")
                conn.commit()
                
            except sqlite3.Error as e:
                # 如果出錯，撤銷更改
                conn.rollback()
                raise sqlite3.Error(f"資料庫操作失敗: {str(e)}")     
    except sqlite3.Error as e:
        raise sqlite3.Error(f"資料庫連接失敗: {str(e)}")

def get_story(version: int) -> dict:
    """獲取指定版本的紀錄"""
    #TODO: 獲取指定版本的故事
    pass

def generate_story_prompt(preferences: dict) -> str:
    """生成初始提示詞"""
    return STORY_PROMPT_TEMPLATE.format(
        theme=preferences['theme'],
        genre=preferences['genre'],
        tone=preferences['tone'],
        elements=', '.join(preferences['key_elements'])
    )

def generate_regenerate_prompt(preferences: dict, original_story: str, feedback: str) -> str:
    """生成重新生成的提示詞"""
    return REGENERATE_PROMPT_TEMPLATE.format(
        original_story=original_story,
        feedback=feedback,
        theme=preferences['theme'],
        genre=preferences['genre'],
        tone=preferences['tone'],
        elements=', '.join(preferences['key_elements'])
    )

def call_openai_api(prompt: str) -> str:
    """調用OpenAI API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"調用OpenAI API失敗: {str(e)}")

@click.group()
def cli():
    """AI故事生成工具"""
    # 每次啟動時初始化資料庫
    init_db()

@cli.command()
def create_story():
    """創建新故事"""
    # 獲取用戶輸入
    theme = click.prompt("主題 (如：AI/科幻/奇幻/愛情)", type=str)
    genre = click.prompt("類型 (如：短文/對話/小說)", type=str)
    tone = click.prompt("語氣 (如：樂觀/黑暗/幽默)", type=str)
    key_elements = click.prompt("關鍵元素 (用逗號分隔)", type=str).split(',')
    
    preferences = {
        "theme": theme,
        "genre": genre,
        "tone": tone,
        "key_elements": key_elements
    }
    
    try:
        # 生成初始故事
        version = 1
        prompt = generate_story_prompt(preferences)
        content = call_openai_api(prompt)
        
        # 保存第一個版本
        save_story(
            version=version,
            theme=theme,
            genre=genre,
            tone=tone,
            elements=key_elements,
            prompt=prompt,
            content=content
        )
        
        # 顯示故事
        click.echo(f"\n第 {version} 版故事：\n")
        click.echo(content)
        
        # 循環獲取反饋並重新生成
        while click.confirm("\n您想要提供反饋嗎？"):
            feedback = click.prompt("請輸入您的反饋意見", type=str)
            rating = click.prompt("請給這個版本評分 (1-5)", type=int, default=3)
            
            # 生成新版本
            version += 1
            prompt = generate_regenerate_prompt(preferences, content, feedback)
            content = call_openai_api(prompt)
            
            # 保存新版本資訊
            save_story(
                version=version,
                theme=theme,
                genre=genre,
                tone=tone,
                elements=key_elements,
                prompt=prompt,
                content=content,
                feedback=feedback,
                rating=rating
            )
            
            # 顯示新版本
            click.echo(f"\n第 {version} 版故事：\n")
            click.echo(content)
            
            if click.confirm("您滿意這個版本嗎？", default=True):
                break
        
        click.echo("\n感謝使用！")
        
    except Exception as e:
        click.echo(f"發生錯誤: {str(e)}", err=True)

if __name__ == '__main__':
    cli() 
    