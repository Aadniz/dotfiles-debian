import re
from typing import List, Dict


def update_source_packages(apps: List[dict], readme_path):
    """Update the README.md with a table of source applications sorted by date."""

    # Sort applications by date (oldest first)
    apps_sorted = sorted(apps, key=lambda x: x['date'])

    # Read current README
    with open(readme_path, 'r') as f:
        readme_content = f.read()

    # Generate the markdown table
    table_lines = [
        "| Name | Link       | Last Updated |",
        "|------|------------|--------------|",
    ]

    for app in apps_sorted:
        name = app['name']
        link = app['link']
        date = app['date'].strftime('%Y-%m-%d')

        # Format repository link if available
        repo_text = f"[Source link]({link})" if link else "-"

        table_lines.append(f"| {name} | {repo_text} | {date} |")

    table_content = '\n'.join(table_lines)

    # Replace the content between markers
    pattern = r'(<!--BEGIN_SOURCE_PACKAGES-->)(.*?)(<!--END_SOURCE_PACKAGES-->)'
    replacement = f'\\1\n{table_content}\n\\3'
    new_readme = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

    # Write the updated README
    with open(readme_path, 'w') as f:
        f.write(new_readme)

    print(f"Updated README.md with {len(apps_sorted)} source packages")


def update_apt_packages(packages: List[Dict[str, str]], readme_path: str):
    """Update the apt packages section in README.md."""
    with open(readme_path, 'r') as f:
        content = f.read()

    # Generate markdown table
    table_lines = [
        "| Package | Description | Installed |",
        "|---------|-------------|-----------|",
    ]

    for pkg in sorted(packages, key=lambda x: x['date']):
        table_lines.append(f"| {pkg['name']} | {pkg['description']} | {pkg['date'].strftime('%Y-%m-%d')} |")

    table_content = '\n'.join(table_lines)

    # Replace content between markers
    pattern = r'(<!--BEGIN_APT_PACKAGES-->)(.*?)(<!--END_APT_PACKAGES-->)'
    replacement = f'\\1\n{table_content}\n\\3'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(readme_path, 'w') as f:
        f.write(new_content)