import argparse
import json
import sys

from colorama import Fore, Style

from persona.lib.format import clean_location
from persona.lib.generate import collapsed_dict, gen_samples, get_composite_path, get_file_path, list_locations

ALL_FEATURES = {
    'age', 'sex', 'religion', 'sexuality', 'ethnicity',
    'language', 'location', 'relationship', 'place of birth',
    'occupation', 'education', 'marital status', 'housing tenure', 'country of birth',
}

BAR_MAX = 40


def pprint(data: list[dict]):
    for i, sample in enumerate(data):
        if len(data) > 1:
            print(Fore.CYAN + f'Persona {i+1}')
        for k, v in sample.items():
            print(Fore.YELLOW + k.title() + ': ' + Fore.WHITE + str(v))
        if len(data) > 1:
            print()
    print(Style.RESET_ALL, end='')


def load_location_data(location: str) -> dict | None:
    path = get_file_path(location)
    if path is None:
        return None
    with open(path) as f:
        return json.load(f)


def show_distribution(location: str, feature: str, data: dict) -> None:
    feature_data = data.get(feature)
    if feature_data is None:
        available = [k for k in data if k != '_meta']
        print(Fore.RED + f"Feature '{feature}' not found for {format_location(location)}." + Style.RESET_ALL)
        print('Available: ' + ', '.join(available))
        sys.exit(1)

    collapsed = collapsed_dict(feature_data)
    labels = [', '.join(reversed(path)) for path, _ in collapsed]
    values = [v for _, v in collapsed]

    total = sum(values)
    pcts = [v / total for v in values]

    if feature != 'age':
        pairs = sorted(zip(labels, pcts), key=lambda x: -x[1])
        labels, pcts = [p[0] for p in pairs], [p[1] for p in pairs]

    max_label = max(len(l) for l in labels)
    max_pct = max(pcts)

    title = f'{format_location(location)} - {feature.title()}'
    rule = '─' * (max_label + BAR_MAX + 12)

    print()
    print(Fore.CYAN + title + Fore.RESET)
    print(rule)

    for label, pct in zip(labels, pcts):
        bar_len = round(pct / max_pct * BAR_MAX)
        bar = '█' * bar_len
        padded_label = label.ljust(max_label)
        pct_str = f'{pct * 100:.1f}%'.rjust(6)
        print(f'{Fore.YELLOW}{padded_label}{Fore.RESET}  {Fore.BLUE}{bar:<{BAR_MAX}}{Fore.RESET}  {pct_str}')

    sources = data.get('_meta', {}).get('sources', [])
    relevant = [s for s in sources if feature in s.get('features', [])]
    if relevant:
        print()
        for s in relevant:
            print(Style.DIM + f"Source: {s['name']} ({s['year']})" + Style.RESET_ALL)
    print()


def show_features(location: str, data: dict) -> None:
    features = [k for k in data if k != '_meta']
    print(Fore.CYAN + format_location(location) + ' - available features:' + Fore.RESET)
    for f in features:
        print(f'  {f}')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Generate realistic personas from real-world demographic data.',
        epilog='Example: persona england -n 3 --age --sex',
    )
    parser.add_argument(
        'target',
        nargs='?',
        default=None,
        help='Target location (e.g. england, united_kingdom, australia)',
    )
    parser.add_argument(
        '-n', type=int, default=1, metavar='COUNT',
        help='Number of personas to generate (default: 1)',
    )
    parser.add_argument(
        '--list', action='store_true',
        help='List all available locations and exit',
    )
    parser.add_argument(
        '--show',
        nargs='?',
        const='',
        metavar='FEATURE',
        help='Show distribution for a feature (omit FEATURE to list available features)',
    )
    parser.add_argument(
        '--json', action='store_true',
        help='Output as JSON instead of formatted text',
    )
    parser.add_argument(
        '--seed', type=int, default=None, metavar='SEED',
        help='Random seed for reproducible output',
    )
    for feature in sorted(ALL_FEATURES):
        flag = '--' + feature.replace(' ', '-')
        parser.add_argument(flag, action='store_true', help=f'Include {feature}')
    return parser


def get_enabled_features(args: argparse.Namespace) -> set[str] | None:
    enabled = set()
    for feature in ALL_FEATURES:
        if getattr(args, feature.replace(' ', '_'), False):
            enabled.add(feature)
    return enabled if enabled else None


def format_location(location: str) -> str:
    return location.replace('_', ' ').title()


def run():
    parser = build_parser()
    args = parser.parse_args()

    if args.list:
        for loc in list_locations():
            print(loc)
        return

    if args.target is None:
        parser.print_help()
        return

    target = clean_location(args.target)

    if args.show is not None:
        data = load_location_data(target)
        if data is None:
            if get_composite_path(target):
                print(
                    Fore.RED + f"'{args.target}' contains sub-locations — use a more specific location." + Style.RESET_ALL,
                    file=sys.stderr,
                )
            else:
                print(
                    Fore.RED + f"Location '{args.target}' not found." + Style.RESET_ALL,
                    file=sys.stderr,
                )
                print("Run with --list to see available locations.", file=sys.stderr)
            sys.exit(1)

        if args.show == '':
            show_features(target, data)
        else:
            show_distribution(target, args.show, data)
        return

    enabled_features = get_enabled_features(args)
    N = args.n

    try:
        samples = gen_samples(target, enabled_features, N, seed=args.seed)
    except ValueError:
        print(
            Fore.RED + f"Error: location '{args.target}' not found." + Style.RESET_ALL,
            file=sys.stderr,
        )
        print("Run with --list to see available locations.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(samples, indent=2))
    else:
        print(Fore.CYAN + '> ' + format_location(target) + Fore.WHITE)
        pprint(samples)


if __name__ == '__main__':
    run()
