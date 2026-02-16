

alias = {
    'uk': 'united_kingdom',
    'usa': 'united_states_of_america',
    'united_states': 'united_states_of_america',
    'uae': 'united_arab_emirates',
    'world': 'global',
}


def clean_location(location: str) -> str:
    location = location.replace('-', '_').replace(' ', '_').lower()
    if location in alias:
        location = alias[location]
    return location
