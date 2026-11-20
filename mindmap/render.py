"""把布局结果渲染成可打印的 HTML + 内嵌 SVG。"""

from __future__ import annotations

import html
from typing import List, Tuple

from .layout import Layout, layout_tree
from .parser import MindmapError, Node

LEVEL_STYLES: Tuple[Tuple[str, str, str], ...] = (
    ("#0f172a", "#0f172a", "#ffffff"),
    ("#e0f2fe", "#0284c7", "#0c4a6e"),
    ("#dcfce7", "#16a34a", "#14532d"),
    ("#fef3c7", "#d97706", "#78350f"),
    ("#ede9fe", "#7c3aed", "#4c1d95"),
    ("#ffe4e6", "#e11d48", "#881337"),
    ("#f1f5f9", "#64748b", "#0f172a"),
)

_FONT_STACK = (
    "'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', "
    "'Source Han Sans SC', sans-serif"
)

PAGE_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 20px 22px 24px;
    background: #f8fafc;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
  }
  header { margin-bottom: 12px; }
  h1 { font-size: 23px; margin: 0 0 5px; letter-spacing: 0.5px; }
  .sub { color: #64748b; font-size: 12px; }
  .canvas {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px;
    overflow: auto;
  }
  svg.map { display: block; width: 100%; height: auto; }
  footer { color: #94a3b8; font-size: 11px; margin-top: 10px; }
  @page { size: A4 landscape; margin: 8mm; }
  @media print {
    body { background: #fff; padding: 0; }
    header { margin-bottom: 8px; }
    .canvas { border: none; border-radius: 0; padding: 0; overflow: visible; }
    svg.map { max-height: 172mm; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <div class="sub">__SUMMARY__ · 由缩进大纲生成</div>
</header>
<div class="canvas">
__SVG__
</div>
<footer>mindmap · 用两个空格或四个空格表示层级，节点文字尽量精简</footer>
</body>
</html>
"""


def _svg(layout: Layout, label: str) -> str:
    parts: List[str] = [
        '<svg class="map" viewBox="0 0 %.0f %.0f" role="img" aria-label="%s">'
        % (layout.width, layout.height, html.escape(label))
    ]

    for box in layout.boxes:
        if box.parent < 0:
            continue
        parent = layout.boxes[box.parent]
        start_x = parent.x + parent.width
        start_y = parent.y
        end_x = box.x
        end_y = box.y
        middle = (start_x + end_x) / 2
        parts.append(
            '<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
            'fill="none" stroke="#94a3b8" stroke-width="1.6" />'
            % (
                start_x,
                start_y,
                middle,
                start_y,
                middle,
                end_y,
                end_x,
                end_y,
            )
        )

    for box in layout.boxes:
        fill, stroke, text_color = LEVEL_STYLES[box.depth % len(LEVEL_STYLES)]
        top = box.y - box.height / 2
        parts.append(
            '<g><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" '
            'fill="%s" stroke="%s" stroke-width="1.5" />'
            '<text x="%.1f" y="%.1f" text-anchor="middle" '
            'dominant-baseline="middle" font-family="%s" font-size="14" '
            'fill="%s">%s</text></g>'
            % (
                box.x,
                top,
                box.width,
                box.height,
                fill,
                stroke,
                box.x + box.width / 2,
                box.y,
                _FONT_STACK,
                text_color,
                html.escape(box.text),
            )
        )

    parts.append("</svg>")
    return "".join(parts)


def render_page(root: Node, title: str = "思维导图") -> str:
    """生成整页 HTML；标题为空时抛 ``MindmapError``。"""
    if not title.strip():
        raise MindmapError("思维导图标题不能为空")
    layout = layout_tree(root)
    page = PAGE_TEMPLATE
    replacements = {
        "__TITLE__": html.escape(title.strip()),
        "__SUMMARY__": "%d 个节点 · %d 层"
        % (root.node_count, root.max_depth + 1),
        "__SVG__": _svg(layout, title.strip()),
    }
    for key, value in replacements.items():
        page = page.replace(key, value)
    return page
