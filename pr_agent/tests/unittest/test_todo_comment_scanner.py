import pytest
from pr_agent.tools.todo_comment_scanner import TODOCommentScanner

SAMPLE_DIFF = """\
diff --git a/foo.py b/foo.py
--- a/foo.py
+++ b/foo.py
@@ -1 +1,2 @@
 def fn():
+    # TODO: handle error
"""


def test_scan_detects_todo():
    scanner = TODOCommentScanner(["TODO"])
    assert scanner.scan(SAMPLE_DIFF) == ["foo.py:2 — # TODO: handle error"]


def test_scan_ignores_non_added_todo():
    diff = SAMPLE_DIFF.replace("+    # TODO", "     # TODO")
    assert TODOCommentScanner(["TODO"]).scan(diff) == []
