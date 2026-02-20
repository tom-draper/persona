import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from colorama import Fore

DATA_DIR = Path(__file__).parent.parent / 'data'

# Maximum rows to show in a chart / table before truncating
MAX_ITEMS = 20


def flatten_dict(d: dict, parent_key: str = '', sep: str = ', ') -> dict:
    """Flatten nested dicts, joining keys with sep (inner key first)."""
    items = []
    for k, v in d.items():
        new_key = k + sep + parent_key if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def prepare_data(feature: str, raw: dict) -> dict:
    """Flatten, normalise, sort and truncate data for a feature."""
    flat = flatten_dict(raw)
    total = sum(flat.values())
    if total == 0:
        return {}

    flat = {k: v / total for k, v in flat.items()}

    # Age buckets keep their natural order; everything else sorts by share descending
    if feature != 'age':
        flat = dict(sorted(flat.items(), key=lambda x: x[1], reverse=True))

    if len(flat) > MAX_ITEMS:
        top = dict(list(flat.items())[:MAX_ITEMS])
        remainder = 1.0 - sum(top.values())
        if remainder > 0.001:
            top['Other'] = remainder
        flat = top

    return flat


def _blue_gradient(n: int) -> list:
    cmap = plt.cm.Blues
    return [cmap(0.35 + 0.5 * i / max(n - 1, 1)) for i in range(n)]


def gen_graph(path: str, feature: str, raw: dict) -> None:
    flat = prepare_data(feature, raw)
    if not flat:
        return

    labels = list(flat.keys())
    values = list(flat.values())
    n = len(labels)
    use_horizontal = n > 6

    colors = _blue_gradient(n)

    if use_horizontal:
        fig, ax = plt.subplots(figsize=(10, max(4, n * 0.40)))
        bars = ax.barh(range(n), values, color=colors[::-1], edgecolor='white', linewidth=0.4)
        ax.set_yticks(range(n))
        ax.set_yticklabels(labels, fontsize=9)
        ax.invert_yaxis()
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0, decimals=0))
        ax.set_xlabel('Share', fontsize=10)
        for bar, val in zip(bars, values):
            if val > 0.005:
                ax.text(
                    bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2,
                    f'{val:.1%}', va='center', fontsize=8, color='#333333',
                )
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(range(n), values, color=colors, edgecolor='white', linewidth=0.4)
        ax.set_xticks(range(n))
        ax.set_xticklabels(labels, rotation=-40, ha='left', fontsize=9)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0, decimals=0))
        ax.set_ylabel('Share', fontsize=10)
        for bar, val in zip(bars, values):
            if val > 0.01:
                ax.text(
                    bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                    f'{val:.1%}', ha='center', va='bottom', fontsize=8, color='#333333',
                )

    ax.set_title(feature.replace('_', ' ').title(), fontsize=13, fontweight='bold', pad=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(length=0)
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')
    plt.tight_layout()

    img_dir = Path(path) / 'img'
    img_dir.mkdir(exist_ok=True)
    fig.savefig(img_dir / f'{feature}.png', dpi=150, bbox_inches='tight')
    plt.close(fig)


def gen_composite_graph(path: str, location: str, raw: dict) -> None:
    total = sum(raw.values())
    flat = dict(sorted(
        {k: v / total for k, v in raw.items()}.items(),
        key=lambda x: x[1], reverse=True,
    ))

    labels = list(flat.keys())
    values = list(flat.values())
    n = len(labels)
    use_horizontal = n > 6
    colors = _blue_gradient(n)

    if use_horizontal:
        fig, ax = plt.subplots(figsize=(10, max(4, n * 0.40)))
        bars = ax.barh(range(n), values, color=colors[::-1], edgecolor='white', linewidth=0.4)
        ax.set_yticks(range(n))
        ax.set_yticklabels(labels, fontsize=9)
        ax.invert_yaxis()
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0, decimals=0))
        for bar, val in zip(bars, values):
            if val > 0.005:
                ax.text(
                    bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2,
                    f'{val:.1%}', va='center', fontsize=8,
                )
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(range(n), values, color=colors, edgecolor='white', linewidth=0.4)
        ax.set_xticks(range(n))
        ax.set_xticklabels(labels, rotation=-40, ha='left', fontsize=9)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0, decimals=0))
        for bar, val in zip(bars, values):
            if val > 0.01:
                ax.text(
                    bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                    f'{val:.1%}', ha='center', va='bottom', fontsize=8,
                )

    ax.set_title(location.replace('_', ' ').title(), fontsize=13, fontweight='bold', pad=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(length=0)
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')
    plt.tight_layout()

    img_dir = Path(path) / 'img'
    img_dir.mkdir(exist_ok=True)
    fig.savefig(img_dir / f'{location}.png', dpi=150, bbox_inches='tight')
    plt.close(fig)


def markdown_table(feature: str, raw: dict) -> str:
    flat = prepare_data(feature, raw)
    if not flat:
        return ''
    lines = ['| Option | Share |', '|---|---:|']
    for label, prob in flat.items():
        lines.append(f'| {label} | {prob:.1%} |')
    return '\n'.join(lines)


def printed_list(items: list[str]) -> str:
    if len(items) > 2:
        return ', '.join(items[:-1]) + ', and ' + items[-1]
    if len(items) == 2:
        return ' and '.join(items)
    if len(items) == 1:
        return items[0]
    return ''


def format_sources(sources: list[dict]) -> str:
    lines = ['## Sources', '']
    for source in sources:
        name = source.get('name', 'Unknown')
        year = source.get('year', '')
        url = source.get('url', '')
        features = source.get('features', [])
        year_str = f' ({year})' if year else ''
        link = f'[{name}{year_str}]({url})' if url else f'{name}{year_str}'
        features_str = ', '.join(f'`{f}`' for f in features)
        lines.append(f'- {link}')
        if features_str:
            lines.append(f'  *Covers: {features_str}*')
    return '\n'.join(lines)


def build_readme_content(path: str, data: dict, filename: str) -> str:
    title = filename.replace('.json', '').replace('_', ' ').title()
    features = [k for k in data if k != '_meta']

    lines = [
        f'# {title}',
        '',
        f'**{len(features)} feature{"s" if len(features) != 1 else ""}:** {printed_list(features)}.',
        '',
    ]

    for feature in features:
        heading = feature.replace('_', ' ').title()
        lines += [f'## {heading}', '']

        gen_graph(path, feature, data[feature])
        lines += [f'![{heading}](img/{feature}.png)', '']

        table = markdown_table(feature, data[feature])
        if table:
            lines += [table, '']

    sources = data.get('_meta', {}).get('sources', [])
    if sources:
        lines += [format_sources(sources)]

    return '\n'.join(lines)


def build_composite_readme_content(path: str, location: str, data: dict) -> str:
    title = location.replace('_', ' ').title()
    gen_composite_graph(path, location, data)

    lines = [
        f'# {title}',
        '',
        f'Composite location — randomly selects a sub-location weighted by population: {printed_list(list(data.keys()))}.',
        '',
        f'![{title}](img/{location}.png)',
        '',
    ]
    return '\n'.join(lines)


def gen_data_readme(path: str, target_file: str) -> None:
    try:
        with open(os.path.join(path, target_file)) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    readme_path = os.path.join(path, 'README.md')
    print(Fore.YELLOW + f'  {readme_path}' + Fore.RESET)

    if target_file == 'composite.json':
        location = os.path.basename(path)
        content = build_composite_readme_content(path, location, data)
    else:
        content = build_readme_content(path, data, target_file)

    with open(readme_path, 'w') as f:
        f.write(content)


def generate_docs() -> None:
    print(Fore.CYAN + 'Generating READMEs and charts...' + Fore.RESET)
    for dirpath, _, files in os.walk(str(DATA_DIR)):
        for f in files:
            if f.endswith('.json'):
                gen_data_readme(dirpath, f)
                break  # one JSON file per directory
    print(Fore.GREEN + 'Done.' + Fore.RESET)


if __name__ == '__main__':
    generate_docs()
