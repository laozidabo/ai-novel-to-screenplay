# YAML剧本Schema设计文档

## 概述

本文档定义了AI小说转剧本工具输出的YAML结构化剧本的Schema规范。该Schema用于确保AI生成的剧本数据格式一致、可校验、可编辑。

## 设计原则

1. **面向编辑**：输出是剧本初稿，作者要能继续编辑打磨
2. **来源可追溯**：每个场景标注来自哪个原文章节
3. **结构清晰**：幕→场景→块，三层嵌套，层次分明
4. **类型明确**：动作、对话、转场、画外音分开处理
5. **可校验**：提供JSON Schema，程序可自动检查格式正确性
6. **行业对齐**：参考好莱坞标准剧本格式（INT./EXT.场景标题、动作描写、对话格式）

## 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| schema_version | string | ✓ | Schema版本号（语义化版本，如1.0.0） |
| title | string | ✓ | 剧本标题（通常从小说标题提取） |
| language | string | ✓ | 语言代码（如zh-CN） |
| generated_at | string | ✓ | 生成时间（ISO 8601格式） |
| source | object | ✓ | 原文来源信息 |
| logline | string | | 一句话故事梗概 |
| themes | array | | 主题标签列表 |
| characters | array | ✓ | 人物表 |
| acts | array | ✓ | 幕结构（剧本主体） |
| structure_map | object | | 五点结构映射 |
| story_bible | object | | 改编资料库 |
| adaptation_report | object | | 改编质量报告 |

## 设计原因

### 为什么需要schema_version？

Schema会随版本迭代 evolve，版本号确保向后兼容。使用语义化版本（major.minor.patch）便于管理变更。

### 为什么需要source？

记录原文章节数和标题，便于：
- 追溯剧本内容来自哪些章节
- 验证是否覆盖了所有章节
- 作者回查原文对比

### 为什么需要logline和themes？

- **logline**：一句话梗概是影视行业的标准做法，便于pitch和沟通
- **themes**：主题标签帮助理解故事核心，便于分类和检索

### 为什么characters是顶层字段？

角色是剧本的核心元素，独立于幕和场景。便于：
- 快速查看所有角色
- 跨场景追踪角色
- 生成角色表

## 幕结构（acts）

```yaml
acts:
  - id: "A1"
    title: "第一幕"
    purpose: "建置"
    scenes:
      - id: "S001"
        heading: "EXT. 地点 - 时间"
        ...
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| id | string | ✓ | 幕ID（A1、A2...） |
| title | string | ✓ | 幕标题 |
| purpose | string | ✓ | 戏剧目的（建置/对抗/解决） |
| scenes | array | ✓ | 场景列表 |

### 设计原因

**为什么用幕结构？**

幕（Act）是剧本的基本结构单位。经典三幕结构：
- 第一幕（建置）：建立世界观、介绍角色、引发冲突
- 第二幕（对抗）：冲突升级、角色成长、转折点
- 第三幕（解决）：高潮、结局、新平衡

幕结构帮助作者理解故事节奏和戏剧张力。

## 场景（scenes）

```yaml
scenes:
  - id: "S001"
    heading: "EXT. 魔窟山崖 - DUSK"
    title: "方源自爆"
    location: "魔窟山崖"
    time: "DUSK"
    atmosphere: "肃杀、绝望，山风吹拂，血袍飘荡"
    source_chapter: 1
    characters: ["方源", "群雄"]
    summary: "方源被围攻，自爆身亡"
    blocks: [...]
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| id | string | ✓ | 场景ID（S001、S002...） |
| heading | string | ✓ | 场景标题行（INT./EXT. 地点 - 时间） |
| title | string | | 场景标题 |
| location | string | ✓ | 场景地点 |
| time | string | ✓ | 场景时间（DAY/NIGHT/DAWN/DUSK） |
| atmosphere | string | | 场景氛围（光线、声音、温度） |
| source_chapter | integer | | 来源章节序号 |
| characters | array | ✓ | 出场角色列表 |
| summary | string | | 场景概要 |
| blocks | array | ✓ | 内容块列表 |

### 设计原因

**为什么需要heading和title两个字段？**

- **heading**：行业标准格式（`INT./EXT. 地点 - 时间`），用于正式剧本排版
- **title**：中文场景标题（如"方源自爆"），便于作者快速理解场景内容

**为什么需要atmosphere？**

场景氛围是视觉化的重要元素，包含：
- 光线（明亮/昏暗/月光）
- 声音（风声/雨声/喧嚣）
- 温度（寒冷/炎热）
- 气味（血腥/花香）

这些信息帮助导演和摄影师理解场景的视觉风格。

**为什么需要source_chapter？**

追溯场景来自哪个原文章节，便于：
- 作者对照原文检查改编质量
- 验证章节覆盖完整性

## 内容块（blocks）

```yaml
blocks:
  - type: "transition"
    text: "FADE IN:"
  - type: "action"
    text: "方源站在山巅，血袍飘荡。"
  - type: "dialogue"
    character: "方源"
    text: "青山落日，秋月春风。"
  - type: "dialogue"
    character: "方源"
    parenthetical: "低声"
    text: "终究是失败了呀。"
  - type: "voice_over"
    character: "方源"
    text: "他心中暗道：若是春秋蝉有效，来生还要做邪魔。"
  - type: "transition"
    text: "CUT TO:"
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| type | string | ✓ | 块类型（action/dialogue/transition/voice_over） |
| text | string | ✓ | 内容文本 |
| character | string | dialogue必填 | 说话角色 |
| parenthetical | string | | 括号说明（情绪/动作提示） |

### 块类型说明

| 类型 | 说明 | 格式要求 |
|------|------|---------|
| action | 动作描写 | 现在时态，只写可拍摄内容（视觉+听觉） |
| dialogue | 对话 | 原文保留，不改写 |
| transition | 转场 | FADE IN/CUT TO/DISSOLVE TO/FADE OUT |
| voice_over | 画外音 | 内心独白转为画外音(V.O.) |

### 设计原因

**为什么需要voice_over类型？**

小说中有大量心理描写（他想、他心中暗道），这些在剧本中不能直接拍出来。处理方式：
- 转为画外音(V.O.)：保留内心独白，用声音表达
- 删除：如果可以通过动作/表情表达，则删除心理描写

voice_over类型让这两种处理方式都有对应的格式。

**为什么dialogue需要parenthetical？**

parenthetical是剧本标准格式，用于提示演员：
- 情绪（低声、愤怒、颤抖）
- 动作（转身说、边走边说）
- 语气（嘲讽、真诚）

但应简短，不要过度指导演员。

## 五点结构映射（structure_map）

```yaml
structure_map:
  model: "five_point_map"
  beats:
    - id: "opening_image"
      label: "开场意象"
      scene_id: "S001"
      summary: "方源被围攻，自爆身亡"
    - id: "inciting_incident"
      label: "诱发事件"
      scene_id: "S002"
      summary: "方源重生回到五百年前"
    - id: "midpoint"
      label: "中点转折"
      scene_id: "S003"
      summary: "方源决定重走魔道"
    - id: "climax"
      label: "高潮"
      scene_id: "S004"
      summary: "开窍大典开始"
    - id: "resolution"
      label: "结局"
      scene_id: "S005"
      summary: "方源迎接新的人生"
```

### 设计原因

**为什么用五点结构？**

五点结构是好莱坞经典叙事结构：
1. **开场意象**：建立基调和世界观
2. **诱发事件**：打破平衡，引发故事
3. **中点转折**：故事方向改变
4. **高潮**：最大冲突
5. **结局**：新的平衡

这个结构帮助作者理解故事的戏剧弧线，确保剧本有完整的叙事结构。

## 改编资料库（story_bible）

```yaml
story_bible:
  characters:
    - name: "方源"
      role: "protagonist"
      continuity_note: "重生前后外貌变化，注意年龄描述"
  locations:
    - name: "古月山寨"
      note: "方源的家乡，有祠堂和高脚吊楼"
      scene_ids: ["S002", "S003"]
```

### 设计原因

**为什么需要story_bible？**

改编过程中需要维护连续性：
- 角色外貌不能前后矛盾
- 地点描述要一致
- 道具不能凭空出现

story_bible是改编的参考资料，帮助作者保持一致性。

## JSON Schema文件

完整的JSON Schema定义在 `schemas/screenplay.schema.json`，可用于：
- 自动校验AI输出是否符合格式
- IDE自动补全和提示
- 文档生成

## 使用示例

### 最小合法示例

```yaml
schema_version: "1.0.0"
title: "测试剧本"
language: "zh-CN"
generated_at: "2026-06-07T00:00:00Z"
source:
  chapter_count: 3
  chapters:
    - index: 1
      title: "第一章"
    - index: 2
      title: "第二章"
    - index: 3
      title: "第三章"
characters:
  - name: "主角"
    role: "protagonist"
    description: "故事主角"
    first_seen_scene: "S001"
acts:
  - id: "A1"
    title: "第一幕"
    purpose: "建置"
    scenes:
      - id: "S001"
        heading: "INT. 房间 - DAY"
        location: "房间"
        time: "DAY"
        characters: ["主角"]
        blocks:
          - type: "action"
            text: "主角坐在桌前。"
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-06-07 | 初始版本 |
