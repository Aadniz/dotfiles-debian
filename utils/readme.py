import re
from .utils import apt_pkg_installed
from typing import List, Dict

class Readme:

    __content: str = None
    __readme_path: str = None

    def __init__(self, readme_path: str) -> None:
        self.__readme_path = readme_path
        with open(self.__readme_path, 'r') as f:
            readme_content = f.read()
        self.__content = readme_content

    def get_pkgs_from_table(self, marker: str) -> List[List[str]]:
        # Extract the table content between the markers
        pattern = fr'<!--BEGIN_{marker}-->(.*?)<!--END_{marker}-->'
        match = re.search(pattern, self.__content, re.DOTALL)

        if not match:
            return []

        table_content = match.group(1).strip()

        # Split into lines and filter out empty lines
        lines = [line.strip() for line in table_content.split('\n') if line.strip()]

        # Remove the separator line (the line with |---|)
        # This assumes the separator line contains at least one '-'
        lines = [line for line in lines if not re.match(r'^\|[-:|]+\|$', line)]

        # Parse each line into a row
        table = []
        for line in lines[1:]:
            # Edge case where there is `\|` inside the column
            line = line.replace('\\|', '%%PIPE%%')
            cells = [cell.strip().replace('%%PIPE%%', '|')
                    for cell in re.split(r'(?<!\\)\|', line.strip('|'))]
            table.append(cells)

        return table

    def build_table(self, rows: List[List[str]]):
        """
        Build a table from a list of rows.
        The first row is the headers
        """
        # Determine the lengths for each column
        lengths = []
        width = len(rows[0])
        for i in range(width):
            max_length = 0
            for j, column in enumerate(rows):
                max_length = max(max_length, len(column[i]))
            lengths.append(max_length)

        table = ""
        for i, row in enumerate(rows):
            row_str = "|"
            for j, column in enumerate(row):
                row_str += " " + '{text: <{width}}'.format(text=column, width=lengths[j]) + " |"
            row_str += "\n"
            if i == 0:
                row_str += "|"
                for j in range(width):
                    row_str += '-'*(lengths[j]+2) + "|"
                row_str += "\n"
            table += row_str

        return table.rstrip("\n")

    def update_source_packages(self, apps: List[dict]):
        """Update the README.md with a table of source applications sorted by date."""

        # Sort applications by date (oldest first)
        apps_sorted = sorted(apps, key=lambda x: x['date'])

        table_rows = [["Name", "Link", "Last Updated"]]

        for app in apps_sorted:
            name = app['name']
            link = app['link']
            date = app['date'].strftime('%Y-%m-%d')

            # Format repository link if available
            repo_text = f"[Source link]({link})" if link else "-"

            table_rows.append([name, repo_text, date])

        table_content = self.build_table(table_rows)

        # Replace the content between markers
        pattern = r'(<!--BEGIN_SOURCE_PACKAGES-->)(.*?)(<!--END_SOURCE_PACKAGES-->)'
        replacement = f'\\1\n{table_content}\n\\3'
        self.__content = re.sub(pattern, replacement, self.__content, flags=re.DOTALL)

        # Write the updated README
        with open(self.__readme_path, 'w') as f:
            f.write(self.__content)

        print(f"Updated README.md with {len(apps_sorted)} source packages")

    def update_existing_pkgs(self, existing_pkgs: List[List[str]], new_pkgs: List[Dict[str, str]]) -> List[List[str]]:
        """
        Looks at existing packages that are no longer installed
        """
        # Remove first
        for pkg in existing_pkgs:
            to_be_removed = False
            for new_pkg in new_pkgs:
                if pkg[0] == new_pkg['name']:
                    if not new_pkg['installed']:
                        to_be_removed = True
                        break
            if to_be_removed:
                existing_pkgs.remove(pkg)

        # Look for new packages to append
        for new_pkg in new_pkgs:
            found = False
            for pkg in existing_pkgs:
                if pkg[0] == new_pkg['name'] and new_pkg['installed']:
                    found = True
                    break
            if not found and new_pkg['installed']:
                existing_pkgs.append([
                    new_pkg['name'],
                    new_pkg['description'] if new_pkg['description'] is not None else "-",
                    new_pkg['date'].strftime('%Y-%m-%d')
                ])

        return existing_pkgs

    def get_unfound_apt_packages(self) -> List[Dict[str, str]]:
        existings_pkgs = self.get_pkgs_from_table('APT_PACKAGES')
        unfound_pkgs = []
        for pkg in existings_pkgs:
            if not apt_pkg_installed(pkg[0]):
                unfound_pkgs.append({
                    'name': pkg[0],
                    'description': pkg[1],
                    'installed': False,
                    'date': pkg[2],
                })
        return unfound_pkgs

    def update_apt_packages(self, packages: List[Dict[str, str]]):
        """Update the apt packages section in README.md."""

        existings_pkgs = self.get_pkgs_from_table('APT_PACKAGES')
        new_pkgs = self.update_existing_pkgs(existings_pkgs, packages)
        rows = [["Package", "Description", "Installed"]] + new_pkgs
        table_content = self.build_table(rows)

        # Replace content between markers
        pattern = r'(<!--BEGIN_APT_PACKAGES-->)(.*?)(<!--END_APT_PACKAGES-->)'
        replacement = f'\\1\n{table_content}\n\\3'
        self.__content = re.sub(pattern, replacement, self.__content, flags=re.DOTALL)

        with open(self.__readme_path, 'w') as f:
            f.write(self.__content)