import sqlite3
import jieba
from nltk.translate.bleu_score import sentence_bleu
from rouge_chinese import Rouge
from config import DB_PATH

class StoryEvaluator:
    def __init__(self):
        """初始化評估器"""
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.rouge = Rouge()
        
    def __del__(self):
        """關閉資料庫連接"""
        self.conn.close()
        
    def get_story_versions(self):
        """獲取所有故事版本"""
        self.cursor.execute("SELECT version FROM story_records ORDER BY version")
        return [row[0] for row in self.cursor.fetchall()]
        
    def get_story_content(self, version):
        """獲取指定版本的故事內容"""
        self.cursor.execute(
            "SELECT content FROM story_records WHERE version = ?",
            (version,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None
        
    def get_story_feedback(self, version):
        """獲取指定版本的反饋"""
        self.cursor.execute(
            "SELECT feedback, rating FROM story_records WHERE version = ?",
            (version,)
        )
        return self.cursor.fetchone()
        
    def tokenize_chinese(self, text):
        """將中文文本分詞"""
        return list(jieba.cut(text))
        
    def calculate_bleu_score(self, reference, candidate):
        """計算BLEU分數"""
        reference_tokens = [self.tokenize_chinese(reference)]
        candidate_tokens = self.tokenize_chinese(candidate)
        return sentence_bleu(reference_tokens, candidate_tokens)
        
    def calculate_rouge_scores(self, reference, candidate):
        """計算ROUGE分數"""
        try:
            # 計算ROUGE分數
            scores = self.rouge.get_scores(candidate, reference)
            
            # 提取各項ROUGE分數
            rouge_l = scores[0]["rouge-l"]
            rouge_1 = scores[0]["rouge-1"]
            rouge_2 = scores[0]["rouge-2"]
            
            return {
                "rouge_l_f": rouge_l["f"],  # F1分數
                "rouge_1_f": rouge_1["f"],  # ROUGE-1 F1分數
                "rouge_2_f": rouge_2["f"]   # ROUGE-2 F1分數
            }
        except Exception as e:
            print(f"計算ROUGE分數時發生錯誤: {str(e)}")
            return {
                "rouge_l_f": 0.0,
                "rouge_1_f": 0.0,
                "rouge_2_f": 0.0
            }
        
    def calculate_change_rate(self, old_content, new_content):
        """計算內容變化率"""
        old_tokens = set(self.tokenize_chinese(old_content))
        new_tokens = set(self.tokenize_chinese(new_content))
        
        # 計算變化的字詞比例
        changed_tokens = len(old_tokens.symmetric_difference(new_tokens))
        total_tokens = len(old_tokens.union(new_tokens))
        
        return changed_tokens / total_tokens if total_tokens > 0 else 0
        
    def evaluate_story_changes(self, old_content, new_content, preferences=None):
        """評估故事的變化"""
        # 基本評估指標
        bleu_score = self.calculate_bleu_score(old_content, new_content)
        change_rate = self.calculate_change_rate(old_content, new_content)
        
        # 計算ROUGE分數
        rouge_scores = self.calculate_rouge_scores(old_content, new_content)
        
        return {
            "bleu_score": bleu_score,
            "change_rate": change_rate,
            "rouge_scores": rouge_scores
        }
        
    def analyze_version_history(self):
        """分析故事版本歷史"""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                
                # 獲取所有版本
                versions = cursor.execute(
                    "SELECT version, content FROM story_records ORDER BY version"
                ).fetchall()
                
                if not versions:
                    return None
                    
                version_count = len(versions)
                
                # 分析內容長度變化
                content_length_trend = []
                for version, content in versions:
                    content_length_trend.append({
                        'version': version,
                        'length': len(content)
                    })
                
                # 分析版本間的變化
                version_changes = []
                for i in range(len(versions)-1):
                    v1_content = versions[i][1]
                    v2_content = versions[i+1][1]
                    
                    # 計算BLEU分數和變化率
                    bleu_score = self.calculate_bleu_score(v1_content, v2_content)
                    change_rate = self.calculate_change_rate(v1_content, v2_content)
                    
                    # 計算ROUGE分數
                    rouge_scores = self.calculate_rouge_scores(v1_content, v2_content)
                    
                    version_changes.append({
                        'from_version': versions[i][0],
                        'to_version': versions[i+1][0],
                        'bleu_score': bleu_score,
                        'change_rate': change_rate,
                        'rouge_scores': rouge_scores
                    })
                
                # 獲取反饋記錄
                feedback_analysis = []
                for version, _ in versions:
                    feedback = cursor.execute(
                        "SELECT version, feedback FROM story_records WHERE version = ? AND feedback IS NOT NULL",
                        (version,)
                    ).fetchone()
                    if feedback:
                        feedback_analysis.append({
                            'version': feedback[0],
                            'feedback': feedback[1]
                        })
                
                return {
                    'version_count': version_count,
                    'content_length_trend': content_length_trend,
                    'version_changes': version_changes,
                    'feedback_analysis': feedback_analysis
                }
                
        except sqlite3.Error as e:
            print(f"分析版本歷史時發生錯誤: {str(e)}")
            return None 