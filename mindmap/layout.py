"""树布局：计算每个节点的坐标与画布尺寸。"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Dict, List

from .parser import Node

FONT_SIZE = 14.0
NODE_HEIGHT = 34.0
MARGIN = 30.0
LEVEL_GAP = 52.0
SIBLING_GAP = 12.0
MIN_WIDTH = 58.0
MAX_WIDTH = 320.0
PADDING_X = 14.0


@dataclass
class Box:
    """一个已布局的节点。"""

    text: str
    depth: int
    x: float
    y: float
    width: float
    height: float
    parent: int


@dataclass
class Layout:
    """整张图的布局结果。"""

    width: float
    height: float
    boxes: List[Box]


def measure_text(text: str, font_size: float = FONT_SIZE) -> float:
    """估算文本宽度：中日韩字符按全角，其余按半角。"""
    width = 0.0
    for char in text:
        if char == " ":
            width += font_size * 0.32
        elif unicodedata.east_asian_width(char) in ("W", "F"):
            width += font_size
        elif char.isupper():
            width += font_size * 0.68
        else:
            width += font_size * 0.56
    return width


def node_width(text: str) -> float:
    """节点宽度：文本宽度加左右内边距，并限制在合理范围内。"""
    estimated = measure_text(text) + PADDING_X * 2
    return min(MAX_WIDTH, max(MIN_WIDTH, estimated))


def layout_tree(root: Node) -> Layout:
    """对整棵树做从左到右的层级布局。"""
    boxes: List[Box] = []
    children: List[List[int]] = []

    def build(node: Node, depth: int, parent: int) -> int:
        index = len(boxes)
        boxes.append(
            Box(
                text=node.text,
                depth=depth,
                x=0.0,
                y=0.0,
                width=node_width(node.text),
                height=NODE_HEIGHT,
                parent=parent,
            )
        )
        children.append([])
        for child in node.children:
            children[index].append(build(child, depth + 1, index))
        return index

    build(root, 0, -1)

    subtree = [0.0] * len(boxes)

    def measure_subtree(index: int) -> float:
        kids = children[index]
        if not kids:
            subtree[index] = NODE_HEIGHT
            return subtree[index]
        total = sum(measure_subtree(kid) for kid in kids)
        total += SIBLING_GAP * (len(kids) - 1)
        subtree[index] = total
        return total

    measure_subtree(0)

    centers = [0.0] * len(boxes)

    def place(index: int, top: float) -> None:
        kids = children[index]
        if not kids:
            centers[index] = top + NODE_HEIGHT / 2
            return
        cursor = top
        for kid in kids:
            place(kid, cursor)
            cursor += subtree[kid] + SIBLING_GAP
        centers[index] = (centers[kids[0]] + centers[kids[-1]]) / 2

    place(0, MARGIN)

    widths: Dict[int, float] = {}
    for box in boxes:
        widths[box.depth] = max(widths.get(box.depth, 0.0), box.width)

    column_x: Dict[int, float] = {}
    cursor = MARGIN
    for depth in sorted(widths):
        column_x[depth] = cursor
        cursor += widths[depth] + LEVEL_GAP

    for index, box in enumerate(boxes):
        box.x = column_x[box.depth]
        box.y = centers[index]

    canvas_width = cursor - LEVEL_GAP + MARGIN
    canvas_height = subtree[0] + MARGIN * 2
    return Layout(width=canvas_width, height=canvas_height, boxes=boxes)
