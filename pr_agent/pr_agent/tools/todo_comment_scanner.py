import re
from typing import List, Tuple


class TODOCommentScanner:
    def __init__(self, patterns: List[str]):
        """
        Initialize the scanner with a list of keyword patterns.
        Patterns are treated as whole words (\bKEYWORD\b).
        """
        self.patterns = [re.compile(rf"\b{re.escape(p)}\b") for p in patterns]

    def extract_added_lines(self, diff_text: str) -> List[Tuple[str, int, str]]:
        """
        Parse a unified diff string and return all added lines.

        Returns:
            List of tuples: (filename, line_number, line_content)
        """
        results: List[Tuple[str, int, str]] = []
        current_file: str = None
        new_lineno: int = None

        for line in diff_text.splitlines():
            if line.startswith("+++ b/"):
                # New file header in diff
                current_file = line[6:]
            elif line.startswith("@@"):
                # Hunk header: parse the starting line number of new file
                # Format: @@ -old_start,old_count +new_start,new_count @@
                parts = line.split()
                new_start = int(parts[2].split(",")[0].lstrip("+"))
                new_lineno = new_start
            elif line.startswith("+") and not line.startswith("+++"):
                # This is an added line. Strip the '+' and capture it.
                if current_file is not None and new_lineno is not None:
                    results.append((current_file, new_lineno, line[1:]))
                    new_lineno += 1
            elif not line.startswith("-") and new_lineno is not None:
                # Context line (unchanged) in the new file, increment line number
                new_lineno += 1

        return results

    def scan(self, diff_text: str) -> List[str]:
        """
        Scan the added lines of a diff for configured patterns.

        Returns:
            List of formatted strings: "filename:line_number — line_content"
        """
        found: List[str] = []
        for filename, lineno, content in self.extract_added_lines(diff_text):
            for pattern in self.patterns:
                if pattern.search(content):
                    found.append(f"{filename}:{lineno} — {content.strip()}")
        return found
