from __future__ import annotations

import unittest

from mindmap.parser import MindmapError, parse_outline


class ParseOutlineTest(unittest.TestCase):
    def test_simple_tree(self) -> None:
        root = parse_outline("根\n  子1\n  子2\n    孙\n")
        self.assertEqual(root.text, "根")
        self.assertEqual([child.text for child in root.children], ["子1", "子2"])
        self.assertEqual(root.children[1].children[0].text, "孙")
        self.assertEqual(root.node_count, 4)
        self.assertEqual(root.max_depth, 2)

    def test_bullets_are_stripped(self) -> None:
        root = parse_outline("- 根\n  * 子\n  • 另一个\n")
        self.assertEqual(root.text, "根")
        self.assertEqual([child.text for child in root.children], ["子", "另一个"])

    def test_four_space_indent(self) -> None:
        root = parse_outline("根\n    子\n        孙\n")
        self.assertEqual(root.children[0].children[0].text, "孙")

    def test_tab_indent(self) -> None:
        root = parse_outline("根\n\t子\n\t\t孙\n")
        self.assertEqual(root.max_depth, 2)

    def test_mixed_space_and_tab(self) -> None:
        with self.assertRaises(MindmapError) as context:
            parse_outline("根\n \t子\n")
        self.assertIn("混用", str(context.exception))

    def test_depth_jump(self) -> None:
        with self.assertRaises(MindmapError) as context:
            parse_outline("根\n  子\n      孙\n")
        self.assertIn("跳级", str(context.exception))

    def test_inconsistent_indent(self) -> None:
        with self.assertRaises(MindmapError) as context:
            parse_outline("根\n  子\n   孙\n")
        self.assertIn("缩进不一致", str(context.exception))

    def test_multiple_roots(self) -> None:
        with self.assertRaises(MindmapError) as context:
            parse_outline("根\n另一个\n")
        self.assertIn("只能有一个根节点", str(context.exception))

    def test_empty(self) -> None:
        with self.assertRaises(MindmapError):
            parse_outline("")
        with self.assertRaises(MindmapError):
            parse_outline("   \n\n  ")

    def test_first_line_indented(self) -> None:
        with self.assertRaises(MindmapError) as context:
            parse_outline("  根\n")
        self.assertIn("不能缩进", str(context.exception))

    def test_empty_node(self) -> None:
        with self.assertRaises(MindmapError):
            parse_outline("根\n  - \n")

    def test_text_too_long(self) -> None:
        with self.assertRaises(MindmapError) as context:
            parse_outline("根\n  " + "字" * 21 + "\n")
        self.assertIn("最多 20 个字", str(context.exception))

    def test_too_many_nodes(self) -> None:
        lines = ["根"] + ["  节点%d" % index for index in range(300)]
        with self.assertRaises(MindmapError) as context:
            parse_outline("\n".join(lines))
        self.assertIn("节点过多", str(context.exception))

    def test_too_deep(self) -> None:
        lines = ["根"]
        for depth in range(1, 8):
            lines.append(" " * (depth * 2) + "第%d层" % depth)
        with self.assertRaises(MindmapError) as context:
            parse_outline("\n".join(lines))
        self.assertIn("层级过深", str(context.exception))

    def test_blank_lines_ignored(self) -> None:
        root = parse_outline("根\n\n  子\n\n  子2\n")
        self.assertEqual(root.node_count, 3)

    def test_node_properties(self) -> None:
        root = parse_outline("根\n  子\n    孙\n  子2\n")
        self.assertEqual(root.node_count, 4)
        self.assertEqual(root.max_depth, 2)
        self.assertEqual(root.children[0].max_depth, 1)


if __name__ == "__main__":
    unittest.main()
