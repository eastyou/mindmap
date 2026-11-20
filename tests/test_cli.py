from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from mindmap.cli import main

OUTLINE = "初中物理\n  力学\n    速度\n  光学\n"


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "outline.txt"
        self.source.write_text(OUTLINE, encoding="utf-8")

    def run_cli(self, *args: str) -> tuple:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_success(self) -> None:
        output = self.root / "map.html"
        code, stdout, stderr = self.run_cli(
            "-i", str(self.source), "-o", str(output), "--title", "复习提纲"
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("4 个节点，3 层", stdout)
        text = output.read_text(encoding="utf-8")
        self.assertIn("复习提纲", text)
        self.assertIn("<svg", text)

    def test_bom_input(self) -> None:
        source = self.root / "bom.txt"
        source.write_text("\ufeff" + OUTLINE, encoding="utf-8")
        output = self.root / "map.html"
        code, _, _ = self.run_cli("-i", str(source), "-o", str(output))
        self.assertEqual(code, 0)

    def test_missing_file(self) -> None:
        code, _, stderr = self.run_cli(
            "-i", str(self.root / "absent.txt"), "-o", str(self.root / "map.html")
        )
        self.assertEqual(code, 2)
        self.assertIn("找不到文件", stderr)

    def test_bad_outline(self) -> None:
        source = self.root / "bad.txt"
        source.write_text("根\n  子\n      孙\n", encoding="utf-8")
        code, _, stderr = self.run_cli(
            "-i", str(source), "-o", str(self.root / "map.html")
        )
        self.assertEqual(code, 2)
        self.assertIn("跳级", stderr)

    def test_blank_title(self) -> None:
        code, _, stderr = self.run_cli(
            "-i",
            str(self.source),
            "-o",
            str(self.root / "map.html"),
            "--title",
            "  ",
        )
        self.assertEqual(code, 2)
        self.assertIn("标题", stderr)

    def test_write_failure(self) -> None:
        code, _, stderr = self.run_cli(
            "-i", str(self.source), "-o", str(self.root)
        )
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", stderr)


if __name__ == "__main__":
    unittest.main()
