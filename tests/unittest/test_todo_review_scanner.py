import pytest
from pr_agent.algo.pr_processing import get_todo_sections

SAMPLE_PATCH = """\
diff --git a/foo.py b/foo.py
--- a/foo.py
+++ b/foo.py
@@ -10,6 +10,8 @@ def fn():
     print("hello")
+    # TODO: handle edge case
+    # FIXME: cleanup
"""


def test_get_todo_sections_detects_both():
    todos = get_todo_sections(SAMPLE_PATCH, "foo.py")
    assert "foo.py:11 — # TODO: handle edge case" in todos
    assert "foo.py:12 — # FIXME: cleanup" in todos


def test_get_todo_sections_ignores_context():
    patch = SAMPLE_PATCH.replace("+    # TODO", "     # TODO")
    patch = patch.replace("+    # FIXME", "     # FIXME")
    assert get_todo_sections(patch, "foo.py") == []
