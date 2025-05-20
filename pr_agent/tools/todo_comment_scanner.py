import re
from typing import List, Tuple


class TODOCommentScanner:
    def __init__(self, patterns: List[str]):
        self.patterns = [re.compile(rf"\b{re.escape(p)}\b") for p in patterns]

    def extract_added_lines(self, diff_text: str) -> List[Tuple[str, int, str]]:
        results, current_file, new_lineno = [], None, None
        for line in diff_text.splitlines():
            if line.startswith("+++ b/"):
                current_file = line[6:]
            elif line.startswith("@@"):
                new_start = int(line.split()[2].split(",")[0].lstrip("+"))
                new_lineno = new_start
            elif (
                line.startswith("+")
                and not line.startswith("+++")
                and new_lineno is not None
            ):
                results.append((current_file, new_lineno, line[1:]))
                new_lineno += 1
            elif not line.startswith("-") and new_lineno is not None:
                new_lineno += 1
        return results

    def scan(self, diff_text: str) -> List[str]:
        found = []
        for fname, ln, content in self.extract_added_lines(diff_text):
            for pat in self.patterns:
                if pat.search(content):
                    found.append(f"{fname}:{ln} — {content.strip()}")
        return found
