"""命令行入口：大纲文本转思维导图页面。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .parser import MindmapError, parse_outline
from .render import render_page


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mindmap",
        description="用缩进大纲生成可打印的 SVG 思维导图",
    )
    parser.add_argument("--version", action="version", version="mindmap 0.1.0")
    parser.add_argument("-i", "--input", required=True, help="大纲文本文件")
    parser.add_argument(
        "-o", "--output", default="mindmap.html", help="输出 HTML 路径"
    )
    parser.add_argument("--title", default="思维导图", help="页面标题")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.title.strip():
        print("错误: 思维导图标题不能为空", file=sys.stderr)
        return 2

    try:
        text = Path(args.input).read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        print("错误: 找不到文件: %s" % args.input, file=sys.stderr)
        return 2
    except IsADirectoryError:
        print("错误: 这是一个目录，不是大纲文件: %s" % args.input, file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print("错误: 文件编码不是 UTF-8，请另存为 UTF-8 后重试", file=sys.stderr)
        return 2
    except OSError as exc:
        print("错误: 读取文件失败: %s" % exc, file=sys.stderr)
        return 2

    try:
        root = parse_outline(text)
        page = render_page(root, title=args.title)
    except MindmapError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2

    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    print(
        "已生成 %s：%d 个节点，%d 层"
        % (args.output, root.node_count, root.max_depth + 1)
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
