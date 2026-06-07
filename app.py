"""
AI小说转剧本工具 - 主界面（典雅中国风重制版）
"""

import os
import re
import json
import tempfile
from datetime import datetime

import gradio as gr
import yaml as yaml_lib

from chapter_parser import split_chapters, get_chapter_count
from schema import validate_screenplay
from converter import analyze_chapter, generate_story_bible, generate_screenplay, to_yaml
from library import scan_folder, _read_chapters_range, suggest_default_folder

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "examples")
SAMPLE_FILE = os.path.join(EXAMPLES_DIR, "sample_novel.txt")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), ".history.json")
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&family=Ma+Shan+Zheng&display=swap');

:root {
    --paper:        #f4ecd8;
    --paper-deep:   #ebe0c4;
    --paper-edge:   #d9cba6;
    --ink:          #2b2118;
    --ink-soft:     #5a4a3a;
    --ink-faint:    #8a7a66;
    --cinnabar:     #9b2c2c;
    --cinnabar-dk:  #7a1f1f;
    --bamboo:       #5a7a52;
    --bamboo-dk:    #3d5638;
    --gold:         #b08840;
    --shadow:       0 1px 3px rgba(60,40,20,.08), 0 6px 18px rgba(60,40,20,.06);
}

.gradio-container {
    font-family: 'Noto Serif SC', 'Songti SC', serif !important;
    background:
        radial-gradient(ellipse at top, #faf3df 0%, var(--paper) 55%, var(--paper-deep) 100%) !important;
    color: var(--ink) !important;
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 24px 32px !important;
}

/* 让文本域拉伸到列宽 */
.gradio-container textarea {
    width: 100% !important;
}

/* 顶部卷轴标题区 */
.scroll-banner {
    position: relative;
    text-align: center;
    padding: 32px 24px 18px;
    margin-bottom: 8px;
}
.scroll-banner::before, .scroll-banner::after {
    content: "";
    position: absolute;
    left: 8%;
    right: 8%;
    height: 6px;
    background:
        linear-gradient(90deg,
            transparent 0%, var(--gold) 8%, var(--gold) 92%, transparent 100%);
    border-radius: 3px;
    opacity: .55;
}
.scroll-banner::before { top: 0; }
.scroll-banner::after  { bottom: 0; }
.scroll-title {
    font-family: 'Ma Shan Zheng', 'Noto Serif SC', serif !important;
    font-size: 2.6rem !important;
    font-weight: 900 !important;
    color: var(--ink) !important;
    letter-spacing: .4em;
    margin: 0 !important;
    text-indent: .4em;
}
.scroll-subtitle {
    font-size: .95rem !important;
    color: var(--ink-soft) !important;
    letter-spacing: .25em;
    margin-top: 6px !important;
    font-weight: 300;
}
.scroll-seal {
    display: inline-block;
    margin-left: 14px;
    padding: 3px 9px;
    background: var(--cinnabar);
    color: var(--paper);
    font-family: 'Ma Shan Zheng', serif;
    font-size: 1.05rem;
    line-height: 1;
    border-radius: 3px;
    transform: rotate(-4deg);
    box-shadow: 0 0 0 2px var(--cinnabar-dk) inset;
    letter-spacing: .15em;
    vertical-align: middle;
}

/* 面板通用样式 */
.paper-panel {
    background: rgba(255, 252, 240, .55) !important;
    border: 1px solid var(--paper-edge) !important;
    border-radius: 6px !important;
    box-shadow: var(--shadow) !important;
    padding: 14px 18px !important;
}
.panel-title {
    font-family: 'Ma Shan Zheng', 'Noto Serif SC', serif !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    color: #fff8e8 !important;
    margin: -4px -8px 14px -8px !important;
    padding: 10px 18px;
    background: linear-gradient(180deg, #b03535 0%, var(--cinnabar) 55%, var(--cinnabar-dk) 100%);
    border: 1px solid var(--cinnabar-dk);
    border-radius: 4px;
    box-shadow: 0 2px 0 var(--cinnabar-dk), inset 0 1px 0 rgba(255, 240, 200, .25);
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: .25em;
    text-indent: .25em;
    text-shadow: 0 1px 0 rgba(0, 0, 0, .25);
    position: relative;
}
.panel-title::before, .panel-title::after {
    content: "";
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 60%;
    background: rgba(255, 240, 200, .35);
    border-radius: 2px;
}
.panel-title::before { left: 6px; }
.panel-title::after  { right: 6px; }
.panel-title .glyph {
    color: #ffe6a8;
    font-size: 1.35rem;
    text-shadow: 0 1px 0 rgba(0, 0, 0, .3);
}
.panel-title .meta {
    margin-left: auto;
    font-size: .8rem;
    font-weight: 400;
    color: rgba(255, 240, 200, .85);
    font-family: 'Noto Sans SC', sans-serif;
    letter-spacing: .05em;
    text-indent: 0;
    text-shadow: 0 1px 0 rgba(0, 0, 0, .2);
}

/* 文本域 */
textarea, input[type="text"] {
    font-family: 'Noto Serif SC', serif !important;
    background: #fdf9ec !important;
    border: 1px solid var(--paper-edge) !important;
    color: var(--ink) !important;
    line-height: 1.8 !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: var(--cinnabar) !important;
    box-shadow: 0 0 0 2px rgba(155,44,44,.15) !important;
    outline: none !important;
}

/* 按钮 */
button.primary, button.lg.primary {
    background: linear-gradient(180deg, #b03535 0%, var(--cinnabar) 50%, var(--cinnabar-dk) 100%) !important;
    color: #fff8e8 !important;
    border: 1px solid var(--cinnabar-dk) !important;
    font-family: 'Noto Serif SC', serif !important;
    font-weight: 600 !important;
    letter-spacing: .15em;
    box-shadow: 0 2px 0 var(--cinnabar-dk), var(--shadow) !important;
}
button.primary:hover {
    background: linear-gradient(180deg, #c0392b 0%, #a82a2a 100%) !important;
}
button.secondary {
    background: linear-gradient(180deg, #faf3df 0%, var(--paper-deep) 100%) !important;
    color: var(--ink) !important;
    border: 1px solid var(--paper-edge) !important;
    font-family: 'Noto Serif SC', serif !important;
    letter-spacing: .1em;
}
button.secondary:hover {
    background: var(--paper-edge) !important;
    color: var(--cinnabar-dk) !important;
}

/* 进度条 */
.progress-track {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0;
    margin: 6px 4px 14px;
    position: relative;
}
.progress-step {
    flex: 1;
    text-align: center;
    position: relative;
    z-index: 2;
}
.progress-step .dot {
    width: 28px; height: 28px; line-height: 28px;
    margin: 0 auto 4px;
    border-radius: 50%;
    background: var(--paper-deep);
    color: var(--ink-faint);
    border: 2px solid var(--paper-edge);
    font-family: 'Noto Serif SC', serif;
    font-weight: 600;
    font-size: .9rem;
    transition: all .25s ease;
}
.progress-step .label {
    font-size: .78rem;
    color: var(--ink-faint);
    font-family: 'Noto Sans SC', sans-serif;
    letter-spacing: .1em;
}
.progress-step.active .dot {
    background: var(--cinnabar);
    color: var(--paper);
    border-color: var(--cinnabar-dk);
    box-shadow: 0 0 0 4px rgba(155,44,44,.15);
}
.progress-step.active .label { color: var(--cinnabar-dk); font-weight: 500; }
.progress-step.done .dot {
    background: var(--bamboo);
    color: var(--paper);
    border-color: var(--bamboo-dk);
}
.progress-step.done .label { color: var(--bamboo-dk); }
.progress-rail {
    position: absolute;
    top: 14px; left: 12%; right: 12%;
    height: 2px;
    background: var(--paper-edge);
    z-index: 1;
}
.progress-rail-fill {
    height: 100%;
    background: var(--bamboo);
    transition: width .4s ease;
}

/* 状态条 */
.status-bar {
    font-family: 'Noto Sans SC', sans-serif;
    font-size: .85rem;
    color: var(--ink-soft);
    padding: 6px 12px;
    background: rgba(255, 252, 240, .6);
    border-left: 3px solid var(--cinnabar);
    border-radius: 0 4px 4px 0;
    margin-top: 8px;
}
.status-bar.success { border-left-color: var(--bamboo); color: var(--bamboo-dk); }
.status-bar.error   { border-left-color: var(--cinnabar); color: var(--cinnabar-dk); }

/* 统计卡片 */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 10px;
    margin: 10px 0;
}
.stat-card {
    background: linear-gradient(135deg, #fdf9ec 0%, var(--paper) 100%);
    border: 1px solid var(--paper-edge);
    border-radius: 4px;
    padding: 12px 14px;
    text-align: center;
}
.stat-card .num {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--cinnabar);
    line-height: 1.1;
}
.stat-card .lbl {
    font-size: .78rem;
    color: var(--ink-soft);
    margin-top: 2px;
    letter-spacing: .15em;
}

/* 角色徽章 */
.char-badges { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
.char-badge {
    background: var(--paper-deep);
    color: var(--ink);
    padding: 3px 10px;
    border-radius: 12px;
    font-size: .8rem;
    border: 1px solid var(--paper-edge);
}
.char-badge.protagonist { background: var(--cinnabar); color: var(--paper); border-color: var(--cinnabar-dk); }
.char-badge.antagonist  { background: #4a4a4a; color: var(--paper); border-color: #2b2b2b; }

/* Tabs */
.tab-nav button {
    font-family: 'Noto Serif SC', serif !important;
    letter-spacing: .1em;
}

/* 下拉框 */
select, .gr-box select {
    font-family: 'Noto Sans SC', sans-serif !important;
    background: #fdf9ec !important;
    border: 1px solid var(--paper-edge) !important;
    color: var(--ink) !important;
}

/* 隐藏 Gradio 默认 footer 美化 */
footer { display: none !important; }
"""

STEP_LABELS = ["解析章节", "逐章分析", "合并角色", "生成剧本", "校验输出"]


def _read_sample():
    try:
        with open(SAMPLE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _example_choices():
    full = _read_sample()
    if not full:
        return [("示例：《蛊真人》节选", "")]
    lines = full.splitlines(keepends=True)
    ch1_end = next((i for i, l in enumerate(lines) if i > 5 and l.startswith("第二节")), len(lines))
    ch2_end = next((i for i, l in enumerate(lines) if i > ch1_end + 5 and l.startswith("第三节")), len(lines))
    return [
        ("示例 1：第一章（最快）", "".join(lines[:ch1_end])),
        ("示例 2：前两章（推荐）", "".join(lines[:ch2_end])),
        ("示例 3：全文三章（完整）", full),
    ]


def _load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _load_labels():
    return [f"{h['time']} · {h['title']} · {h['stats']}" for h in _load_history()]


def _save_history(entry, yaml_text=""):
    """写入历史记录并把对应 YAML 落到 outputs/ 目录，便于恢复/下载。"""
    if yaml_text:
        try:
            os.makedirs(OUTPUTS_DIR, exist_ok=True)
            slug = re.sub(r"[^\w\u4e00-\u9fff\-]+", "_", entry.get("title", "untitled"))[:40] or "untitled"
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(OUTPUTS_DIR, f"{ts}_{slug}.yaml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(yaml_text)
            entry["file"] = path
        except Exception as e:
            import traceback
            print(f"[ERROR] _save_history: {e}\n{traceback.format_exc()}")
    history = _load_history()
    history.insert(0, entry)
    history = history[:10]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        import traceback
        print(f"[ERROR] history.json: {e}\n{traceback.format_exc()}")
    return [f"{h['time']} · {h['title']} · {h['stats']}" for h in history]


def _restore_from_history(label):
    """根据下拉框的 label 从 outputs/ 找回对应的 YAML 并填回输出框。"""
    if not label:
        return "", "", _build_stats_html({}), _status_html("未选择历史条目", "error")
    for h in _load_history():
        if f"{h['time']} · {h['title']} · {h['stats']}" == label:
            path = h.get("file")
            if not path or not os.path.exists(path):
                return "", "", _build_stats_html({}), _status_html("⚠ 该历史条目文件已丢失", "error")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    yaml_text = f.read()
                # 尝试解析回 dict 用于可读/统计
                # 先剥离开头的 markdown 标题/提示行（仅在解析时去除，不影响 yaml_text 输出）
                import re as _re
                yaml_only = _re.sub(r"^#[^\n]*\n+", "", yaml_text)
                yaml_only = _re.sub(r"^>[^\n]*\n+", "", yaml_only, flags=_re.MULTILINE).lstrip()
                try:
                    data = yaml_lib.safe_load(yaml_only) or {}
                except Exception:
                    data = {}
                readable = _format_screenplay_readable(data)
                stats_html = _build_stats_html(data)
                return readable, yaml_text, stats_html, _status_html(
                    f"📜 已恢复：《{h['title']}》", "success"
                )
            except Exception as e:
                return "", "", _build_stats_html({}), _status_html(f"恢复失败：{e}", "error")
    return "", "", _build_stats_html({}), _status_html("未找到该历史条目", "error")


def _clear_history_file():
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
    except Exception:
        pass
    return None


def _format_screenplay_readable(data: dict) -> str:
    """将剧本数据渲染为可读的中文剧本格式（非 YAML）。"""
    if not data:
        return ""
    out = []
    title = data.get("title", "未命名")
    out.append(f"# {title}\n")
    out.append(f"**{len(data.get('characters', []))} 角色 · "
               f"{len(data.get('acts', []))} 幕 · "
               f"{sum(len(a.get('scenes', [])) for a in data.get('acts', []))} 场景**\n")
    for act in data.get("acts", []):
        out.append(f"\n## {act.get('title', '')}")
        if act.get("purpose"):
            out.append(f"_{act['purpose']}_\n")
        for sc in act.get("scenes", []):
            heading = sc.get("heading") or f"{sc.get('location', '')} - {sc.get('time', '')}"
            out.append(f"\n### {sc.get('id', '')} · {heading}\n")
            for blk in sc.get("blocks", []):
                t = blk.get("type", "")
                if t == "action":
                    out.append(f"  {blk.get('text', '')}")
                elif t == "dialogue":
                    ch = blk.get("character", "")
                    paren = blk.get("parenthetical", "")
                    txt = blk.get("text", "")
                    if paren:
                        out.append(f"  > *{paren}*")
                    out.append(f"  > **{ch}**：{txt}")
                elif t == "transition":
                    out.append(f"\n  —— {blk.get('text', '')} ——")
    return "\n".join(out)


def _build_stats_html(data: dict) -> str:
    if not data:
        return (
            '<div style="text-align:center;padding:36px 20px;color:var(--ink-faint);">'
            '<div style="font-size:2.4rem;margin-bottom:10px;opacity:.5;">🎭</div>'
            '<div style="font-family:\'Noto Serif SC\',serif;font-size:1rem;'
            'letter-spacing:.15em;color:var(--ink-soft);margin-bottom:6px;">剧本尚未生成</div>'
            '<div style="font-size:.8rem;letter-spacing:.1em;">'
            '粘贴文本或载入示例，点击「转换」后将在此显示角色、幕、场景统计。</div>'
            '</div>'
        )
    chars = data.get("characters", [])
    acts = data.get("acts", [])
    scenes = sum(len(a.get("scenes", [])) for a in acts)
    blocks = sum(
        len(s.get("blocks", []))
        for a in acts for s in a.get("scenes", [])
    )
    html = f"""
<div class="stats-grid">
  <div class="stat-card"><div class="num">{len(chars)}</div><div class="lbl">角色</div></div>
  <div class="stat-card"><div class="num">{len(acts)}</div><div class="lbl">幕</div></div>
  <div class="stat-card"><div class="num">{scenes}</div><div class="lbl">场景</div></div>
  <div class="stat-card"><div class="num">{blocks}</div><div class="lbl">剧本块</div></div>
</div>
<div class="char-badges">
"""
    for c in chars[:30]:
        name = c.get("name", "?")
        role = c.get("role", "supporting")
        html += f'<span class="char-badge {role}">{name}</span>'
    html += "</div>"
    return html


def _status_html(text: str, kind: str = "info") -> str:
    return f'<div class="status-bar {kind}">{text}</div>'


def _step_html(active: int) -> str:
    """生成三步骤进度条 HTML（步骤 0=未开始, 1=解析, 2=分析, 3=生成）。"""
    steps = [
        ("壹", "解析章节"),
        ("贰", "AI 分析"),
        ("叁", "生成剧本"),
    ]
    parts = ['<div class="progress-track"><div class="progress-rail"><div class="progress-rail-fill" '
             f'style="width: {max(0, min(100, (active-1)*50))}%"></div></div>']
    for i, (num, lbl) in enumerate(steps, start=1):
        cls = "done" if active > i else ("active" if active == i else "")
        parts.append(
            f'<div class="progress-step {cls}">'
            f'<div class="dot">{num if cls != "done" else "✓"}</div>'
            f'<div class="label">{lbl}</div></div>'
        )
    parts.append('</div>')
    return "".join(parts)


def _convert_stream(text, progress=gr.Progress(track_tqdm=False)):
    """流式生成器：每步 yield 当前 UI 状态。"""
    if not text or not text.strip():
        yield (
            "", "",
            _build_stats_html({}),
            _status_html("⚠ 请先粘贴小说文本", "error"),
            _step_html(0),
            gr.update(visible=False),
        )
        return

    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        yield (
            "", "",
            _build_stats_html({}),
            _status_html("❌ API 密钥未配置 · 请在 .env 中填入 DEEPSEEK_API_KEY", "error"),
            _step_html(0),
            gr.update(visible=False),
        )
        return

    progress(0.05, "解析章节…")
    detected = get_chapter_count(text)
    chapters = split_chapters(text)
    chapter_count = len(chapters)
    if detected < 1:
        yield (
            "", "",
            _build_stats_html({}),
            _status_html("❌ 未检测到章节 · 请确保文本包含「第X章」标记", "error"),
            _step_html(0),
            gr.update(visible=False),
        )
        return
    if chapter_count > 5:
        chapters = chapters[:5]
        chapter_count = 5

    yield (
        "", "", _build_stats_html({}),
        _status_html(f"✓ 已识别 {chapter_count} 个章节 · 准备开始分析"),
        _step_html(1), gr.update(visible=True),
    )

    analyses = []
    for i, ch in enumerate(chapters):
        progress((i + 1) / (chapter_count + 2), f"分析第 {i+1}/{chapter_count} 章 · {ch['title']}")
        yield (
            f"⏳ 正在分析第 {i+1}/{chapter_count} 章 · {ch['title']}\n\n_请耐心等待 AI 返回结果…_",
            "", _build_stats_html({}),
            _status_html(f"⏳ 分析第 {i+1}/{chapter_count} 章", "info"),
            _step_html(2), gr.update(visible=True),
        )
        result, error = analyze_chapter(ch["content"])
        if error:
            yield (
                f"❌ 第 {i+1} 章分析失败：{error}", "",
                _build_stats_html({}),
                _status_html(f"❌ 分析失败：{error}", "error"),
                _step_html(2), gr.update(visible=True),
            )
            return
        analyses.append(result)

    progress(0.85, "合并角色与场景…")
    yield (
        f"✓ 已完成 {len(analyses)} 章分析\n\n⏳ 正在合并角色、场景、关系…",
        "", _build_stats_html({}),
        _status_html("⏳ 合并 Story Bible…"),
        _step_html(2), gr.update(visible=True),
    )
    story_bible, error = generate_story_bible(analyses)
    if error:
        yield (
            f"❌ {error}", "",
            _build_stats_html({}),
            _status_html(f"❌ {error}", "error"),
            _step_html(2), gr.update(visible=True),
        )
        return

    progress(0.92, "生成结构化剧本…")
    yield (
        f"✓ Story Bible 已生成\n\n⏳ 正在生成结构化剧本（幕/场景/块）…",
        "", _build_stats_html({}),
        _status_html("⏳ 生成剧本…"),
        _step_html(3), gr.update(visible=True),
    )
    screenplay, error = generate_screenplay(story_bible, analyses, chapter_count)

    if screenplay is None:
        yield (
            f"❌ {error}", "",
            _build_stats_html({}),
            _status_html(f"❌ {error}", "error"),
            _step_html(3), gr.update(visible=True),
        )
        return

    is_valid, errors = validate_screenplay(screenplay)
    title = screenplay.get("title", "未命名")
    n_chars = len(screenplay.get("characters", []))
    n_acts = len(screenplay.get("acts", []))
    n_scenes = sum(len(a.get("scenes", [])) for a in screenplay.get("acts", []))
    yaml_text = to_yaml(screenplay)
    readable = _format_screenplay_readable(screenplay)
    stats_html = _build_stats_html(screenplay)

    header = f"# {title}\n\n> {n_chars} 角色 · {n_acts} 幕 · {n_scenes} 场景\n\n"
    if not is_valid:
        header += f"> ⚠️ 校验提示：{errors[0] if errors else '未知错误'}\n\n"
    yaml_with_header = header + yaml_text
    readable_with_header = header + readable

    if is_valid:
        status = _status_html(f"✅ 生成完成 · 《{title}》 · {n_chars} 角色 / {n_acts} 幕 / {n_scenes} 场景", "success")
    else:
        status = _status_html(f"⚠️ 生成完成但存在校验问题 · 《{title}》", "error")

    new_hist = _save_history({
        "time": datetime.now().strftime("%m-%d %H:%M"),
        "title": title,
        "stats": f"{n_chars}角/{n_acts}幕/{n_scenes}场",
    }, yaml_text=yaml_with_header)

    # 把 YAML 写到 outputs/ 目录，返回文件路径给 gr.File
    try:
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        slug = re.sub(r"[^\w\u4e00-\u9fff\-]+", "_", title)[:40] or "untitled"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        yaml_path = os.path.join(OUTPUTS_DIR, f"{ts}_{slug}.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_with_header)
        file_update = gr.update(visible=True, value=yaml_path)
    except Exception as e:
        import traceback
        print(f"[ERROR] yaml write: {e}\n{traceback.format_exc()}")
        file_update = gr.update(visible=False, value=None)

    progress(1.0, "完成")
    yield (
        readable_with_header,
        yaml_with_header,
        stats_html,
        status,
        _step_html(4),
        file_update,
    )
    return new_hist, gr.update(choices=new_hist)


def convert_novel(text, progress=gr.Progress(track_tqdm=False)):
    """非流式入口（保留以兼容 API）。"""
    final = None
    for state in _convert_stream(text, progress):
        final = state
    return final[0], final[1], final[2], final[3], final[4], final[5]


def load_example(choice):
    examples = _example_choices()
    for label, content in examples:
        if label == choice:
            return content, f"已加载：{label}（{len(content)} 字）"
    return "", "未找到示例"


def copy_to_clipboard():
    return gr.update(value="已复制 ✓ 剧本内容到剪贴板")


def _scan_folder_action(folder):
    """扫描文件夹并返回文件下拉选项。"""
    if not folder or not folder.strip():
        return gr.update(choices=[], value=None), _status_html("⚠ 请输入文件夹路径", "error")
    if not os.path.isdir(folder):
        return gr.update(choices=[], value=None), _status_html(f"❌ 文件夹不存在：{folder}", "error")
    files = scan_folder(folder)
    if not files:
        return gr.update(choices=[], value=None), _status_html(f"📂 {folder} 中未找到小说文件", "error")
    # 选项文本：相对路径 + 大小 + 估算章节数
    choices = [
        f"{f['rel_path']}  ·  {f['size_human']}  ·  ~{f['chapter_count']} 章"
        for f in files
    ]
    paths = [f["path"] for f in files]
    return (
        gr.update(choices=choices, value=choices[0] if choices else None),
        _status_html(f"📚 找到 {len(files)} 个文件：{folder}", "success"),
        gr.update(value=paths[0] if paths else None),
    )


def _load_from_library(file_choice, start_ch, end_ch):
    """从选中文件加载指定章节范围。"""
    if not file_choice:
        return "", _status_html("⚠ 请先扫描文件夹并选择文件", "error")
    # Gradio 6 的 Dropdown 返回 (display, value) 元组，提取 value
    if isinstance(file_choice, (list, tuple)):
        file_choice = file_choice[-1] if len(file_choice) >= 1 else ""
    file_choice = str(file_choice).strip()
    if not file_choice:
        return "", _status_html("⚠ 文件选择为空", "error")
    # 反查路径
    folder = suggest_default_folder()
    files = scan_folder(folder)  # 复用扫描结果
    target_path = None
    for f in files:
        label = f"{f['rel_path']}  ·  {f['size_human']}  ·  ~{f['chapter_count']} 章"
        if label == file_choice:
            target_path = f["path"]
            break
    if not target_path or not os.path.exists(target_path):
        return "", _status_html(f"❌ 文件不存在：{file_choice[:60]}", "error")
    try:
        # 1) 类型与范围校验
        try:
            s = int(start_ch) if str(start_ch).strip() else 1
        except (TypeError, ValueError):
            return "", _status_html(f"⚠ 起始章无效：{start_ch}", "error")
        try:
            e = int(end_ch) if str(end_ch).strip() else None
        except (TypeError, ValueError):
            return "", _status_html(f"⚠ 结束章无效：{end_ch}", "error")
        if s < 1:
            return "", _status_html("⚠ 起始章必须 ≥ 1", "error")
        if e is not None and e < s:
            return "", _status_html(f"⚠ 结束章 ({e}) 不能小于起始章 ({s})", "error")
        # 2) 加载
        text, info = _read_chapters_range(target_path, start=s, end=e)
        sc, ec = info["selected_range"]
        total = info["total_chapters"]
        # 3) 结果状态
        warn = ""
        if total == 0:
            return "", _status_html("⚠ 文件中未检测到章节", "error")
        if sc is None or ec is None:
            return "", _status_html(f"⚠ 章节 {s}-{e or '?'} 超出范围（共 {total} 章）", "error")
        if s > total:
            return "", _status_html(f"⚠ 起始章 {s} 超出总章节数 {total}", "error")
        if e is not None and e > total:
            warn = f" · 结束章 {e} 超过总章节数，已截到第 {total} 章"
        if total > 5 and (ec - sc + 1) > 5:
            warn = f" · 已截取前 5 章用于转换（{sc}-{min(ec, sc+4)}）"
        msg = f"📖 已加载：第 {sc}-{ec} 章 / 共 {total} 章 · {len(text)} 字{warn}"
        kind = "success" if not warn else "info"
        return text, _status_html(msg, kind)
    except Exception as ex:
        return "", _status_html(f"❌ 加载失败：{ex}", "error")


def _build_ui():
    examples = _example_choices()
    history = _load_history()
    history_labels = [f"{h['time']} · {h['title']} · {h['stats']}" for h in history]

    with gr.Blocks(title="剧本工坊 · 典雅版") as demo:
        gr.HTML(f"""
<div class="scroll-banner">
  <h1 class="scroll-title">剧 本 工 坊<span class="scroll-seal">印</span></h1>
  <div class="scroll-subtitle">A I · 小 说 · 转 · 剧 本 · 工 具</div>
</div>
""")

        # ---------- 📚 书架：从文件夹自动加载小说 ----------
        with gr.Group(elem_classes="paper-panel"):
            gr.HTML('<div class="panel-title"><span class="glyph">📚</span>书　架  <span class="meta">从文件夹自动发现小说文件，按需提取章节</span></div>')
            with gr.Row():
                folder_in = gr.Textbox(
                    label=None, container=False, show_label=False,
                    placeholder=f"文件夹路径（默认 {suggest_default_folder()}）",
                    value=suggest_default_folder(),
                    scale=5,
                )
                scan_btn = gr.Button("🔍  扫 描", scale=1, elem_classes="secondary")
            with gr.Row():
                file_dd = gr.Dropdown(
                    choices=[], label=None, show_label=False, container=False,
                    scale=6, interactive=True,
                )
                file_path_state = gr.Textbox(visible=False)  # hidden state
                ch_start = gr.Number(label="起始章", value=1, minimum=1, precision=0,
                                     scale=1, container=False)
                ch_end = gr.Number(label="结束章", value=5, minimum=1, precision=0,
                                   scale=1, container=False)
                load_btn = gr.Button("📥  载入章节", scale=1, variant="primary")
            with gr.Row():
                gr.HTML('<div style="font-size:.78rem;color:var(--ink-soft);letter-spacing:.05em;">'
                        '提示：支持 .txt / .text 格式，单文件 1KB-100MB。'
                        '一次最多处理 5 章（DeepSeek API 限制），大文件请分段。'
                        '</div>')

        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group(elem_classes="paper-panel"):
                    gr.HTML('<div class="panel-title"><span class="glyph">📜</span>原文输入</div>')
                    with gr.Row():
                        example_dd = gr.Dropdown(
                            choices=[e[0] for e in examples],
                            value=examples[0][0] if examples else None,
                            label=None,
                            show_label=False,
                            scale=4,
                            container=False,
                        )
                        example_btn = gr.Button("📖 载入示例", scale=1, elem_classes="secondary")
                    input_text = gr.Textbox(
                        placeholder="在此粘贴小说文本…\n\n每章以「第X章 / 第X节 / Chapter X」开头\n\n建议 3-5 章，效果最佳。",
                        lines=28,
                        show_label=False,
                        container=False,
                    )

            with gr.Column(scale=1):
                with gr.Group(elem_classes="paper-panel"):
                    gr.HTML('<div class="panel-title"><span class="glyph">🎭</span>剧本输出</div>')
                    with gr.Tabs():
                        with gr.TabItem("📖 可读剧本"):
                            output_readable = gr.Textbox(
                                lines=28, show_label=False, interactive=False, container=False,
                                placeholder="转换完成后，此处显示格式化的可读剧本…",
                            )
                        with gr.TabItem("📄 YAML 原文"):
                            output_yaml = gr.Textbox(
                                lines=28, show_label=False, interactive=False, container=False,
                                placeholder="YAML 格式剧本将在此显示…",
                            )
                        with gr.TabItem("📊 统计信息"):
                            output_stats = gr.HTML(_build_stats_html({}))

        with gr.Group(elem_classes="paper-panel"):
            progress_html = gr.HTML(_step_html(0))
            status_html = gr.HTML(_status_html("就绪 · 等待输入"))
            with gr.Row():
                convert_btn = gr.Button("🔄  转  换", variant="primary", size="lg", scale=2)
                cancel_btn = gr.Button("⏹  取 消", variant="stop", size="lg", scale=1, visible=False)
                copy_btn = gr.Button("📋  复制 YAML", size="lg", scale=1)
                download_file = gr.File(
                    label="📥 下载 .yaml", visible=False, interactive=False, scale=1
                )
            with gr.Row():
                with gr.Column(scale=3):
                    history_dd = gr.Dropdown(
                        choices=history_labels,
                        value=history_labels[0] if history_labels else None,
                        label="📚 历史记录（点击 + 下方按钮可恢复）",
                        show_label=True,
                        allow_custom_value=True,
                        filterable=True,
                    )
                restore_btn = gr.Button("♻️  恢复选中", scale=1, elem_classes="secondary")
                clear_hist_btn = gr.Button("🗑  清空", scale=0, min_width=80, elem_classes="secondary")

        gr.HTML("""
<div style="text-align:center;margin-top:18px;font-size:.75rem;color:var(--ink-faint);letter-spacing:.2em;">
  ·  剧 本 工 坊  ·  AI × 文 学  ·  v2.0  ·
</div>
""")

        example_btn.click(
            fn=load_example,
            inputs=[example_dd],
            outputs=[input_text, status_html],
        )

        # 书架交互
        scan_btn.click(
            fn=_scan_folder_action,
            inputs=[folder_in],
            outputs=[file_dd, status_html, file_path_state],
        )
        # 按 Enter 触发扫描
        folder_in.submit(
            fn=_scan_folder_action,
            inputs=[folder_in],
            outputs=[file_dd, status_html, file_path_state],
        )
        load_btn.click(
            fn=_load_from_library,
            inputs=[file_dd, ch_start, ch_end],
            outputs=[input_text, status_html],
        )

        input_text.change(
            fn=lambda t: _status_html(
                f"已输入 {len(t)} 字 · 检测到 {get_chapter_count(t)} 章"
                if t and t.strip() else "就绪 · 等待输入"
            ),
            inputs=[input_text],
            outputs=[status_html],
        )

        convert_event = convert_btn.click(
            fn=_convert_stream,
            inputs=[input_text],
            outputs=[output_readable, output_yaml, output_stats,
                     status_html, progress_html, download_file],
        )

        # 转换进行中：显示「取消」按钮
        convert_btn.click(
            fn=lambda: gr.update(visible=True),
            inputs=None,
            outputs=[cancel_btn],
        )
        # 转换完成/出错后：隐藏「取消」按钮
        convert_event.then(
            fn=lambda: gr.update(visible=False),
            inputs=None,
            outputs=[cancel_btn],
        )
        # 点击「取消」会触发 cancels，停止 _convert_stream
        cancel_btn.click(
            fn=lambda: (_status_html("⏹ 已取消本次转换", "error"),
                        _step_html(0), gr.update(visible=False)),
            inputs=None,
            outputs=[status_html, progress_html, cancel_btn],
            cancels=[convert_event],
        )

        restore_btn.click(
            fn=_restore_from_history,
            inputs=[history_dd],
            outputs=[output_readable, output_yaml, output_stats, status_html],
        )

        # 转换成功后刷新历史下拉框选项
        convert_event.then(
            fn=lambda: gr.update(choices=_load_labels()),
            inputs=None,
            outputs=[history_dd],
        )

        clear_hist_btn.click(
            fn=lambda: (gr.update(choices=[], value=None),
                        _status_html("历史已清空", "success")),
            inputs=None,
            outputs=[history_dd, status_html],
        ).then(
            fn=_clear_history_file,
            inputs=None,
            outputs=[],
        )

        copy_btn.click(
            fn=None,
            inputs=[output_yaml],
            outputs=None,
            js="(text) => { if(!text){return '暂无内容';} navigator.clipboard.writeText(text); return '已复制'; }",
        )

    return demo


if __name__ == "__main__":
    demo = _build_ui()
    demo.launch(
        css=CUSTOM_CSS,
        server_name="127.0.0.1",
        server_port=7868,
        theme=gr.themes.Soft(),
        width="100%",
        height="100vh",
    )
