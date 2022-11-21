import os
import json
import re


def build_readme_content(filename: str, data: dict, sources: str) -> str:
    title = filename.replace('.json', '').replace('_', ' ').title()
    content = f'# {title}' + '\n\n' + sources
    return content


def get_sources(path: str) -> str:
    sources = "## Sources\n"
    with open(path, 'r') as f:
        old_readme = f.read()
        if match := re.search(r'## Sources(.|[\s])*$', old_readme):
            # Replace sources with current source text
            sources = match.group()
    return sources


def gen_data_readme(path: str, target_file: str):
    try:
        with open(os.path.join(path, target_file), 'r') as f:
            data = json.load(f)

        readme_file_path = os.path.join(path, 'README.md')
        sources = get_sources(readme_file_path)
        readme = build_readme_content(target_file, data, sources)

        with open(readme_file_path, 'w') as f:
            f.write(readme)
    except json.JSONDecodeError:
        pass


def gen_data_readmes() -> list[str]:
    for _dir in os.walk('data'):
        files = _dir[2]
        for f in files:
            if f.endswith('.json'):
                gen_data_readme(_dir[0], f)


if __name__ == '__main__':
    gen_data_readmes()
