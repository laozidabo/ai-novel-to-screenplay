"""
AI小说转剧本工具 - 主界面

Gradio Web界面，支持输入小说文本并展示转换结果。
"""

import gradio as gr


def convert_novel(text):
    """
    转换小说文本为剧本格式（占位函数，后续PR接入真实转换）
    """
    if not text or not text.strip():
        return "请输入小说文本"
    return "【占位输出】\n\nAI转换功能将在后续版本中实现。\n\n当前输入字数：" + str(len(text))


# Gradio界面
with gr.Blocks(title="AI小说转剧本工具") as demo:
    gr.Markdown("# AI小说转剧本工具")
    gr.Markdown("将小说文本转换为结构化剧本（YAML格式）")

    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="小说文本",
                placeholder="请粘贴至少3个章节的小说文本...",
                lines=20,
            )
            convert_btn = gr.Button("转换为剧本", variant="primary")
        with gr.Column():
            output_text = gr.Textbox(
                label="剧本输出（YAML格式）",
                lines=20,
                interactive=False,
            )

    convert_btn.click(
        fn=convert_novel,
        inputs=input_text,
        outputs=output_text,
    )


if __name__ == "__main__":
    demo.launch()
