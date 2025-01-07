# ai_story_tool
資料檢索期末專題 AI創作平台

# AI驱动的个性化故事生成器

这是一个基于命令行的AI驱动故事生成系统，能够根据用户的偏好自动生成个性化的故事内容。

## 功能特点

- 通过命令行界面输入故事偏好
- 支持多种主题和类型的故事生成
- 自动优化提示词以提升生成质量
- 本地存储生成的故事内容
- 支持查看历史生成的故事

## 安装说明

1. 克隆项目并进入项目目录
2. 创建并激活虚拟环境（推荐）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 配置环境变量：
   创建 `.env` 文件并添加：
   ```
   OPENAI_API_KEY=你的OpenAI API密钥
   ```

## 使用方法

1. 生成新故事：
   ```bash
   python src/main.py create-story
   ```

2. 查看已生成的故事：
   ```bash
   python src/main.py view-story [故事ID]
   ```

## 注意事项

- 使用前请确保已配置正确的OpenAI API密钥
- 生成的故事会保存在本地数据库中
- 建议在虚拟环境中运行项目 