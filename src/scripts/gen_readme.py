import os
import json
import re
import matplotlib.pyplot as plt


def gen_graphs(path: str, data: dict) -> list[dict]:
    graphs = []
    for feature, value in data.items():
        if type(value) is not dict:
            break
        
        labels = list(value.keys())
        x = list(range(len(labels)))
        y = list(value.values())
        plt.bar(x, y, align='center', alpha=0.5)
        plt.xticks(x, labels)
        plt.ylabel('Probability')
        plt.title(feature.title())

        img_dir = re.sub(r'^data', 'img', path)
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            
        img_path = os.path.join(img_dir, feature)
        print(img_path, img_dir)
        plt.savefig(img_path)
        plt.show()

        graphs.append({
            'title': feature.title(),
            'path': img_path
        })
    
    return graphs


def build_readme_content(path: str, filename: str, data: dict, sources: str) -> str:
    title = filename.replace('.json', '').replace('_', ' ').title()
    print(data)
    graphs = gen_graphs(path, data)
    content = f'# {title}'
    
    for graph in graphs:
        content += f'## {graph["title"]}\n\n![{graph["title"]}]({graph["path"]})'
    
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
        sources = get_sources(readme_file_path)
        readme = build_readme_content(path, target_file, data, sources)

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
