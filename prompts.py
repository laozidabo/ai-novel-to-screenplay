"""
提示词模板模块

包含各阶段的AI提示词模板：
- 章节分析：提取角色、场景、情节
- Story Bible合并：合并多章分析结果
- 剧本生成：输出符合Schema的结构化剧本
"""

import json

# ============================================================
# 章节分析提示词
# ============================================================

CHAPTER_ANALYSIS_SYSTEM = """你是一位专业的剧本分析师。你的任务是分析小说章节，提取关键的剧本元素。

你必须严格按照指定的JSON格式输出，不要添加任何额外文字或解释。

输出要求：
1. 使用标准JSON格式
2. 所有字段都必须填写
3. 角色名称保持原文一致
4. 场景描述要具体（地点、时间、氛围）"""

CHAPTER_ANALYSIS_PROMPT = """请分析以下小说章节，提取剧本所需的结构化信息。

## 章节内容

{chapter_content}

## 输出要求

请以JSON格式输出以下信息：

```json
{{
  "chapter_summary": "本章主要情节概述（50字以内）",
  "characters": [
    {{
      "name": "角色名",
      "role": "protagonist/antagonist/supporting/minor",
      "description": "角色简要描述（外貌、性格、身份）"
    }}
  ],
  "scenes": [
    {{
      "title": "场景标题",
      "location": "地点",
      "time": "时间（白天/夜晚/清晨等）",
      "characters": ["出场角色名"],
      "summary": "场景概要（30字以内）"
    }}
  ],
  "plot_points": [
    "关键情节点1",
    "关键情节点2"
  ]
}}
```

注意：
- role只能填 protagonist（主角）、antagonist（反派）、supporting（配角）、minor（次要）
- 每个场景必须有明确的地点和时间
- 按情节发展顺序排列场景
- 提取所有有台词或有重要动作的角色"""


# ============================================================
# Story Bible合并提示词
# ============================================================

STORY_BIBLE_SYSTEM = """你是一位专业的剧本编辑。你的任务是合并多章分析结果，构建全局的Story Bible（改编资料库）。

你必须严格按照指定的JSON格式输出。"""

STORY_BIBLE_PROMPT = """请将以下多章分析结果合并为一份全局Story Bible。

## 各章分析结果

{chapter_analyses}

## 输出要求

请以JSON格式输出：

```json
{{
  "title": "故事标题（从内容推断）",
  "logline": "一句话故事梗概（30字以内）",
  "themes": ["主题1", "主题2"],
  "characters": [
    {{
      "name": "角色名",
      "role": "protagonist/antagonist/supporting/minor",
      "description": "综合描述",
      "first_seen_chapter": 1
    }}
  ],
  "locations": [
    {{
      "name": "地点名",
      "note": "地点描述",
      "chapters": [1, 2]
    }}
  ],
  "relationships": [
    {{
      "from": "角色A",
      "to": "角色B",
      "relation": "关系描述"
    }}
  ]
}}
```

注意：
- 同一角色在不同章节中出现时，合并为一条记录
- 角色描述应综合所有章节的信息
- 去除重复角色
- 按角色重要性排序"""


# ============================================================
# 剧本生成提示词
# ============================================================

SCREENPLAY_GENERATION_SYSTEM = """你是一位专业的编剧。你的任务是根据Story Bible和章节分析，生成结构化的YAML格式剧本。

你必须严格按照指定的JSON格式输出，不要添加任何额外文字。

输出的JSON将被自动转换为YAML格式的剧本文件。"""

SCREENPLAY_GENERATION_PROMPT = """根据以下Story Bible和章节分析，生成结构化剧本。

## Story Bible

{story_bible}

## 章节分析

{chapter_analyses}

## 输出要求

请以JSON格式输出完整的结构化剧本：

```json
{{
  "schema_version": "1.0.0",
  "title": "剧本标题",
  "language": "zh-CN",
  "generated_at": "2026-06-07T00:00:00Z",
  "source": {{
    "chapter_count": {chapter_count},
    "chapters": [
      {{"index": 1, "title": "第一章标题"}},
      {{"index": 2, "title": "第二章标题"}}
    ]
  }},
  "logline": "一句话故事梗概",
  "themes": ["主题1"],
  "characters": [
    {{
      "name": "角色名",
      "role": "protagonist",
      "description": "角色描述",
      "first_seen_scene": "S001"
    }}
  ],
  "acts": [
    {{
      "id": "A1",
      "title": "第一幕",
      "purpose": "建置",
      "scenes": [
        {{
          "id": "S001",
          "title": "场景标题",
          "location": "地点",
          "time": "时间",
          "source_chapter": 1,
          "characters": ["角色名"],
          "summary": "场景概要",
          "blocks": [
            {{"type": "action", "text": "动作描写"}},
            {{"type": "dialogue", "character": "角色名", "text": "台词内容"}},
            {{"type": "dialogue", "character": "角色名", "parenthetical": "低声", "text": "台词内容"}},
            {{"type": "transition", "text": "转场描述"}}
          ]
        }}
      ]
    }}
  ],
  "structure_map": {{
    "model": "five_point_map",
    "beats": [
      {{"id": "opening_image", "label": "开场意象", "scene_id": "S001", "summary": "..."}},
      {{"id": "inciting_incident", "label": "诱发事件", "scene_id": "S002", "summary": "..."}},
      {{"id": "midpoint", "label": "中点转折", "scene_id": "S003", "summary": "..."}},
      {{"id": "climax", "label": "高潮", "scene_id": "S004", "summary": "..."}},
      {{"id": "resolution", "label": "结局", "scene_id": "S005", "summary": "..."}}
    ]
  }}
}}
```

重要规则：
1. 每个场景的blocks必须至少包含1个action或dialogue
2. dialogue类型的block必须有character字段
3. scene id格式为S001、S002...（三位数字）
4. act id格式为A1、A2...
5. source_chapter对应原文章节序号
6. 将小说的叙述性描写转换为动作描写（action）
7. 将小说的对话转换为剧本对话格式（dialogue）
8. 根据情节发展划分幕和场景"""


# ============================================================
# 辅助函数
# ============================================================

def get_chapter_analysis_messages(chapter_content: str) -> list:
    """
    构建章节分析的API消息列表。

    Args:
        chapter_content: 章节文本内容

    Returns:
        OpenAI格式的消息列表
    """
    return [
        {"role": "system", "content": CHAPTER_ANALYSIS_SYSTEM},
        {"role": "user", "content": CHAPTER_ANALYSIS_PROMPT.format(chapter_content=chapter_content)},
    ]


def get_story_bible_messages(chapter_analyses: list) -> list:
    """
    构建Story Bible合并的API消息列表。

    Args:
        chapter_analyses: 各章分析结果列表

    Returns:
        OpenAI格式的消息列表
    """
    # 格式化各章分析
    analyses_text = ""
    for i, analysis in enumerate(chapter_analyses, 1):
        analyses_text += f"\n### 第{i}章分析\n```json\n{json.dumps(analysis, ensure_ascii=False, indent=2)}\n```\n"

    return [
        {"role": "system", "content": STORY_BIBLE_SYSTEM},
        {"role": "user", "content": STORY_BIBLE_PROMPT.format(chapter_analyses=analyses_text)},
    ]


def get_screenplay_generation_messages(
    story_bible: dict,
    chapter_analyses: list,
    chapter_count: int,
) -> list:
    """
    构建剧本生成的API消息列表。

    Args:
        story_bible: Story Bible数据
        chapter_analyses: 各章分析结果
        chapter_count: 原文章节数

    Returns:
        OpenAI格式的消息列表
    """
    analyses_text = ""
    for i, analysis in enumerate(chapter_analyses, 1):
        analyses_text += f"\n### 第{i}章\n```json\n{json.dumps(analysis, ensure_ascii=False, indent=2)}\n```\n"

    return [
        {"role": "system", "content": SCREENPLAY_GENERATION_SYSTEM},
        {"role": "user", "content": SCREENPLAY_GENERATION_PROMPT.format(
            story_bible=json.dumps(story_bible, ensure_ascii=False, indent=2),
            chapter_analyses=analyses_text,
            chapter_count=chapter_count,
        )},
    ]


def extract_json_from_response(response_text: str) -> dict:
    """
    从AI响应中提取JSON数据（robust解析）。

    Args:
        response_text: AI返回的文本

    Returns:
        解析后的字典，解析失败返回None
    """
    import re

    # 尝试直接解析
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # 尝试提取```json代码块
    json_match = re.search(r"```json\s*\n?(.*?)\n?\s*```", response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试提取{...}或[...]（贪婪匹配最外层）
    brace_match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    return None


# 测试代码
if __name__ == "__main__":
    # 测试消息构建
    messages = get_chapter_analysis_messages("第一章 风起\n那年春天，李明站在窗前。")
    print("章节分析消息:")
    print(f"  角色数: {len(messages)}")
    print(f"  系统提示长度: {len(messages[0]['content'])} 字")
    print(f"  用户提示长度: {len(messages[1]['content'])} 字")
    print()

    # 测试JSON提取
    test_responses = [
        '{"name": "test"}',
        '```json\n{"name": "test"}\n```',
        '这是分析结果：\n{"name": "test"}\n以上是结果。',
        '无效的响应',
    ]
    print("JSON提取测试:")
    for resp in test_responses:
        result = extract_json_from_response(resp)
        print(f"  '{resp[:30]}...' -> {'成功' if result else '失败'}")
