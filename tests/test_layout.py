from __future__ import annotations

import unittest

from mindmap.layout import (
    MARGIN,
    MAX_WIDTH,
    MIN_WIDTH,
    NODE_HEIGHT,
    layout_tree,
    measure_text,
    node_width,
)
from mindmap.parser import parse_outline


class LayoutTest(unittest.TestCase):
    def test_single_node(self) -> None:
        layout = layout_tree(parse_outline("根\n"))
        self.assertEqual(len(layout.boxes), 1)
        box = layout.boxes[0]
        self.assertEqual(box.parent, -1)
        self.assertEqual(box.x, MARGIN)
        self.assertEqual(box.y, MARGIN + NODE_HEIGHT / 2)
        self.assertGreaterEqual(box.width, MIN_WIDTH)
        self.assertAlmostEqual(layout.height, NODE_HEIGHT + MARGIN * 2)

    def test_depth_moves_right(self) -> None:
        layout = layout_tree(parse_outline("根\n  子\n    孙\n"))
        root, child, grandchild = layout.boxes
        self.assertGreater(child.x, root.x + root.width)
        self.assertGreater(grandchild.x, child.x + child.width)

    def test_parent_centered_between_children(self) -> None:
        layout = layout_tree(parse_outline("根\n  子1\n  子2\n  子3\n"))
        root = layout.boxes[0]
        children = layout.boxes[1:]
        self.assertAlmostEqual(
            root.y, (children[0].y + children[-1].y) / 2
        )

    def test_siblings_do_not_overlap(self) -> None:
        text = "根\n" + "".join("  子%d\n    孙%d\n" % (i, i) for i in range(4))
        layout = layout_tree(parse_outline(text))
        by_depth = {}
        for box in layout.boxes:
            by_depth.setdefault(box.depth, []).append(box)
        for boxes in by_depth.values():
            ordered = sorted(boxes, key=lambda item: item.y)
            for first, second in zip(ordered, ordered[1:]):
                self.assertGreaterEqual(second.y - first.y, NODE_HEIGHT)

    def test_boxes_inside_canvas(self) -> None:
        layout = layout_tree(parse_outline("根\n" + "".join("  子%d\n" % i for i in range(8))))
        for box in layout.boxes:
            self.assertGreaterEqual(box.x, 0)
            self.assertGreaterEqual(box.y - box.height / 2, 0)
            self.assertLessEqual(box.x + box.width, layout.width)
            self.assertLessEqual(box.y + box.height / 2, layout.height)

    def test_deterministic(self) -> None:
        text = "根\n  子1\n    孙1\n  子2\n"
        first = layout_tree(parse_outline(text))
        second = layout_tree(parse_outline(text))
        self.assertEqual(
            [(box.x, box.y) for box in first.boxes],
            [(box.x, box.y) for box in second.boxes],
        )

    def test_measure_text(self) -> None:
        self.assertGreater(measure_text("中"), measure_text("a"))
        self.assertGreater(measure_text("A"), measure_text("a"))
        self.assertGreater(measure_text("ab"), measure_text("a"))

    def test_node_width_limits(self) -> None:
        self.assertEqual(node_width("a"), MIN_WIDTH)
        self.assertEqual(node_width("字" * 40), MAX_WIDTH)


if __name__ == "__main__":
    unittest.main()
