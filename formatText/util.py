
#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from .builder import generate_commands
from .constants import DEFAULT_OUTPUT_DIR

def main():
    parser = argparse.ArgumentParser(description="生成 gamerule 函数文件")
    parser.add_argument("input", help="输入 JSON 文件路径")
    parser.add_argument("--pretty", action="store_true", help="美化输出")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help=f"输出目录（默认 {DEFAULT_OUTPUT_DIR}）")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 文件 {input_path} 不存在", file=sys.stderr)
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}", file=sys.stderr)
            sys.exit(1)

    base_dir = Path(args.output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    for key, value in data.items():
        if isinstance(value, str):
            out_file = base_dir / f"{key}.mcfunction"
            commands = generate_commands(value, args.pretty)
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(commands) + '\n')
            print(f"生成: {out_file}")

        elif isinstance(value, list):
            out_dir = base_dir / key
            out_dir.mkdir(parents=True, exist_ok=True)
            for idx, item in enumerate(value, start=1):
                if not isinstance(item, str):
                    continue
                out_file = out_dir / f"{idx}.mcfunction"
                commands = generate_commands(item, args.pretty)
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(commands) + '\n')
                print(f"生成: {out_file}")
        else:
            print(f"警告: 键 '{key}' 的类型不是 str 或 list，已跳过", file=sys.stderr)

if __name__ == "__main__":
    main()