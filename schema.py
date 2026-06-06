"""
Schema定义与校验模块

负责加载JSON Schema文件并提供剧本数据校验功能。
"""

import json
import os
from typing import Tuple, List, Optional

from jsonschema import validate, ValidationError

# Schema文件路径
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schemas", "screenplay.schema.json")

# 缓存加载的Schema
_schema_cache = None


def load_schema() -> dict:
    """
    加载JSON Schema文件。

    Returns:
        Schema字典
    """
    global _schema_cache
    if _schema_cache is None:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            _schema_cache = json.load(f)
    return _schema_cache


def validate_screenplay(data: dict) -> Tuple[bool, List[str]]:
    """
    校验剧本数据是否符合Schema。

    Args:
        data: 剧本数据字典

    Returns:
        (is_valid, errors) 元组
        - is_valid: 是否通过校验
        - errors: 错误信息列表（空列表表示通过）
    """
    schema = load_schema()
    errors = []

    try:
        validate(instance=data, schema=schema)
        return True, []
    except ValidationError as e:
        # 收集所有错误路径
        error_msg = _format_error(e)
        errors.append(error_msg)
        return False, errors
    except Exception as e:
        errors.append(f"校验异常: {str(e)}")
        return False, errors


def validate_screenplay_full(data: dict) -> Tuple[bool, List[str]]:
    """
    完整校验剧本数据，收集所有错误（而非第一个就停止）。

    Args:
        data: 剧本数据字典

    Returns:
        (is_valid, errors) 元组
    """
    from jsonschema import Draft202012Validator

    schema = load_schema()
    validator = Draft202012Validator(schema)
    errors = []

    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        error_msg = _format_error(error)
        errors.append(error_msg)

    return len(errors) == 0, errors


def _format_error(error: ValidationError) -> str:
    """
    格式化校验错误信息。

    Args:
        error: ValidationError对象

    Returns:
        格式化的错误字符串
    """
    # 构建路径
    path = " → ".join(str(p) for p in error.absolute_path) if error.absolute_path else "根节点"

    # 简化错误信息
    msg = error.message
    if len(msg) > 100:
        msg = msg[:100] + "..."

    return f"[{path}] {msg}"


def get_schema_summary() -> dict:
    """
    获取Schema摘要信息。

    Returns:
        包含字段信息的字典
    """
    schema = load_schema()
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    fields = []
    for name, prop in properties.items():
        fields.append({
            "name": name,
            "type": prop.get("type", "unknown"),
            "required": name in required,
            "description": prop.get("description", ""),
        })

    return {
        "title": schema.get("title", ""),
        "total_fields": len(fields),
        "required_count": len(required),
        "fields": fields,
    }


# 测试代码
if __name__ == "__main__":
    # 测试加载Schema
    schema = load_schema()
    print(f"Schema加载成功: {schema['title']}")
    print(f"必填字段: {schema['required']}")
    print()

    # 测试合法数据
    valid_data = {
        "schema_version": "1.0.0",
        "title": "测试剧本",
        "language": "zh-CN",
        "generated_at": "2026-06-07T00:00:00Z",
        "source": {
            "chapter_count": 3,
            "chapters": [
                {"index": 1, "title": "第一章"},
                {"index": 2, "title": "第二章"},
                {"index": 3, "title": "第三章"},
            ]
        },
        "characters": [
            {
                "name": "主角",
                "role": "protagonist",
                "description": "故事主角",
                "first_seen_scene": "S001"
            }
        ],
        "acts": [
            {
                "id": "A1",
                "title": "第一幕",
                "purpose": "建置",
                "scenes": [
                    {
                        "id": "S001",
                        "title": "开场",
                        "location": "城市",
                        "time": "白天",
                        "characters": ["主角"],
                        "blocks": [
                            {"type": "action", "text": "主角走在街上"}
                        ]
                    }
                ]
            }
        ]
    }

    is_valid, errors = validate_screenplay(valid_data)
    print(f"合法数据校验: {'通过 ✓' if is_valid else '失败 ✗'}")
    if errors:
        for e in errors:
            print(f"  - {e}")

    # 测试非法数据（缺少必填字段）
    invalid_data = {
        "title": "测试剧本",
        # 缺少 schema_version, language, generated_at, source, characters, acts
    }

    is_valid, errors = validate_screenplay(invalid_data)
    print(f"\n非法数据校验: {'通过 ✓' if is_valid else '失败 ✗'}")
    if errors:
        for e in errors:
            print(f"  - {e}")

    # 测试Schema摘要
    summary = get_schema_summary()
    print(f"\nSchema摘要:")
    print(f"  总字段数: {summary['total_fields']}")
    print(f"  必填字段: {summary['required_count']}")
    for f in summary['fields']:
        req = "必填" if f['required'] else "可选"
        print(f"  - {f['name']}: {f['type']} ({req}) - {f['description']}")
