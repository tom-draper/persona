import argparse
import json
import sys

from colorama import Fore, Style

from persona.lib.format import clean_location
from persona.lib.generate import gen_samples, list_all_features, list_locations


def pprint(data: list[dict]):
    for i, sample in enumerate(data):
        if len(data) > 1:
            print(Fore.CYAN + f"Persona {i + 1}")
        for k, v in sample.items():
            print(Fore.YELLOW + k.title() + ": " + Fore.WHITE + str(v))
        if len(data) > 1:
            print()
    print(Style.RESET_ALL, end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate realistic personas from real-world demographic data.",
        epilog="Example: persona england -n 3 --age --sex",
    )
    parser.add_argument(
        "target",
        nargs="*",
        default=None,
        help=(
            "Target location (e.g. england, united_kingdom, australia). "
            "Give a path to target a nested location that shares a name with a "
            "top-level one, e.g. 'persona united_states_of_america georgia' for "
            "the US state vs 'persona georgia' for the country."
        ),
    )
    parser.add_argument(
        "-n",
        type=int,
        default=1,
        metavar="COUNT",
        help="Number of personas to generate (default: 1)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available locations and exit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="SEED",
        help="Random seed for reproducible output",
    )
    for feature in sorted(list_all_features()):
        flag = "--" + feature.replace(" ", "-")
        parser.add_argument(flag, action="store_true", help=f"Include {feature}")
    return parser


def get_enabled_features(args: argparse.Namespace) -> set[str] | None:
    enabled = set()
    for feature in list_all_features():
        if getattr(args, feature.replace(" ", "_"), False):
            enabled.add(feature)
    return enabled if enabled else None


def format_location(location: str) -> str:
    return location.replace("_", " ").title()


def run():
    parser = build_parser()
    args = parser.parse_args()

    if args.list:
        for loc in list_locations():
            print(loc)
        return

    if not args.target:
        parser.print_help()
        return

    # A target may be several tokens forming a path down the tree
    # (e.g. "united_states_of_america georgia"); join them for gen_samples,
    # which normalises and resolves each segment.
    target = "/".join(args.target)
    enabled_features = get_enabled_features(args)
    N = args.n

    try:
        samples = gen_samples(target, enabled_features, N, seed=args.seed)
    except ValueError:
        print(
            Fore.RED + f"Error: location '{' '.join(args.target)}' not found." + Style.RESET_ALL,
            file=sys.stderr,
        )
        print("Run with --list to see available locations.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(samples, indent=2))
    else:
        heading = " / ".join(format_location(clean_location(t)) for t in args.target)
        print(Fore.CYAN + "> " + heading + Fore.WHITE)
        pprint(samples)


if __name__ == "__main__":
    run()
