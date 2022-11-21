import os
import json
import re
import matplotlib.pyplot as plt



def flatten_dict(d: dict, parent_key: str = '', sep: str =', ') -> dict:
    items = []
    for k, v in d.items():
        new_key = k + sep + parent_key if parent_key else k
        if type(v) is dict:
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
    

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
        plt.xticks(x, labels)
        plt.ylabel('Probability')
        plt.title(feature.title())
        plt.tight_layout()

        # Create dir for images if not exist
        img_dir = os.path.join(path, 'img')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            
        img_path = os.path.join(img_dir, feature)
        print(img_path + '.png')
        
        plt.savefig(img_path)
        plt.close(fig)

        graphs.append(feature)
    
    return graphs


def build_readme_content(path: str, filename: str, data: dict, sources: str) -> str:
    title = filename.replace('.json', '').replace('_', ' ').title()
    graphs = gen_graphs(path, data)
    content = f'# {title}'
    
    for feature in graphs:
        content += f'\n\n## {feature.title()}\n\n![{feature.title()}](img/{feature}.png)'
    
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
