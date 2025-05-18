from pr_agent.algo.pr_processing import get_todo_sections

patch= """
@@ -0,+0 +1,+3 @@
+ def add_numbers(a, b):
+    # TODO: Add error handling for non-numeric inputs
+    return a + b
"""


class TestGetTodoSections:
    def test_get_todo_sections(self):
        result = get_todo_sections(patch, 'main.py')
        assert result[0] == 'main.py:2 - # TODO: Add error handling for non-numeric inputs'
