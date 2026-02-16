import argparse
import json
import sys
from typing import Union

from colorama import Fore, Style

from lib.format import clean_location
from lib.generate import gen_samples, list_locations

ALL_FEATURES = {
    'age', 'sex', 'religion', 'sexuality', 'ethnicity',
    'language', 'location', 'relationship', 'place of birth',
}


def pprint(data: list[dict]):
    for i, sample in enumerate(data):
        if len(data) > 1:
            print(Fore.CYAN + f'Persona {i+1}')
        for k, v in sample.items():
            print(Fore.YELLOW + k.title() + ': ' + Fore.WHITE + str(v))
        if len(data) > 1:
            print()
    print(Style.RESET_ALL, end='')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Generate realistic personas from real-world demographic data.',
        epilog='Example: python main.py england -n 3 --age --sex',
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
        '--json', action='store_true',
        help='Output as JSON instead of formatted text',
    )
    for feature in sorted(ALL_FEATURES):
        flag = '--' + feature.replace(' ', '-')
        parser.add_argument(flag, action='store_true', help=f'Include {feature}')
    return parser


def get_enabled_features(args: argparse.Namespace) -> Union[set[str], None]:
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
    enabled_features = get_enabled_features(args)
    N = args.n

    try:
        samples = gen_samples(target, enabled_features, N)
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
