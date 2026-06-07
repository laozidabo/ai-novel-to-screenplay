"""
小说库扫描模块

负责扫描指定文件夹，识别小说文本文件，提取章节信息。
支持：.txt / .text 扩展名；按文件大小排序；快速章节检测（不加载全文）。
"""

import os
import re
import time
from typing import List, Dict, Optional

# 复用现有的章节检测
from chapter_parser import detect_chapters, split_chapters

# 小说文件扩展名
NOVEL_EXTENSIONS = {".txt", ".text"}

# 常见小说文件大小范围（小于 1KB 不太可能是完整小说，大于 100MB 也很少）
MIN_FILE_SIZE = 1024          # 1KB
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# 快速章节检测：只读文件前 N 字节估算章节数
PREVIEW_BYTES = 200 * 1024    # 200KB 用于预检测

# 文件总大小超过此值时，根据前 N 章推算总章节数（避免读 22MB 全文）
ESTIMATE_THRESHOLD = 1 * 1024 * 1024  # 1MB
ESTIMATE_SAMPLE_CH = 5                  # 用前 5 章的均长推算总章节数

# 目录遍历的最大深度（防止符号链接死循环）
MAX_DEPTH = 4


def _quick_chapter_count(filepath: str) -> int:
    """快速估算章节数（只读取前 200KB，加速扫描）。"""
    try:
        size = os.path.getsize(filepath)
        if size <= ESTIMATE_THRESHOLD:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return get_chapter_count(text)
        # 大文件：只读前 PREVIEW_BYTES，按前几章均长推算
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            preview = f.read(PREVIEW_BYTES)
        preview_chs = detect_chapters(preview)
        if not preview_chs:
            return 0
        # 用前 ESTIMATE_SAMPLE_CH 章的均长 × 文件大小推算
        sample = preview_chs[:ESTIMATE_SAMPLE_CH]
        if len(sample) < 2:
            return len(preview_chs)
        sample_len = sum(ch["end"] - ch["start"] for ch in sample) / len(sample)
        if sample_len <= 0:
            return len(preview_chs)
        # UTF-8 中文字符平均 ~3 字节，所以字符数 ≈ 字节数 / 3
        est = int(size / 3 / sample_len)
        return max(len(preview_chs), est)
    except Exception:
        return 0


def _read_chapters_range(filepath: str, start: int = 1, end: Optional[int] = None,
                         max_chars: int = 60_000) -> tuple:
    """
    读取文件中指定范围的章节。
    Args:
        filepath: 文件路径
        start: 起始章节（1-based）
        end: 结束章节（inclusive），None 表示到最后
        max_chars: 累计最大字符数（防止一次加载太多）
    Returns:
        (text, info_dict)
        text: 拼接后的章节文本
        info_dict: {total_chapters, selected_range, file_size, loaded_chars}
    """
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    chapters = detect_chapters(text)
    total = len(chapters)
    if total == 0:
        return text[:max_chars], {
            "total_chapters": 0,
            "selected_range": (0, 0),
            "file_size": len(text),
            "loaded_chars": min(len(text), max_chars),
            "warning": "未检测到章节标记",
        }
    s = max(1, start)
    e = min(total, end if end else total)
    if s > e:
        s, e = e, s
    # 截取章节内容
    pieces = []
    chars_used = 0
    selected = []
    for ch in chapters[s - 1: e]:
        content = text[ch["start"]:ch["end"]].strip()
        if chars_used + len(content) > max_chars:
            remaining = max_chars - chars_used
            if remaining <= 200:
                break
            content = content[:remaining] + "\n\n[…章节内容因字符上限被截断…]"
        pieces.append(content)
        chars_used += len(content)
        selected.append(ch["index"])
    return "\n\n".join(pieces), {
        "total_chapters": total,
        "selected_range": (s, e),
        "file_size": len(text),
        "loaded_chars": chars_used,
        "selected_count": len(selected),
    }


def get_chapter_count(text: str) -> int:
    """返回章节数量。"""
    return len(detect_chapters(text))


def scan_folder(folder: str, recursive: bool = True,
                extensions: set = None) -> List[Dict]:
    """
    扫描文件夹，列出所有候选小说文件。
    Args:
        folder: 文件夹绝对路径
        recursive: 是否递归子目录
        extensions: 自定义扩展名集合，None 使用默认 {.txt, .text}
    Returns:
        文件信息列表（按大小降序），每个元素：
        {path, name, rel_path, size_bytes, size_human, mtime, chapter_count, depth}
    """
    if extensions is None:
        extensions = NOVEL_EXTENSIONS
    if not folder or not os.path.isdir(folder):
        return []
    folder = os.path.abspath(folder)
    results = []
    def _walk(dir_path: str, depth: int):
        if depth > MAX_DEPTH:
            return
        try:
            entries = list(os.scandir(dir_path))
        except (PermissionError, OSError):
            return
        for entry in entries:
            if entry.is_file(follow_symlinks=False):
                ext = os.path.splitext(entry.name)[1].lower()
                if ext not in extensions:
                    continue
                try:
                    st = entry.stat()
                except OSError:
                    continue
                if st.st_size < MIN_FILE_SIZE or st.st_size > MAX_FILE_SIZE:
                    continue
                # 快速预检测章节
                ch_count = _quick_chapter_count(entry.path)
                if ch_count == 0:
                    # 完全没章节标记的纯文本可能不是小说，但可能是压缩成一团的纯文本
                    # 只在文件较大时接受
                    if st.st_size < 50 * 1024:
                        continue
                results.append({
                    "path": entry.path,
                    "name": entry.name,
                    "rel_path": os.path.relpath(entry.path, folder),
                    "size_bytes": st.st_size,
                    "size_human": _human_size(st.st_size),
                    "mtime": st.st_mtime,
                    "chapter_count": ch_count,
                    "depth": depth,
                })
            elif entry.is_dir(follow_symlinks=False) and recursive:
                # 跳过常见的忽略目录
                base = os.path.basename(entry.path)
                if base.startswith(".") or base in {"__pycache__", "node_modules", "venv", ".git"}:
                    continue
                _walk(entry.path, depth + 1)
    _walk(folder, 0)
    # 按大小降序（大文件更可能是完整小说）
    results.sort(key=lambda x: -x["size_bytes"])
    return results


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} GB"


# 预设文件夹（供 UI 默认值）
DEFAULT_FOLDERS = [
    os.path.dirname(__file__),                          # 项目根目录
    os.path.join(os.path.dirname(__file__), "examples"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop"),
]


def suggest_default_folder() -> str:
    """返回第一个存在的默认文件夹。"""
    for f in DEFAULT_FOLDERS:
        if os.path.isdir(f):
            return f
    return os.path.dirname(__file__)


# 测试
if __name__ == "__main__":
    folder = os.path.dirname(__file__)
    print(f"扫描: {folder}")
    t0 = time.time()
    files = scan_folder(folder)
    print(f"找到 {len(files)} 个文件 ({time.time()-t0:.2f}s):")
    for f in files[:10]:
        print(f"  {f['rel_path']} - {f['size_human']}, ~{f['chapter_count']} 章")
