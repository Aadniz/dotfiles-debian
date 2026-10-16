import re
import sys
from pathlib import Path


class Readme:
    """Markdown tables placed between <!--BEGIN_X--> and <!--END_X--> markers."""

    def __init__(self, path: Path):
        self.path = path
        self.text = path.read_text()

    def _section(self, marker: str) -> re.Match:
        match = re.search(rf"<!--BEGIN_{marker}-->(.*?)<!--END_{marker}-->", self.text, re.DOTALL)
        if not match:
            sys.exit(f"{self.path} is missing the <!--BEGIN_{marker}--> and <!--END_{marker}--> markers")
        return match

    def table(self, marker: str) -> list[list[str]]:
        """Rows without header and separator. Cells are kept as written, so an escaped "\\|" stays escaped."""
        lines = self._section(marker)[1].strip().splitlines()[2:]
        return [[cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip())[1:-1]] for line in lines]

    def set_table(self, marker: str, header: list[str], rows: list[list[str]]) -> None:
        widths = [max(map(len, column)) for column in zip(header, *rows)]

        def line(cells: list[str]) -> str:
            return "| " + " | ".join(cell.ljust(width) for cell, width in zip(cells, widths)) + " |"

        table = [line(header), "|" + "|".join("-" * (w + 2) for w in widths) + "|", *map(line, rows)]
        start, end = self._section(marker).span(1)
        self.text = self.text[:start] + "\n" + "\n".join(table) + "\n" + self.text[end:]

    def save(self) -> None:
        self.path.write_text(self.text)
