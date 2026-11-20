from __future__ import annotations

import unittest

from mindmap.parser import MindmapError, parse_outline
from mindmap.render import render_page


class RenderPageTest(unittest.TestCase):
    def test_svg_structure(self) -> None:
        root = parse_outline("根\n  子1\n  子2\n    孙\n")
        page = render_page(root, title="物理复习")
        self.assertEqual(page.count("<rect"), 4)
        self.assertEqual(page.count("<path"), 3)
        self.assertIn("<svg", page)
        self.assertIn("</svg>", page)
        self.assertIn("物理复习", page)

    def test_summary(self) -> None:
        root = parse_outline("根\n  子\n    孙\n")
        page = render_page(root)
        self.assertIn("3 个节点 · 3 层", page)

    def test_escape_text(self) -> None:
        root = parse_outline("根\n  <b>子</b>\n")
        page = render_page(root, title="<script>alert(1)</script>")
        self.assertIn("&lt;b&gt;子&lt;/b&gt;", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertNotIn("<b>子</b>", page)
        self.assertNotIn("<script>alert(1)</script>", page)

    def test_blank_title(self) -> None:
        root = parse_outline("根\n")
        with self.assertRaises(MindmapError):
            render_page(root, title="   ")

    def test_print_css(self) -> None:
        page = render_page(parse_outline("根\n"))
        self.assertIn("size: A4 landscape", page)
        self.assertIn("viewBox", page)

    def test_deterministic(self) -> None:
        text = "根\n  子1\n  子2\n"
        first = render_page(parse_outline(text))
        second = render_page(parse_outline(text))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
