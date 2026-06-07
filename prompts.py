"""
提示词模板模块

包含各阶段的AI提示词模板：
- 章节分析：提取角色、场景、情节
- Story Bible合并：合并多章分析结果
- 剧本生成：输出符合Schema的结构化剧本
"""

import json

# ============================================================
# 章节分析提示词（优化版）
# ============================================================

CHAPTER_ANALYSIS_SYSTEM = """你是一位AI原生影视系统架构师，擅长将小说编译为可被AI视频、AI动画、AI分镜系统直接消费的结构化影视数据。

核心原则：
1. 严格按JSON格式输出，不要添加任何额外文字
2. 角色名保持原文一致，不要翻译或改写
3. 对话必须原文保留，不要改写或省略
4. 所有内容必须可拍摄、可视化、可镜头化、可表演
5. 禁止文学修辞、长篇心理描写、抽象抒情
6. 动作描写必须是"可被摄像机观察到的内容"

错误："他感到无尽悲凉"
正确："他沉默站在雨中，手缓缓握紧"""

CHAPTER_ANALYSIS_PROMPT = """请将以下小说章节转化为剧本结构化信息。

## 章节内容

{chapter_content}

## 输出格式

```json
{{
  "chapter_summary": "本章核心情节概述（50字以内，突出冲突和转折）",
  "characters": [
    {{
      "name": "角色名（原文）",
      "role": "protagonist/antagonist/supporting/minor/background",
      "description": "外貌特征 + 性格特点 + 身份背景 + 核心动机",
      "appearance": {{
        "age": "年龄或年龄段",
        "build": "体型",
        "hair": "发型发色",
        "eyes": "眼睛特征",
        "clothing": "标志性服装",
        "visual_symbol": "视觉符号（如：碧绿大袍、血色瞳孔）",
        "color_palette": "主色调（如：翠绿+暗红）"
      }},
      "personality": {{
        "core_traits": ["性格特征1", "性格特征2"],
        "contradictions": "内在矛盾",
        "emotional_mask": "外在表现vs内在真实"
      }},
      "dialogue_sample": "该角色的一句代表性台词原文"
    }}
  ],
  "scenes": [
    {{
      "title": "场景标题（动词+名词，如「方源自爆」「兄弟对话」）",
      "location": "具体地点（含空间特征）",
      "time": "具体时间（白天/夜晚/清晨/黄昏 + 光线描述）",
      "atmosphere": "场景氛围（紧张/温馨/压抑/肃杀等 + 环境声音/气味/温度）",
      "cinematic_style": {{
        "pacing": "节奏（slow/medium/fast）",
        "camera_language": "主要镜头语言（如：大量特写、缓慢推镜）",
        "visual_density": "视觉密度（sparse/balanced/dense）"
      }},
      "emotional_progression": {{
        "start": "场景开始时的情绪",
        "middle": "场景中间的情绪",
        "end": "场景结束时的情绪"
      }},
      "characters": ["出场角色名"],
      "props": ["重要道具或物品"],
      "summary": "场景核心事件（30字以内）",
      "visual_memory_point": "本场景的视觉记忆点（如：血滴落在青石台阶）"
    }}
  ],
  "dialogues": [
    {{
      "character": "说话角色名",
      "text": "台词原文（完整保留，不要改写）",
      "context": "说话时的动作/情绪/状态",
      "target": "对话对象（如果有）"
    }}
  ],
  "actions": [
    {{
      "character": "执行动作的角色",
      "description": "可拍摄的动作描述（去掉心理描写，保留视觉动作）",
      "significance": "这个动作的戏剧意义"
    }}
  ],
  "plot_points": [
    "关键情节点1（冲突/转折/决定）",
    "关键情节点2"
  ],
  "emotional_arc": "本章情绪走向（如：紧张→绝望→释然）"
}}
```

## 转换规则

### 对话转换
- 小说对话原文 → 保持不变，放入dialogues
- 心理独白（他想、他心中暗道）→ 不放入dialogues，放入actions的description
- 对话中的动作描写（他笑着说）→ 拆分：台词放text，动作放context

### 动作转换
- 心理描写（他感到悲伤）→ 转化为可拍摄动作（他的眼眶泛红，声音哽咽）
- 环境描写（夕阳西下）→ 放入scene的atmosphere
- 回忆/闪回 → 单独场景，标注time为「闪回」

### 角色提取
- 有台词的角色 → 必须提取
- 有重要动作的角色 → 必须提取
- 仅被提及但未出场 → 不提取
- 群体角色（群雄、众人）→ 用「群像」标注

### 场景划分
- 地点变化 → 新场景
- 时间跳跃 → 新场景
- 角色组合变化 → 可能新场景
- 每个场景必须有明确的地点和时间"""


# ============================================================
# Story Bible合并提示词（优化版）
# ============================================================

STORY_BIBLE_SYSTEM = """你是一位AI原生影视系统架构师，负责维护长篇叙事的连续性和一致性。你的任务是合并多章分析结果，构建全局Story Bible。

核心原则：
1. 同一角色在不同章节中必须合并为一条记录
2. 角色视觉特征必须固定（发型、配色、轮廓、视觉符号），确保AI角色一致性
3. 人物关系要明确（血缘、师徒、敌对、盟友等）
4. 地点要有空间描述和氛围特征
5. 维护世界观一致性（时代、力量体系、社会结构）
6. 追踪连续性状态（伤势、情绪、物品、关系变化）"""

STORY_BIBLE_PROMPT = """请将以下多章分析结果合并为一份全局Story Bible。

## 各章分析结果

{chapter_analyses}

## 输出格式

```json
{{
  "title": "故事标题（从内容推断，要有文学性）",
  "logline": "一句话故事梗概（30字以内，包含主角、目标、冲突）",
  "themes": ["核心主题1", "核心主题2"],
  "genre": "类型（玄幻/武侠/都市/历史等）",
  "world": {{
    "era": "时代背景",
    "power_system": "力量体系（如果有）",
    "social_structure": "社会结构",
    "geography": "地理环境",
    "visual_style": "视觉风格（如：东方古典+暗黑奇幻）"
  }},
  "characters": [
    {{
      "name": "角色名",
      "role": "protagonist/antagonist/supporting/minor/background",
      "description": "综合描述（外貌+性格+背景+动机+弧线）",
      "first_seen_chapter": 1,
      "key_traits": ["性格特征1", "性格特征2"],
      "visual_identity": {{
        "silhouette": "轮廓描述（用于AI角色一致性）",
        "color_palette": "主色调",
        "visual_symbol": "标志性视觉符号"
      }},
      "relationships": [
        {{"with": "其他角色名", "relation": "关系描述"}}
      ],
      "continuity_rules": {{
        "must_keep": ["必须保持的特征"],
        "forbidden": ["禁止的变化"]
      }}
    }}
  ],
  "locations": [
    {{
      "name": "地点名",
      "description": "空间描述和氛围",
      "significance": "剧情意义",
      "visual_style": "视觉风格描述",
      "chapters": [1, 2]
    }}
  ],
  "timeline": [
    {{
      "chapter": 1,
      "events": ["关键事件1", "关键事件2"]
    }}
  ],
  "conflicts": [
    {{
      "type": "核心冲突类型（人vs人/人vs自我/人vs命运）",
      "description": "冲突描述",
      "characters": ["相关角色"]
    }}
  ],
  "foreshadowing": ["伏笔1", "伏笔2"]
}}
```

## 合并规则

### 角色去重
- 名字相同 → 合并为一条
- 同一人的不同称呼（方源/方老魔/魔头）→ 合并，主名为原文名字
- 描述互补 → 综合所有章节的描述

### 关系建立
- 对话对象 → 可能有关系
- 共同出场 → 可能有关系
- 明确的称呼（兄弟、师徒）→ 确定关系

### 时间线
- 按章节顺序排列
- 标注关键转折点"""


# ============================================================
# 剧本生成提示词（优化版）
# ============================================================

SCREENPLAY_GENERATION_SYSTEM = """你是一位AI原生影视系统架构师，将小说编译为可被AI视频、AI动画、AI分镜系统直接消费的结构化影视数据。

核心原则：
1. 严格按JSON格式输出
2. 对话保持原文，不要改写
3. 所有动作必须是"可被摄像机观察到的内容"，禁止抽象描写
4. 场景标题必须是 INT./EXT. 地点 - 时间 格式
5. 每个场景必须有情绪变化（禁止静态场景）
6. 每个场景必须有视觉记忆点
7. 重要场景需包含镜头设计
8. 心理描写转为画外音(V.O.)或转化为可观察动作

错误："他很愤怒" / "气氛压抑"
正确："他猛地站起，椅子向后翻倒" / "所有人缓缓后退一步" """

SCREENPLAY_GENERATION_PROMPT = """根据以下Story Bible和章节分析，生成专业剧本。

## Story Bible

{story_bible}

## 章节分析

{chapter_analyses}

## 输出格式

```json
{{
  "schema_version": "1.0.0",
  "title": "剧本标题",
  "language": "zh-CN",
  "generated_at": "2026-06-07T00:00:00Z",
  "source": {{
    "chapter_count": {chapter_count},
    "chapters": [
      {{"index": 1, "title": "章节标题"}}
    ]
  }},
  "logline": "一句话故事梗概",
  "themes": ["主题1"],
  "characters": [
    {{
      "name": "角色名",
      "role": "protagonist",
      "description": "角色描述",
      "visual_identity": {{
        "silhouette": "轮廓描述",
        "color_palette": "主色调",
        "visual_symbol": "标志性视觉符号"
      }},
      "first_seen_scene": "S001"
    }}
  ],
  "acts": [
    {{
      "id": "A1",
      "title": "幕标题",
      "purpose": "戏剧目的（建置/对抗/解决/转折）",
      "scenes": [
        {{
          "id": "S001",
          "heading": "INT./EXT. 地点 - 时间",
          "title": "场景标题",
          "location": "具体地点",
          "time": "具体时间",
          "atmosphere": "场景氛围（光线+声音+气味+温度）",
          "cinematic_style": {{
            "pacing": "slow/medium/fast",
            "camera_language": "主要镜头语言",
            "visual_density": "sparse/balanced/dense"
          }},
          "emotional_progression": {{
            "start": "开始情绪",
            "middle": "中间情绪",
            "end": "结束情绪"
          }},
          "visual_memory_point": "本场景的视觉记忆点",
          "source_chapter": 1,
          "characters": ["角色名"],
          "summary": "场景概要",
          "blocks": [
            {{
              "type": "transition",
              "text": "FADE IN:"
            }},
            {{
              "type": "action",
              "text": "可拍摄的动作描述（现在时态，只写视觉+听觉）"
            }},
            {{
              "type": "dialogue",
              "character": "角色名",
              "text": "台词原文"
            }},
            {{
              "type": "dialogue",
              "character": "角色名",
              "parenthetical": "简短情绪提示",
              "text": "台词原文"
            }},
            {{
              "type": "voice_over",
              "character": "角色名",
              "text": "内心独白转为画外音"
            }},
            {{
              "type": "transition",
              "text": "CUT TO:"
            }}
          ]
        }}
      ]
    }}
  ],
  "structure_map": {{
    "model": "five_point_map",
    "beats": [
      {{"id": "opening_image", "label": "开场意象", "scene_id": "S001", "summary": "..." }},
      {{"id": "inciting_incident", "label": "诱发事件", "scene_id": "S002", "summary": "..." }},
      {{"id": "midpoint", "label": "中点转折", "scene_id": "S003", "summary": "..." }},
      {{"id": "climax", "label": "高潮", "scene_id": "S004", "summary": "..." }},
      {{"id": "resolution", "label": "结局", "scene_id": "S005", "summary": "..." }}
    ]
  }},
  "story_bible": {{
    "characters": [
      {{"name": "角色名", "role": "protagonist", "continuity_note": "连续性注意事项"}}
    ],
    "locations": [
      {{"name": "地点名", "note": "描述", "scene_ids": ["S001"]}}
    ]
  }}
}}
```

## 幕结构规则

### 幕划分原则
- 第一幕（建置）：建立世界观、介绍角色、引发冲突
- 第二幕（对抗）：冲突升级、角色成长、转折点
- 第三幕（解决）：高潮、结局、新平衡

### 场景划分原则
- 每个场景有明确的戏剧目标
- 场景长度适中（不要太长，3-5个blocks为宜）
- 场景结尾要有钩子（悬念/情感/冲突）

### 场景标题格式（heading）
- 必须是 `INT. 地点 - 时间` 或 `EXT. 地点 - 时间` 格式
- INT. = 室内，EXT. = 室外
- 时间：DAY/NIGHT/MORNING/EVENING/DAWN/DUSK/CONTINUOUS
- 示例：`EXT. 魔窟山崖 - DUSK`、`INT. 古月山寨祠堂 - NIGHT`

### Block编写规则

**transition（转场）**：
- 每个场景第一个block必须是transition
- 开场：FADE IN:
- 场景切换：CUT TO:
- 时间流逝：DISSOLVE TO:
- 结尾：FADE OUT.

**action（动作）**：
- 必须可拍摄（摄影机能拍到的）
- 用现在时态（他转身，不是他转了身）
- 去掉心理描写（他想、他感到、他心中暗道）
- 保留视觉动作（他转身、他握紧拳头、他的眼眶泛红）
- 包含环境细节（光线、声音、道具）

**dialogue（对话）**：
- 保持原文，不要改写
- parenthetical提示情绪（低声、愤怒、颤抖）
- 每句对话不超过50字
- 对话中的动作提示放在parenthetical中

**voice_over（画外音）**：
- 用于表达内心独白
- 心理描写（他想、他心中暗道）→ 转为voice_over
- 格式：角色名 + (V.O.) + 内心独白文本
- 回忆/闪回的旁白也用voice_over"""



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

    # 验证prompt内容
    print("\n优化验证:")
    print(f"  few-shot示例: {'示例' in CHAPTER_ANALYSIS_PROMPT or 'example' in CHAPTER_ANALYSIS_PROMPT.lower()}")
    print(f"  对话转换规则: {'对话转换' in CHAPTER_ANALYSIS_PROMPT}")
    print(f"  动作转换规则: {'动作转换' in CHAPTER_ANALYSIS_PROMPT}")
    print(f"  场景氛围要求: {'atmosphere' in CHAPTER_ANALYSIS_PROMPT}")
    print(f"  角色描述要求: {'appearance' in CHAPTER_ANALYSIS_PROMPT}")
    print(f"  五点结构: {'five_point' in SCREENPLAY_GENERATION_PROMPT}")
    print(f"  幕结构规则: {'幕划分原则' in SCREENPLAY_GENERATION_PROMPT}")
