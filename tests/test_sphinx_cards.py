import os
from html.parser import HTMLParser
from importlib.metadata import version
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

QUESTIONS = """\
# Questions

::::{question} Single choice
:label: single
:showanswer:

---
[x] First choice
> First feedback
& First shown
[ ] Second choice
> Second feedback
---
::::

::::{question} Multiple choice
:label: multiple
:variant: multiple-select

---
[x] Correct choice
[ ] Wrong choice
^^^
= Overall correct
> Overall incorrect
---
::::

::::{question} Short answers
:label: blocks
:type: short-answer
:showanswer:

---
T[hello] Text label
= Text correct
> Text incorrect
& Text shown
M[x+1]
= Math correct
> Math incorrect
---
::::

::::{question} Gaps
:label: gaps
:type: short-answer
:variant: gaps

---
T[answer]
^^^
? A {gap} here.
= Gap correct
---
::::

::::{question} No input
:label: no-input
:type: no-input

---
! Informative feedback
---
::::
"""


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.elements = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element = {"tag": tag, "attrs": attrs, "parent": self.stack[-1] if self.stack else None}
        if "id" in attrs:
            self.elements[attrs["id"]] = element
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input",
                       "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(element)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1]["tag"] == tag:
            self.stack.pop()


class SphinxCardCompatibilityTest(unittest.TestCase):
    def build(self, content, legacy=None, warnings_as_errors=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = "extensions = ['myst_parser', 'sphinx_design', 'teachbooks_questions']\n"
            config += "master_doc = 'index'\nmyst_enable_extensions = ['colon_fence']\n"
            if legacy is not None:
                config += f"sd_card_legacy_separators = {legacy!r}\n"
            (root / "conf.py").write_text(config, encoding="utf-8")
            (root / "index.md").write_text(content, encoding="utf-8")
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
            command = [sys.executable, "-m", "sphinx", "-q", "-b", "html"]
            if warnings_as_errors:
                command.append("-W")
            result = subprocess.run(
                command + [str(root), str(root / "_build")],
                capture_output=True, text=True, env=env,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            html = (root / "_build" / "index.html").read_text(encoding="utf-8")
            elements = Elements()
            elements.feed(html)
            return html, elements.elements, result.stderr

    def assert_parent_class(self, elements, element_id, expected):
        parent = elements[element_id]["parent"]
        self.assertIn(expected, parent["attrs"].get("class", "").split())

    def test_questions_without_design_separator_dependency(self):
        configurations = [None]
        if tuple(int(part) for part in version("sphinx-design").split(".")[:2]) >= (0, 8):
            configurations += [True, False]
        for legacy in configurations:
            with self.subTest(legacy=legacy):
                html, elements, _ = self.build(QUESTIONS, legacy)
                for question in ("single", "multiple"):
                    for index in range(2):
                        self.assert_parent_class(elements, f"{question}-option-{index}", "sd-card-body")
                        self.assert_parent_class(elements, f"{question}-feedback-{index}", "sd-card-footer")
                        self.assert_parent_class(elements, f"{question}-show-{index}", "sd-card-footer")
                for index in range(2):
                    label = elements[f"blocks-option-{index}-label"]
                    self.assert_parent_class(elements, f"blocks-option-{index}-label", "sd-card-header")
                    self.assertEqual("hidden" in label["parent"]["attrs"]["class"].split(), index == 1)
                    self.assert_parent_class(elements, f"blocks-option-{index}-input", "sd-card-body")
                    for suffix in ("feedback", "feedback-incorrect", "feedback-show-answer",
                                   "feedback-parsing-error"):
                        self.assert_parent_class(elements, f"blocks-option-{index}-{suffix}", "sd-card-footer")
                self.assertEqual(elements["blocks-option-0-input"]["tag"], "textarea")
                self.assertEqual(elements["blocks-option-1-input"]["tag"], "math-field")
                for text in ("First feedback", "First shown", "Second feedback", "Overall correct",
                             "Overall incorrect", "Text label", "Text correct", "Text incorrect",
                             "Text shown", "Math correct", "Math incorrect", "Gap correct",
                             "Informative feedback"):
                    self.assertIn(text, html)

    def test_design_legacy_separators_remain_available(self):
        content = """\
# Card

:::{card}
Header
^^^
Body
+++
Footer
:::
"""
        legacy = True if tuple(int(part) for part in version("sphinx-design").split(".")[:2]) >= (0, 8) else None
        html, _, _ = self.build(content, legacy, warnings_as_errors=False)
        self.assertIn('class="sd-card-header', html)
        self.assertIn('class="sd-card-footer', html)
        self.assertIn("Header", html)
        self.assertIn("Footer", html)


if __name__ == "__main__":
    unittest.main()
