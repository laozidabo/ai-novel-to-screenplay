"""
AI小说转剧本工具 - 主界面
"""

import gradio as gr
from chapter_parser import split_chapters, get_chapter_count
from schema import validate_screenplay, get_schema_summary
from converter import analyze_chapter, generate_story_bible, generate_screenplay, to_yaml

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;600;700&display=swap');
.gradio-container { font-family: 'Noto Serif SC', serif !important; }
"""

def build_schema_info_html(is_valid=None, errors=None):
    if is_valid is None: return ""
    elif is_valid: return '<div style="text-align:center;font-size:0.7rem;color:#4a7c5c;">✓ 校验通过</div>'
    else:
        e = errors[0] if errors else "未知错误"
        return f'<div style="text-align:center;font-size:0.7rem;color:#b84d4d;">✗ {e}</div>'

def _convert_core(text):
    if not text or not text.strip():
        yield "请输入小说文本", build_schema_info_html(), ""
        return
    detected_count = get_chapter_count(text)
    chapters = split_chapters(text)
    chapter_count = len(chapters)
    if detected_count < 1:
        yield "❌ 未检测到章节\n\n请确保文本包含章节标记（如「第一章」）", build_schema_info_html(), "❌ 失败"
        return
    if chapter_count > 5:
        chapters = chapters[:5]
        chapter_count = 5
    import os
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        yield "❌ API密钥未配置\n\n编辑 .env 文件，填入 DEEPSEEK_API_KEY", build_schema_info_html(is_valid=False, errors=["API未配置"]), "❌"
        return
    try:
        analyses = []
        for i, ch in enumerate(chapters):
            yield f"⏳ 分析第 {i+1}/{chapter_count} 章...\n\n> {ch['title']}", build_schema_info_html(), f"⏳ 分析第{i+1}章"
            result, error = analyze_chapter(ch["content"])
            if error:
                yield f"❌ 分析失败: {error}", build_schema_info_html(is_valid=False, errors=[error]), "❌"
                return
            analyses.append(result)
    except Exception as e:
        yield f"❌ {str(e)}", build_schema_info_html(is_valid=False, errors=[str(e)]), "❌"
        return
    try:
        yield "⏳ 合并角色和场景...", build_schema_info_html(), "⏳ 合并中"
        story_bible, error = generate_story_bible(analyses)
        if error:
            yield f"❌ {error}", build_schema_info_html(is_valid=False, errors=[error]), "❌"
            return
    except Exception as e:
        yield f"❌ {str(e)}", build_schema_info_html(is_valid=False, errors=[str(e)]), "❌"
        return
    try:
        yield "⏳ 生成剧本...", build_schema_info_html(), "⏳ 生成中"
        screenplay, error = generate_screenplay(story_bible, analyses, chapter_count)
        if screenplay is None:
            yield f"❌ {error}", build_schema_info_html(is_valid=False, errors=[error]), "❌"
            return
    except Exception as e:
        yield f"❌ {str(e)}", build_schema_info_html(is_valid=False, errors=[str(e)]), "❌"
        return
    yaml_output = to_yaml(screenplay)
    is_valid, errors = validate_screenplay(screenplay)
    title = screenplay.get("title", "未知")
    characters = screenplay.get("characters", [])
    acts = screenplay.get("acts", [])
    total_scenes = sum(len(act.get("scenes", [])) for act in acts)
    output = f"# {title}\n\n> {len(characters)} 角色 · {len(acts)} 幕 · {total_scenes} 场景\n\n{yaml_output}"
    if error: output += f"\n\n⚠️ {error}"
    yield output, build_schema_info_html(is_valid=is_valid, errors=errors), f"✅ {title}"

def convert_novel(text):
    for result in _convert_core(text): final = result
    return final[0], final[1]

def load_example():
    import os
    try:
        with open(os.path.join(os.path.dirname(__file__), "examples", "sample_novel.txt"), "r", encoding="utf-8") as f:
            return f.read()
    except: return "示例未找到"

with gr.Blocks(title="剧本工坊") as demo:
    gr.Markdown("# 剧本工坊\n*AI 小说转剧本工具 · 将文字化为舞台*")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📝 原文")
            input_text = gr.Textbox(placeholder="在此粘贴小说文本...\n\n每章以「第X章」开头", lines=22, show_label=False)
        with gr.Column():
            gr.Markdown("### 📜 剧本")
            output_text = gr.Textbox(placeholder="YAML剧本将在此显示", lines=22, show_label=False, interactive=False)

    with gr.Row():
        example_btn = gr.Button("📖 加载示例")
        convert_btn = gr.Button("🔄 转 换", variant="primary")
        copy_btn = gr.Button("📋 复制")

    status_bar = gr.Markdown("*就绪 · 等待输入*")

    convert_btn.click(fn=convert_novel, inputs=input_text, outputs=[output_text])
    example_btn.click(fn=load_example, outputs=input_text)
    copy_btn.click(fn=None, inputs=output_text, outputs=None, js="(text) => {navigator.clipboard.writeText(text); return '已复制！'}")

if __name__ == "__main__":
    demo.launch(css=CUSTOM_CSS)
