import click
import os
from dotenv import load_dotenv
from openai import OpenAI
from config import STORY_PROMPT_TEMPLATE

# 加载环境变量
load_dotenv()

# 初始化OpenAI客户端
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@click.group()
def cli():
    """AI驱动的个性化故事生成器"""
    pass

def generate_story(theme, genre, tone, elements):
    """使用OpenAI API生成故事"""
    prompt = STORY_PROMPT_TEMPLATE.format(
        theme=theme,
        genre=genre,
        tone=tone,
        elements=elements
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的故事创作者，善于根据用户的需求创作有趣的故事。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        click.echo(f"生成故事时发生错误: {str(e)}", err=True)
        return None

@cli.command()
@click.option('--theme', prompt='请选择主题', 
              type=click.Choice(['AI', '气候变化', '科幻', '奇幻', '爱情']), 
              help='故事主题')
@click.option('--genre', prompt='请选择类型',
              type=click.Choice(['短篇故事', '对话', '博客文章']),
              help='内容类型')
@click.option('--tone', prompt='请选择语气',
              type=click.Choice(['乐观', '黑暗', '幽默', '正式']),
              help='内容语气')
@click.option('--elements', prompt='关键元素（用逗号分隔）', help='故事中的关键元素')
def create_story(theme, genre, tone, elements):
    """创建新的故事"""
    click.echo(f'正在生成{theme}主题的{genre}...')
    
    story = generate_story(theme, genre, tone, elements)
    if story:
        click.echo("\n生成的故事：\n")
        click.echo(story)
    else:
        click.echo("故事生成失败，请检查API密钥是否正确设置。")

@cli.command()
@click.argument('story_id')
def view_story(story_id):
    """查看已生成的故事"""
    click.echo(f'正在查看故事 {story_id}')
    # TODO: 实现故事查看逻辑

if __name__ == '__main__':
    cli() 