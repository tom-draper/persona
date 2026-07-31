# Only aliases that resolve to a dataset belong here. Names that already match
# a data directory once lowercased and underscored (united_kingdom, global,
# united_states_of_america) resolve without an entry.
alias = {
    "uk": "united_kingdom",
    "great_britain": "united_kingdom",
    "gb": "united_kingdom",
    "britain": "united_kingdom",
    "usa": "united_states_of_america",
    "us": "united_states_of_america",
    "u.s.": "united_states_of_america",
    "u.s.a.": "united_states_of_america",
    "america": "united_states_of_america",
    "united_states": "united_states_of_america",
    "world": "global",
    "earth": "global",
    "espana": "spain",
    "italia": "italy",
    "eire": "ireland",
    "republic_of_ireland": "ireland",
    "uae": "united_arab_emirates",
    "nz": "new_zealand",
    "drc": "democratic_republic_of_the_congo",
    "dr_congo": "democratic_republic_of_the_congo",
    "congo_kinshasa": "democratic_republic_of_the_congo",
    "ksa": "saudi_arabia",
    "ivory_coast": "cote_divoire",
    "holland": "netherlands",
    "czech_republic": "czechia",
    "dprk": "north_korea",
    "burkina": "burkina_faso",
    "dr": "dominican_republic",
    "png": "papua_new_guinea",
    "bosnia": "bosnia_and_herzegovina",
}


def clean_location(location: str) -> str:
    location = location.replace("-", "_").replace(" ", "_").lower()
    if location in alias:
        location = alias[location]
    return location
