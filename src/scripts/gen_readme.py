import json
import os
import re

import matplotlib.pyplot as plt
from colorama import Fore


def flatten_dict(d: dict, parent_key: str = '', sep: str = ', ') -> dict:
    items = []
    for k, v in d.items():
        new_key = k + sep + parent_key if parent_key else k
        if type(v) is dict:
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def gen_composite_graph(path: str, data: dict) -> list[dict]:
    _, location = os.path.split(path)

    # Build bars data
    labels = list(data.keys())
    x = list(range(len(labels)))
    y = list(data.values())

    # Create plot
    fig = plt.figure(figsize=(12, 8))
    plt.bar(x, y, align='center', alpha=0.5)
    plt.xticks(x, labels, rotation=-60, fontsize=9)
    plt.ylabel('Probability')
    plt.title(location.title())
    plt.tight_layout()

    # Create dir for images if not exist
    img_dir = os.path.join(path, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    img_path = os.path.join(img_dir, location)
    print(f'    {img_path}.png')

    plt.savefig(img_path)
    plt.close(fig)


def gen_graphs(path: str, data: dict) -> list[dict]:
    graphs = []
    for feature, value in data.items():
        if type(value) is not dict:
            break

        # Build bars data
        d = flatten_dict(value)
        labels = list(d.keys())
        x = list(range(len(labels)))
        y = list(d.values())

        # Create plot
        fig = plt.figure(figsize=(12, 8))
        plt.bar(x, y, align='center', alpha=0.5)
        plt.xticks(x, labels, rotation=-60, fontsize=9)
        plt.ylabel('Probability')
        plt.title(feature.title())
        plt.tight_layout()

        # Create dir for images if not exist
        img_dir = os.path.join(path, 'img')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        img_path = os.path.join(img_dir, feature)
        print(f'    {img_path}.png')

        plt.savefig(img_path)
        plt.close(fig)

        graphs.append(feature)

    return graphs


def printed_list_format(lst: list[str]):
    if len(lst) > 2:
        return ', '.join(lst[:-1]) + ", and " + str(lst[-1])
    elif len(lst) == 2:
        return ' and '.join(lst)
    elif len(lst) == 1:
        return lst[0]
    return ''


def build_composite_readme_content(path: str, data: dict) -> str:
    _, location = os.path.split(path)

    title = location.replace('_', ' ').title()
    gen_composite_graph(path, data)
    content = f'# {title}'

    content += '\n\nComposite: Made up of '

    locations = list(data.keys())
    content += printed_list_format(locations)

    content += f'.\n\n\![{title}](img/{location}.png)'
    return content


def build_readme_content(path: str, data: dict, filename: str) -> str:
    title = filename.replace('.json', '').replace('_', ' ').title()
    graphs = gen_graphs(path, data)
    content = f'# {title}'

    content += f'\n{len(graphs)} features '
    for i, feature in enumerate(graphs):
        if i == len(graphs) - 1:
            content += f'{feature.lower()}.'
        else:
            content += f'{feature.lower()}, '
    for feature in graphs:
        content += f'\n\n## {feature.title()}\n\n![{feature.title()}](img/{feature}.png)'

    readme_file_path = os.path.join(path, 'README.md')
    sources = get_sources(readme_file_path)
    content += '\n\n' + sources
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

        print(Fore.YELLOW + f'Generating {readme_file_path}...' + Fore.WHITE)

        if target_file == 'composite.json':
            readme = build_composite_readme_content(path, data)
        else:
            readme = build_readme_content(path, data, target_file)

        with open(readme_file_path, 'w') as f:
            f.write(readme)
    except json.JSONDecodeError:
        pass


def gen_data_readmes() -> list[str]:
    for _dir in os.walk('data'):
        path = _dir[0]
        files = _dir[2]
        for f in files:
            if f.endswith('.json'):
                gen_data_readme(path, f)
                break


if __name__ == '__main__':
    gen_data_readmes()
