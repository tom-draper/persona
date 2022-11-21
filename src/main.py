import sys
from typing import Union

from colorama import Fore

from lib.generate import gen_samples

all_features = {'age', 'sex', 'religion', 'sexuality', 'ethnicity', 'religion',
                'language', 'location', 'relationship'}


alias = {
    'uk': 'united kingdom',
    'usa': 'united states',
    'uae': 'united arab emirates'
}


def pprint(data: dict[str, float]):
    for i, sample in enumerate(data):
        if len(data) > 1:
            print(Fore.CYAN + f'Persona {i+1}')
        for k, v in sample.items():
            print(Fore.YELLOW + k.title() + ': ' + Fore.WHITE + str(v))
        if len(data) > 1:
            print()


def get_count() -> int:
    count = 1
    for i, arg in enumerate(sys.argv):
        if arg == '-n' or arg == '-N' and i < len(sys.argv) - 1:
            count = int(sys.argv[i+1])

    return count


def get_enabled_features() -> Union[set[str], None]:
    enabled_features = None
    for arg in sys.argv:
        arg = arg.replace('-', '')
        if arg in all_features:
            enabled_features.add(arg)
    return enabled_features


def get_target_country() -> str:
    target = sys.argv[1].replace('-', ' ').replace('_', ' ')
    if target in alias:
        target = alias[target]
    return target


def run():
    if len(sys.argv) < 2:
        return

    # Collect arguments
    target = get_target_country()
    enabled_features = get_enabled_features()
    N = get_count()

    # Generate samples
    print(Fore.CYAN + '> ' + target.title() + Fore.WHITE)
    samples = gen_samples(target, enabled_features, N)
    pprint(samples)


if __name__ == '__main__':
    run()
