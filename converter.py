"""
AI转换核心模块

负责调用DeepSeek API，将小说文本转换为结构化剧本。
"""

import os
import json
import yaml
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

from prompts import (
    get_chapter_analysis_messages,
    get_story_bible_messages,
    get_screenplay_generation_messages,
    extract_json_from_response,
)
from schema import validate_screenplay

# 加载环境变量
load_dotenv()


def get_client() -> OpenAI:
    """
    获取DeepSeek API客户端。

    Returns:
        OpenAI客户端实例
    """
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    if not api_key or api_key == "your_api_key_here":
        raise ValueError("请在 .env 文件中配置 DEEPSEEK_API_KEY")

    return OpenAI(api_key=api_key, base_url=base_url)


def call_api(messages: list, temperature: float = 0.7) -> str:
    """
    调用DeepSeek API。

    Args:
        messages: OpenAI格式的消息列表
        temperature: 温度参数（0-1，越低越确定）

    Returns:
        AI返回的文本

    Raises:
        ValueError: API密钥未配置
        Exception: API调用失败
    """
    client = get_client()
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=8192,
    )

    return response.choices[0].message.content


def analyze_chapter(chapter_content: str) -> Tuple[Optional[Dict], str]:
    """
    分析单个章节，提取角色、场景、情节。

    Args:
        chapter_content: 章节文本内容

    Returns:
        (result, error) 元组
        - result: 分析结果字典，失败时为None
        - error: 错误信息，成功时为空字符串
    """
    if not chapter_content or not chapter_content.strip():
        return None, "章节内容为空"

    try:
        messages = get_chapter_analysis_messages(chapter_content)
        response_text = call_api(messages, temperature=0.2)
        result = extract_json_from_response(response_text)

        if result is None:
            return None, "AI返回的内容无法解析为JSON"

        # 验证必要字段
        required_fields = ["chapter_summary", "characters", "scenes", "plot_points"]
        missing = [f for f in required_fields if f not in result]
        if missing:
            return None, f"AI返回缺少字段: {', '.join(missing)}"

        return result, ""

    except ValueError as e:
        return None, str(e)
    except Exception as e:
        return None, f"API调用失败: {str(e)}"


def generate_story_bible(chapter_analyses: List[Dict]) -> Tuple[Optional[Dict], str]:
    """
    合并多章分析结果为Story Bible。

    Args:
        chapter_analyses: 各章分析结果列表

    Returns:
        (result, error) 元组
    """
    try:
        messages = get_story_bible_messages(chapter_analyses)
        response_text = call_api(messages, temperature=0.2)
        result = extract_json_from_response(response_text)

        if result is None:
            return None, "AI返回的内容无法解析为JSON"

        return result, ""

    except ValueError as e:
        return None, str(e)
    except Exception as e:
        return None, f"API调用失败: {str(e)}"


def generate_screenplay(
    story_bible: Dict,
    chapter_analyses: List[Dict],
    chapter_count: int,
) -> Tuple[Optional[Dict], str]:
    """
    生成结构化剧本。

    Args:
        story_bible: Story Bible数据
        chapter_analyses: 各章分析结果
        chapter_count: 原文章节数

    Returns:
        (result, error) 元组
    """
    try:
        messages = get_screenplay_generation_messages(
            story_bible, chapter_analyses, chapter_count
        )
        response_text = call_api(messages, temperature=0.2)
        result = extract_json_from_response(response_text)

        if result is None:
            return None, "AI返回的内容无法解析为JSON"

        # 添加生成时间
        result["generated_at"] = datetime.now(timezone.utc).isoformat()

        # Schema校验
        is_valid, errors = validate_screenplay(result)
        if not is_valid:
            return result, f"生成的剧本Schema校验失败: {'; '.join(errors[:3])}"

        return result, ""

    except ValueError as e:
        return None, str(e)
    except Exception as e:
        return None, f"API调用失败: {str(e)}"


def to_yaml(data: Dict) -> str:
    """
    将字典转换为YAML格式字符串。

    Args:
        data: 要转换的字典

    Returns:
        YAML格式字符串
    """
    return yaml.dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=120,
    )


def pipeline(text: str) -> Tuple[str, str]:
    """
    完整转换流水线：文本 → 章节解析 → AI分析 → 合并 → 生成剧本 → YAML。

    Args:
        text: 小说全文

    Returns:
        (yaml_output, error) 元组
        - yaml_output: YAML格式剧本，失败时为空字符串
        - error: 错误信息，成功时为空字符串
    """
    from chapter_parser import split_chapters

    # 1. 章节解析
    chapters = split_chapters(text)
    if not chapters:
        return "", "无法解析章节"

    # 2. 逐章分析
    analyses = []
    for ch in chapters:
        result, error = analyze_chapter(ch["content"])
        if error:
            return "", f"第{ch['index']}章分析失败: {error}"
        analyses.append(result)

    # 3. 合并Story Bible
    story_bible, error = generate_story_bible(analyses)
    if error:
        return "", f"Story Bible合并失败: {error}"

    # 4. 生成剧本
    screenplay, error = generate_screenplay(story_bible, analyses, len(chapters))
    if screenplay is None:
        return "", f"剧本生成失败: {error}"

    # 5. 转换为YAML
    yaml_output = to_yaml(screenplay)

    return yaml_output, error  # error可能是校验警告


# 测试代码
if __name__ == "__main__":
    import sys

    # 检查API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        print("错误: 请在 .env 文件中配置 DEEPSEEK_API_KEY")
        print("编辑 ~/ai-novel-to-screenplay/.env 文件")
        sys.exit(1)

    # 测试单章分析
    test_chapter = """第一节：纵身亡魔心仍不悔

方源一身残破的碧绿大袍，披头散发，浑身浴血，环顾四周。
山风吹得血袍飘荡，如战旗般嚯嚯作响。
鲜红的血液，从身上数百道伤口向外涌着。

"方源，乖乖地交出春秋蝉，我给你个痛快！"
"方老魔，你不要妄图反抗了，今日我们正道各大派联合起来，就是要踏破你的魔窟。"

方源对局势洞若观火，不过即便死亡将临，他仍旧是面不改色，神情平淡。
他目光幽幽，如古井深潭一般，一如既往的深不见底。"""

    print("正在分析章节...")
    result, error = analyze_chapter(test_chapter)

    if error:
        print(f"分析失败: {error}")
    else:
        print(f"分析成功!")
        print(f"  概述: {result['chapter_summary']}")
        print(f"  角色数: {len(result['characters'])}")
        for c in result['characters']:
            print(f"    - {c['name']} ({c['role']})")
        print(f"  场景数: {len(result['scenes'])}")
        for s in result['scenes']:
            print(f"    - {s['title']} @ {s['location']}")
        print(f"  情节点: {len(result['plot_points'])}")
        for p in result['plot_points']:
            print(f"    - {p}")
