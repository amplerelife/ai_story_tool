import os
import click
import sqlite3
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from config import (
    INIT_DB,
    BASE_DIR,
    DATA_DIR,
    DB_PATH
    
)
from prompt_engineering import (
    generate_story_prompt,
    generate_regenerate_prompt,
    chain_of_thought,
    SYSTEM_PROMPT
)
import json
import jieba
from evaluation import StoryEvaluator

# 設置jieba的日誌級別為WARNING以上，避免顯示載入訊息
jieba.setLogLevel(logging.WARNING)

# 預先載入jieba
jieba.initialize()

#程式碼全部都是繁體
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
                else:
                    # 如果不存在，則插入
                    cursor.execute("""
                        INSERT INTO story_records 
                        (version, theme, genre, tone, elements, prompt, 
                         content, feedback, rating)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (version, theme, genre, tone, elements_json, prompt,
                          content, feedback, rating))
                conn.commit()
                
            except sqlite3.Error as e:
                # 如果出錯，撤銷更改
                conn.rollback()
                raise sqlite3.Error(f"資料庫操作失敗: {str(e)}")     
    except sqlite3.Error as e:
        raise sqlite3.Error(f"資料庫連接失敗: {str(e)}")

def analyze_with_chain_of_thought(preferences: dict) -> str:
    """
    使用思考鏈分析故事元素並生成精簡的背景分析
    """
    # 獲取所有思考提示詞
    thought_prompts = chain_of_thought(preferences)
    analysis_results = []
    
    # 為每個思考方向添加引導
    summary_request = """

    請以自由的方式總結你的想法：
    - 提供2-3個最具啟發性的見解
    - 說明這些見解如何幫助故事創作
    - 用生動的語言表達你的思考
    """
    
    # 對每個思考方向進行分析
    for prompt in thought_prompts:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt + summary_request}
                ],
                temperature=0.7,
                max_tokens=300
            )
            analysis_results.append(response.choices[0].message.content)
        except Exception as e:
            print(f"思考鏈分析時發生錯誤: {str(e)}")
            continue
    
    # 將所有分析整合為上下文
    context = "\n\n創作思路：\n" + "\n---\n".join(
        result.strip() for result in analysis_results
    )
    
    # 整合所有分析為創作指南
    try:
        final_summary = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "您是一位深諳文學創作的智者，請將這些思考整合為富有洞見的創作指南。"},
                {"role": "user", "content": f"""
                請將這些創作思路提煉為一份優雅簡潔的創作指南：

                {context}

                要求：
                - 提供富有啟發性的創作建議
                - 保持文學性與實用性的平衡
                - 讓每個建議都能啟發創作靈感
                - 注重表達的優美與準確
                """}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return final_summary.choices[0].message.content
    except Exception as e:
        print(f"最終總結生成失敗: {str(e)}")
        return context

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
            max_tokens=3000
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
    # 初始化評估器
    evaluator = StoryEvaluator()
    
    # 獲取用戶輸入
    theme = click.prompt("主題 (如：AI/科幻/奇幻/愛情)", type=str)
    genre = click.prompt("類型 (如：短文/對話/小說)", type=str)
    tone = click.prompt("語氣 (如：樂觀/陰沉/幽默)", type=str)
    key_elements = click.prompt("關鍵元素 (用逗號分隔)", type=str).split(',')
    
    preferences = {
        "theme": theme,
        "genre": genre,
        "tone": tone,
        "key_elements": key_elements
    }
    
    try:
        # 使用思考鏈進行深入分析
        analysis_context = analyze_with_chain_of_thought(preferences)
        
        # 生成初始故事
        version = 1
        # 將分析結果加入提示詞
        base_prompt = generate_story_prompt(preferences)
        prompt = f"""
{base_prompt}

故事構思參考：
{analysis_context}

請根據以上要求和構思建議，創作一個打動人心的故事。注意：
1. 以上構思僅供參考，您可以有自己的創意發揮
2. 請保持故事的連貫性和完整性
3. 確保符合之前提到的所有要求
"""
        print(f"\n生成故事的提示詞:\n{prompt}")
        content = call_openai_api(prompt)
        
        # 保存第一個版本，沒有feedback與rating
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
        print("========================")
        click.echo(f"\n第 {version} 版故事：\n")
        click.echo(content)
        
        # 循環獲取反饋並重新生成
        while click.confirm("\n您想要提供反饋嗎？"):
            feedback = click.prompt("請輸入您的反饋意見", type=str)
            rating = click.prompt("請給這個版本評分 (1-5)", type=int, default=3)
            
            # 生成新版本    
            version += 1
            preferences['rating'] = rating  # 添加評分到preferences
            base_prompt = generate_regenerate_prompt(preferences, content, feedback)
            prompt = base_prompt + analysis_context
            new_content = call_openai_api(prompt)
            
            # 評估故事變化
            evaluation_results = evaluator.evaluate_story_changes(content, new_content, preferences)
            
            # 顯示評估結果
            print("========================")
            # 更新當前內容
            content = new_content
            
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
            
            # 分析版本歷史
            history_analysis = evaluator.analyze_version_history()
            if history_analysis:
                print("========================")
                click.echo("\n版本歷史分析：")
                click.echo(f"總版本數: {history_analysis['version_count']}")
                
                if history_analysis['content_length_trend']:
                    click.echo("\n內容長度變化:")
                    for length_data in history_analysis['content_length_trend']:
                        click.echo(f"版本 {length_data['version']}: {length_data['length']} 字")
                
                if history_analysis.get('version_changes'):
                    click.echo("\n版本間變化:")
                    for change in history_analysis['version_changes']:
                        click.echo(
                            f"版本 {change['from_version']} -> {change['to_version']}:"
                            f"\nBLEU分數: {change['bleu_score']:.2f}"
                            f"\n變化率: {change['change_rate']:.2f}"
                            f"\nROUGE-L: {change['rouge_scores']['rouge_l_f']:.2f}"
                            f"\nROUGE-1: {change['rouge_scores']['rouge_1_f']:.2f}"
                            f"\nROUGE-2: {change['rouge_scores']['rouge_2_f']:.2f}"
                        )
                
                if history_analysis['feedback_analysis']:
                    click.echo("\n歷史反饋:")
                    for feedback_data in history_analysis['feedback_analysis']:
                        click.echo(f"版本 {feedback_data['version']}: {feedback_data['feedback']}")
            
            if click.confirm("您滿意這個版本嗎？", default=True):
                break
        
        click.echo("\n感謝使用！")
        
    except Exception as e:
        click.echo(f"發生錯誤: {str(e)}", err=True)

if __name__ == '__main__':
    cli() 
    