
import json
from parser import parse_line, strip_json_keys

def generate_commands(text: str, pretty: bool = False) -> list[str]:
    """将多行文本转换为 tellraw 命令列表，每条命令的第一个组件均为空文本（防止样式继承）"""
    lines = text.split('\n')
    commands = []
    for line in lines:
        if line == '':
            parsed = [{'text': ''}]
        else:
            parsed = parse_line(line)
            if not parsed:
                parsed = [{'text': ''}]
        # 强制以空组件开头，重置样式
        components = [{'text': ''}] + parsed

        if pretty:
            json_str = json.dumps(components, ensure_ascii=False, indent=2)
        else:
            json_str = json.dumps(components, ensure_ascii=False)
        json_str = strip_json_keys(json_str)
        commands.append(f"tellraw @s {json_str}")
    return commands