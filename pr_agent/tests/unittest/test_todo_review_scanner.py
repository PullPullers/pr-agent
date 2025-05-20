def test_todo_extraction():
    from pr_agent.algo.pr_processing import get_todo_sections

    dummy_patch = """\
diff --git a/sample.py b/sample.py
index e69de29..b6fc4c6 100644
--- a/sample.py
+++ b/sample.py
@@ def calculate():
+    # TODO: need to optimize this
+    # FIXME: this can cause division by zero
+    return 1 / 0
"""
    todos = get_todo_sections(dummy_patch, "sample.py")
    assert any("TODO: need to optimize this" in todo for todo in todos)
    assert any("FIXME: this can cause division by zero" in todo for todo in todos)
