all_features = {'age', 'sex', 'religion', 'sexuality', 'ethnicity', 'religion',
                'language', 'location', 'relationship', 'place of birth'}

alias = {
    'uk': 'united_kingdom',
    'usa': 'united_states',
    'uae': 'united_arab_emirates'
}


def format_location(location: str) -> str:
    location = location.replace('-', '_').lower()
    if location in alias:
        location = alias[location]
    return location
