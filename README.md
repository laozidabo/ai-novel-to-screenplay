# AI小说转剧本工具

将小说文本自动转换为结构化剧本（YAML格式），帮助作者快速获得可编辑的剧本初稿。

## 功能

- 自动识别小说章节
- AI分析角色、场景、情节
- 输出结构化YAML剧本
- 支持多种剧本格式（电影/电视剧/短视频）

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/laozidabo/ai-novel-to-screenplay.git
cd ai-novel-to-screenplay

# 2. 一键初始化环境
bash setup.sh

# 3. 配置API密钥
# 编辑 .env 文件，填入你的 DeepSeek API Key

# 4. 启动应用
source venv/bin/activate
python app.py
```

## 技术栈

- Python 3.14
- Gradio（Web界面）
- DeepSeek API（AI转换）
- PyYAML + jsonschema（YAML生成与校验）

## 许可证

MIT
