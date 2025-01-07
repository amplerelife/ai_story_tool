import os
import click
from datetime import datetime
from uuid import uuid4
from openai import OpenAI
from dotenv import load_dotenv
from config import STORY_PROMPT_TEMPLATE, SYSTEM_PROMPT

# 加载环境变量和初始化客户端
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_story_prompt(preferences: dict) -> str:
    """根据用户偏好生成提示词"""
    return STORY_PROMPT_TEMPLATE.format(
        theme=preferences['theme'],
        genre=preferences['genre'],
        tone=preferences['tone'],
        elements=', '.join(preferences['key_elements'])
    )

def call_openai_api(prompt: str) -> str:
    """调用OpenAI API生成故事"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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

def load_stories() -> dict:
    """加載已保存的故事"""
    #TODO: 從資料庫中加載已保存的故事
    pass

def save_story(story: dict):
    """保存故事到資料庫"""
    #TODO: 保存故事到資料庫
    pass

@click.group()
def cli():
    """AI故事生成工具"""
    pass

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
        # 生成故事
        prompt = generate_story_prompt(preferences)
        content = call_openai_api(prompt)
        
        # 創建故事數據
        story = {
            "id": str(uuid4()),
            "title": f"{theme}的{genre}",
            "content": content,
            "preferences": preferences,
            "created_at": datetime.now().isoformat(),
            "feedback_score": None
        }
        
        # 保存故事
        save_story(story)
        
        # 顯示結果
        click.echo("\n生成的故事：\n")
        click.echo(content)
        
    except Exception as e:
        click.echo(f"生成故事時發生錯誤: {str(e)}", err=True)

@cli.command()
@click.argument('story_id', required=False)
def view_story(story_id):
    """查看已生成的故事"""
    stories = load_stories()
    
    if story_id:
        if story_id in stories:
            story = stories[story_id]
            click.echo(f"\n標題：{story['title']}")
            click.echo(f"創建時間：{story['created_at']}")
            click.echo("\n內容：\n")
            click.echo(story['content'])
        else:
            click.echo(f"未找到ID為 {story_id} 的故事")
    else:
        if stories:
            click.echo("\n已生成的故事列表：\n")
            for id, story in stories.items():
                click.echo(f"ID: {id}")
                click.echo(f"標題: {story['title']}")
                click.echo(f"創建時間: {story['created_at']}")
                click.echo("---")
        else:
            click.echo("沒有生成任何故事")

if __name__ == '__main__':
    cli() 