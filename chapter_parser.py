"""
章节解析模块

负责识别小说章节分隔符，将长文本拆分为独立章节。
支持多种中文章节格式。
"""

import re
from typing import List, Dict

# 章节标记正则表达式（按优先级排序）
CHAPTER_PATTERNS = [
    # "第X章" 格式（最常见）
    # 支持：第一章、第1章、第12章、第十章、第十二章
    re.compile(
        r"^[ \t]*第[一二三四五六七八九十百千零〇壹贰叁肆伍陆柒捌玖拾\d]+"
        r"[章回节卷篇部集]"
        r"[ \t]*.*$",
        re.MULTILINE,
    ),
    # "Chapter X" 格式（英文）
    re.compile(
        r"^[ \t]*(?:Chapter|CHAPTER|Ch\.?)\s*\d+.*$",
        re.MULTILINE,
    ),
    # "序章"、"序言"、"楔子"、"尾声"、"终章" 等特殊章节
    re.compile(
        r"^[ \t]*(?:序章|序言|序|楔子|引子|尾声|终章|后记|番外|附录|前言).*$",
        re.MULTILINE,
    ),
    # 纯数字开头 + 标题（如 "1 风起"、"01 风起"）
    re.compile(
        r"^[ \t]*\d{1,3}[ \t]+.{2,30}$",
        re.MULTILINE,
    ),
]


def detect_chapters(text: str) -> List[Dict]:
    """
    检测文本中的章节标记。

    Args:
        text: 小说全文

    Returns:
        章节列表，每个章节包含：
        - index: 章节序号（从1开始）
        - title: 章节标题（匹配到的行）
        - start: 起始位置（字符索引）
        - end: 结束位置（字符索引，下一章开始或文本末尾）
    """
    if not text or not text.strip():
        return []

    # 尝试每种模式，找到匹配最多的那种
    best_matches = []
    for pattern in CHAPTER_PATTERNS:
        matches = list(pattern.finditer(text))
        if len(matches) > len(best_matches):
            best_matches = matches

    if not best_matches:
        return []

    # 构建章节列表
    chapters = []
    for i, match in enumerate(best_matches):
        title = match.group().strip()
        start = match.start()

        # 结束位置：下一章开始 或 文本末尾
        if i + 1 < len(best_matches):
            end = best_matches[i + 1].start()
        else:
            end = len(text)

        chapters.append({
            "index": i + 1,
            "title": title,
            "start": start,
            "end": end,
        })

    return chapters


def split_chapters(text: str) -> List[Dict[str, str]]:
    """
    将文本按章节拆分。

    Args:
        text: 小说全文

    Returns:
        章节列表，每个章节包含：
        - index: 章节序号（从1开始）
        - title: 章节标题
        - content: 章节正文内容
    """
    chapters = detect_chapters(text)

    if not chapters:
        # 无法检测章节时，按字数自动分块
        return _auto_split(text)

    result = []
    for ch in chapters:
        content = text[ch["start"]:ch["end"]].strip()
        result.append({
            "index": ch["index"],
            "title": ch["title"],
            "content": content,
        })

    return result


def _auto_split(text: str, target_chars: int = 3000) -> List[Dict[str, str]]:
    """
    无法检测章节时，按字数自动分块。

    Args:
        text: 全文
        target_chars: 每块目标字数

    Returns:
        分块列表
    """
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        current_chunk.append(para)
        current_len += len(para)

        if current_len >= target_chars:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_len = 0

    # 最后一块
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    result = []
    for i, chunk in enumerate(chunks):
        result.append({
            "index": i + 1,
            "title": f"第{i + 1}部分",
            "content": chunk.strip(),
        })

    return result


def get_chapter_count(text: str) -> int:
    """
    获取章节数量（便捷函数）。

    Args:
        text: 小说全文

    Returns:
        检测到的章节数量
    """
    return len(detect_chapters(text))


# 测试代码
if __name__ == "__main__":
    test_text = """第一章 风起

那年春天，江南的雨格外多。

李明站在窗前，看着窗外的细雨，心中五味杂陈。

第二章 云涌

三个月后，局势急转直下。

李明收到了一封来自北方的信。

第三章 雷鸣

暴风雨终于来了。

整个城市陷入了一片混乱。"""

    chapters = split_chapters(test_text)
    print(f"检测到 {len(chapters)} 个章节：\n")
    for ch in chapters:
        print(f"  [{ch['index']}] {ch['title']}")
        print(f"      内容长度: {len(ch['content'])} 字")
        print(f"      前50字: {ch['content'][:50]}...")
        print()
