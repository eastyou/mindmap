"""解析缩进大纲，构建节点树。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

MAX_NODES = 300
MAX_DEPTH = 6
MAX_TEXT = 20
_BULLETS = ("- ", "* ", "• ")


class MindmapError(ValueError):
    """大纲格式或参数不合法。"""


@dataclass
class Node:
    """思维导图节点。"""

    text: str
    children: List["Node"] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return 1 + sum(child.node_count for child in self.children)

    @property
    def max_depth(self) -> int:
        if not self.children:
            return 0
        return 1 + max(child.max_depth for child in self.children)


def parse_outline(text: str) -> Node:
    """把缩进大纲解析成树；缩进单位由第一条缩进行决定。"""
    if not text.strip():
        raise MindmapError("大纲内容为空")

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    root: Optional[Node] = None
    stack: List[Node] = []
    unit = 0
    previous_depth = 0
    count = 0

    for line_number, raw in enumerate(lines, start=1):
        if not raw.strip():
            continue

        leading = raw[: len(raw) - len(raw.lstrip(" \t"))]
        if " " in leading and "\t" in leading:
            raise MindmapError(
                "第 %d 行: 缩进混用了空格和制表符，请统一使用一种" % line_number
            )
        indent = len(leading.expandtabs(4))

        content = raw.strip()
        for bullet in _BULLETS:
            if content.startswith(bullet):
                content = content[len(bullet) :].strip()
                break
        if content in ("-", "*", "•"):
            content = ""
        if not content:
            raise MindmapError("第 %d 行: 节点内容不能为空" % line_number)
        if len(content) > MAX_TEXT:
            raise MindmapError(
                "第 %d 行: 节点文字最多 %d 个字，请再精简一些"
                % (line_number, MAX_TEXT)
            )

        if root is None:
            if indent != 0:
                raise MindmapError("第 %d 行: 第一行必须是根节点，不能缩进" % line_number)
            root = Node(content)
            stack = [root]
            count = 1
            previous_depth = 0
            continue

        if indent == 0:
            raise MindmapError("第 %d 行: 只能有一个根节点" % line_number)

        if unit == 0:
            unit = indent
        if indent % unit != 0:
            raise MindmapError(
                "第 %d 行: 缩进不一致，请统一使用 %d 个空格" % (line_number, unit)
            )

        depth = indent // unit
        if depth > previous_depth + 1:
            raise MindmapError(
                "第 %d 行: 缩进跳级了，最多比上一行多一级" % line_number
            )
        if depth > MAX_DEPTH:
            raise MindmapError("第 %d 行: 层级过深，最多 %d 级" % (line_number, MAX_DEPTH))

        count += 1
        if count > MAX_NODES:
            raise MindmapError("节点过多，最多支持 %d 个" % MAX_NODES)

        node = Node(content)
        stack[depth - 1].children.append(node)
        del stack[depth:]
        stack.append(node)
        previous_depth = depth

    if root is None:
        raise MindmapError("大纲内容为空")
    return root
