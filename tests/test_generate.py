"""
Basic sanity tests for the persona generation logic.
Run with: pytest
"""

import numpy as np
import pytest

from persona.lib.generate import (
    _parse_age_bucket,
    collapsed_dict,
    gen_age,
    gen_api_samples,
    gen_feature,
    gen_sample,
    gen_samples,
    list_locations,
    normalise_weights,
)

# ---------------------------------------------------------------------------
# Probability helpers
# ---------------------------------------------------------------------------


def test_normalise_weights_sums_to_one():
    p = normalise_weights([0.3, 0.3, 0.4])
    assert abs(p.sum() - 1.0) < 1e-9


def test_normalise_weights_normalises_unequal_weights():
    p = normalise_weights([1.0, 1.0])
    assert abs(p.sum() - 1.0) < 1e-9
    assert abs(p[0] - 0.5) < 1e-9


def test_normalise_weights_zero_raises():
    with pytest.raises(ValueError):
        normalise_weights([0.0])


# ---------------------------------------------------------------------------
# Age generation
# ---------------------------------------------------------------------------


def test_gen_age_range_returns_int_in_bounds():
    rng = np.random.default_rng()
    age_data = {"25-29": 1.0}
    for _ in range(20):
        age = gen_age(age_data, rng)
        assert isinstance(age, int)
        assert 25 <= age <= 29


def test_gen_age_open_ended_capped_at_100():
    rng = np.random.default_rng()
    age_data = {"65+": 1.0}
    for _ in range(30):
        age = gen_age(age_data, rng)
        assert isinstance(age, int)
        assert 65 <= age <= 100


def test_gen_age_high_open_ended_does_not_exceed_100():
    rng = np.random.default_rng()
    age_data = {"90+": 1.0}
    for _ in range(30):
        age = gen_age(age_data, rng)
        assert 90 <= age <= 100


# ---------------------------------------------------------------------------
# collapsed_dict
# ---------------------------------------------------------------------------


def test_collapsed_dict_flat():
    result = collapsed_dict({"a": 0.5, "b": 0.5})
    assert len(result) == 2
    keys = [r[0] for r in result]
    assert ["a"] in keys and ["b"] in keys


def test_collapsed_dict_nested():
    d = {"White": {"British": 0.8, "Irish": 0.1}, "Asian": {"Indian": 0.1}}
    result = collapsed_dict(d)
    assert len(result) == 3


def test_collapsed_dict_deep_nesting():
    d = {"A": {"B": {"C": 1.0}}}
    result = collapsed_dict(d)
    assert len(result) == 1
    assert result[0][0] == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# gen_feature
# ---------------------------------------------------------------------------


def test_gen_feature_flat():
    rng = np.random.default_rng()
    feature = gen_feature({"Male": 0.49, "Female": 0.51}, rng)
    assert feature in ("Male", "Female")


def test_gen_feature_nested_joins_path():
    rng = np.random.default_rng()
    feature = gen_feature({"White": {"British": 1.0}}, rng)
    assert feature == "British, White"


def test_gen_feature_returns_native_str():
    rng = np.random.default_rng()
    feature = gen_feature({"Male": 0.49, "Female": 0.51}, rng)
    assert type(feature) is str


# ---------------------------------------------------------------------------
# gen_sample / gen_samples with real data
# ---------------------------------------------------------------------------


def test_gen_samples_england_returns_expected_keys():
    samples = gen_samples("england", N=1)
    assert len(samples) == 1
    sample = samples[0]
    assert "age" in sample
    assert "sex" in sample
    assert isinstance(sample["age"], int)
    assert 0 <= sample["age"] <= 100


def test_gen_samples_england_count():
    samples = gen_samples("england", N=5)
    assert len(samples) == 5


@pytest.mark.parametrize("count", [0, -1])
def test_gen_samples_rejects_non_positive_count(count):
    with pytest.raises(ValueError, match="at least 1"):
        gen_samples("england", N=count)


def test_gen_samples_enabled_features_subset():
    samples = gen_samples("england", enabled_features={"age", "sex"}, N=3)
    assert len(samples) == 3
    for sample in samples:
        assert set(sample.keys()) <= {"age", "sex"}
        assert "religion" not in sample


def test_gen_samples_meta_not_in_output():
    samples = gen_samples("england", N=5)
    for sample in samples:
        assert "_meta" not in sample


def test_gen_samples_australia():
    samples = gen_samples("australia", N=1)
    assert len(samples) == 1


def test_gen_samples_uk_composite():
    samples = gen_samples("united_kingdom", N=3)
    assert len(samples) == 3
    for sample in samples:
        assert "age" in sample


def test_gen_samples_invalid_location_raises():
    with pytest.raises(ValueError, match="not found"):
        gen_samples("nonexistent_place", N=1)


# ---------------------------------------------------------------------------
# _parse_age_bucket
# ---------------------------------------------------------------------------


def test_parse_age_bucket_range():
    rng = np.random.default_rng()
    assert 25 <= _parse_age_bucket("25-29", rng) <= 29


def test_parse_age_bucket_open_ended():
    rng = np.random.default_rng()
    age = _parse_age_bucket("65+", rng)
    assert 65 <= age <= 100


def test_parse_age_bucket_exact():
    rng = np.random.default_rng()
    assert _parse_age_bucket("5", rng) == 5


# ---------------------------------------------------------------------------
# preprocess_location_data + gen_api_samples
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def api_data():
    from persona.api.handler import load_location_data

    return load_location_data()


def test_preprocess_adds_processed_key(api_data):
    from persona.api.handler import resolve_key

    assert "processed" in api_data[resolve_key("england", api_data)]


def test_preprocess_composite_adds_subloc_keys(api_data):
    assert "subloc_keys" in api_data["united_kingdom"]
    assert "subloc_probs" in api_data["united_kingdom"]


def test_gen_api_samples_england(api_data):
    from persona.api.handler import resolve_key

    samples = gen_api_samples(resolve_key("england", api_data), api_data, N=1)
    assert len(samples) == 1
    sample = samples[0]
    assert "age" in sample
    assert isinstance(sample["age"], int)
    assert 0 <= sample["age"] <= 100
    assert type(sample["sex"]) is str


def test_gen_api_samples_count(api_data):
    from persona.api.handler import resolve_key

    samples = gen_api_samples(resolve_key("england", api_data), api_data, N=5)
    assert len(samples) == 5


@pytest.mark.parametrize("count", [0, -1])
def test_gen_api_samples_rejects_non_positive_count(api_data, count):
    from persona.api.handler import resolve_key

    with pytest.raises(ValueError, match="at least 1"):
        gen_api_samples(resolve_key("england", api_data), api_data, N=count)


def test_gen_api_samples_meta_not_in_output(api_data):
    from persona.api.handler import resolve_key

    samples = gen_api_samples(resolve_key("england", api_data), api_data, N=3)
    for sample in samples:
        assert "_meta" not in sample


def test_gen_api_samples_uk_composite(api_data):
    from persona.api.handler import resolve_key

    samples = gen_api_samples(resolve_key("united_kingdom", api_data), api_data, N=3)
    assert len(samples) == 3
    for sample in samples:
        assert "age" in sample
        assert "location" in sample


# ---------------------------------------------------------------------------
# list_locations
# ---------------------------------------------------------------------------


def test_list_locations_returns_sorted_list():
    locs = list_locations()
    assert isinstance(locs, list)
    assert locs == sorted(locs)


def test_list_locations_includes_expected():
    locs = list_locations()
    assert "england" in locs
    assert "united_kingdom" in locs  # composite
    assert "australia" in locs


def test_list_locations_excludes_meta():
    locs = list_locations()
    assert "_meta" not in locs


# ---------------------------------------------------------------------------
# clean_location aliases
# ---------------------------------------------------------------------------


def test_clean_location_aliases():
    from persona.lib.format import clean_location

    assert clean_location("uk") == "united_kingdom"
    assert clean_location("UK") == "united_kingdom"
    assert clean_location("britain") == "united_kingdom"
    assert clean_location("world") == "global"
    assert clean_location("northern-ireland") == "northern_ireland"
    for name in ("usa", "us", "U.S.A.", "america", "united_states", "United States of America"):
        assert clean_location(name) == "united_states_of_america", name
    # Unknown names pass through unchanged rather than mapping to missing data
    assert clean_location("atlantis") == "atlantis"


def test_gen_samples_marital_status_only_if_age_16_plus():
    # Run many times to catch a variety of ages including under-16
    for _ in range(50):
        sample = gen_samples("england", N=1)[0]
        if sample.get("age", 16) < 16:
            assert "marital status" not in sample


def test_gen_name_is_conditioned_on_sex_and_cohort():
    from persona.lib.generate import gen_name

    table = {
        "Male": {"1950s": {"Robert": 1.0}, "2000s": {"Jayden": 1.0}},
        "Female": {"1950s": {"Susan": 1.0}, "2000s": {"Emma": 1.0}},
    }
    rng = np.random.default_rng(0)
    # sex picks the branch; age picks the birth-decade cohort
    assert gen_name(table, "Female", 5, rng) == "Emma"  # born ~2020 -> 2000s
    assert gen_name(table, "Female", 70, rng) == "Susan"  # born ~1955 -> 1950s
    assert gen_name(table, "Male", 20, rng) == "Jayden"  # born ~2005 -> 2000s
    # a sex the table does not cover yields no name rather than a wrong guess
    assert gen_name(table, "Other", 30, rng) is None


def test_names_are_generated_for_all_ages_and_lead_the_persona():
    seen_child = seen_adult = False
    for sample in gen_samples("california", N=300, seed=3):
        assert "name" in sample
        # name leads the persona
        assert next(iter(sample)) == "name"
        if sample["age"] < 16:
            seen_child = True
        else:
            seen_adult = True
    assert seen_child and seen_adult


def test_bare_city_under_us_state_inherits_names():
    # New York City sits under the New York state leaf, which carries names.
    assert all("name" in s for s in gen_samples("new_york_city", N=20, seed=1))


def test_employment_status_is_adult_only_and_uses_canonical_labels():
    labels = set()
    for sample in gen_samples("netherlands", N=400, seed=7):
        es = sample.get("employment status")
        if sample["age"] < 16:
            assert es is None
        else:
            assert es is not None
            labels.add(es)
    assert labels <= {"Employed", "Unemployed", "Outside the labour force"}
    # all three surface across a healthy sample
    assert "Employed" in labels and "Outside the labour force" in labels


# ---------------------------------------------------------------------------
# Seed reproducibility
# ---------------------------------------------------------------------------


def test_gen_samples_seed_is_reproducible():
    a = gen_samples("england", N=3, seed=42)
    b = gen_samples("england", N=3, seed=42)
    assert a == b


def test_gen_samples_different_seeds_differ():
    a = gen_samples("england", N=1, seed=1)
    b = gen_samples("england", N=1, seed=2)
    assert a != b


def test_gen_api_samples_seed_is_reproducible(api_data):
    from persona.api.handler import resolve_key

    ek = resolve_key("england", api_data)
    a = gen_api_samples(ek, api_data, N=3, seed=99)
    b = gen_api_samples(ek, api_data, N=3, seed=99)
    assert a == b


def test_gen_api_samples_composite_seed_is_reproducible(api_data):
    a = gen_api_samples("united_kingdom", api_data, N=5, seed=7)
    b = gen_api_samples("united_kingdom", api_data, N=5, seed=7)
    assert a == b


# ---------------------------------------------------------------------------
# normalise_weights — additional
# ---------------------------------------------------------------------------


def test_normalise_weights_single_value():
    p = normalise_weights([5.0])
    assert abs(p[0] - 1.0) < 1e-9


def test_normalise_weights_accepts_generator():
    p = normalise_weights(x for x in [0.25, 0.25, 0.5])
    assert abs(p.sum() - 1.0) < 1e-9
    assert len(p) == 3


# ---------------------------------------------------------------------------
# collapsed_dict — edge cases
# ---------------------------------------------------------------------------


def test_collapsed_dict_empty():
    assert collapsed_dict({}) == []


def test_collapsed_dict_single_entry():
    result = collapsed_dict({"a": 1.0})
    assert result == [(["a"], 1.0)]


# ---------------------------------------------------------------------------
# gen_sample — direct unit tests
# ---------------------------------------------------------------------------


def test_gen_sample_excludes_meta():
    rng = np.random.default_rng(0)
    data = {"_meta": {"sources": []}, "sex": {"Male": 0.5, "Female": 0.5}}
    sample = gen_sample(data, None, rng)
    assert "_meta" not in sample
    assert "sex" in sample


def test_gen_sample_enabled_features_filter():
    rng = np.random.default_rng(0)
    data = {"age": {"20-29": 1.0}, "sex": {"Male": 1.0}, "religion": {"None": 1.0}}
    sample = gen_sample(data, {"age", "sex"}, rng)
    assert "religion" not in sample
    assert "age" in sample
    assert "sex" in sample


def test_gen_sample_marital_status_gated_below_16():
    data = {"age": {"0-10": 1.0}, "marital status": {"Single (never married)": 1.0}}
    for _ in range(10):
        sample = gen_sample(data, None, np.random.default_rng())
        assert "marital status" not in sample


def test_gen_sample_adult_features_do_not_depend_on_feature_order():
    data = {"marital status": {"Single (never married)": 1.0}, "age": {"0-10": 1.0}}

    sample = gen_sample(data, None, np.random.default_rng(0))

    assert set(sample) == {"age"}
    assert 0 <= sample["age"] <= 10


def test_gen_api_samples_adult_features_do_not_depend_on_feature_order():
    from persona.lib.generate import preprocess_location_data

    data = preprocess_location_data(
        {
            "test": {
                "key": "test",
                "name": "test",
                "leaf": {
                    "marital status": {"Single (never married)": 1.0},
                    "age": {"0-10": 1.0},
                },
                "composite": None,
            }
        }
    )

    sample = gen_api_samples("test", data, N=1, seed=0)[0]
    assert set(sample) == {"age"}
    assert 0 <= sample["age"] <= 10


# ---------------------------------------------------------------------------
# get_file_path / get_composite_path
# ---------------------------------------------------------------------------


def test_get_file_path_known_location():
    from persona.lib.generate import get_file_path

    path = get_file_path("england")
    assert path is not None
    assert path.name == "england.json"
    assert path.exists()


def test_get_file_path_unknown_location():
    from persona.lib.generate import get_file_path

    assert get_file_path("nonexistent_xyz") is None


def test_get_composite_path_composite_location():
    from persona.lib.generate import get_composite_path

    path = get_composite_path("united_kingdom")
    assert path is not None
    assert path.name == "composite.json"
    assert path.exists()


def test_get_composite_path_non_composite():
    from persona.lib.generate import get_composite_path

    # A pure leaf location (no composite.json in its directory).
    assert get_composite_path("wales") is None


# ---------------------------------------------------------------------------
# select_sublocation
# ---------------------------------------------------------------------------


def test_select_sublocation_returns_known_location():
    from persona.lib.generate import get_composite_path, select_sublocation

    path = get_composite_path("united_kingdom")
    rng = np.random.default_rng(0)
    subloc = select_sublocation(path, rng)
    assert isinstance(subloc, str)
    assert subloc in list_locations()


# ---------------------------------------------------------------------------
# gen_api_samples — additional
# ---------------------------------------------------------------------------


def test_gen_api_samples_enabled_features(api_data):
    from persona.api.handler import resolve_key

    samples = gen_api_samples(
        resolve_key("england", api_data), api_data, enabled_features={"age", "sex"}, N=3
    )
    assert len(samples) == 3
    for sample in samples:
        assert set(sample.keys()) <= {"age", "sex"}
        assert "religion" not in sample


# ---------------------------------------------------------------------------
# handler.get_features
# ---------------------------------------------------------------------------


def test_get_features_regular_location(api_data):
    from persona.api.handler import get_features

    result = get_features("england", api_data)
    assert "england" in result
    assert "age" in result["england"]
    assert "_meta" not in result["england"]


def test_get_features_composite_location(api_data):
    from persona.api.handler import get_features

    result = get_features("united_kingdom", api_data)
    assert "united_kingdom" in result
    assert "age" in result["united_kingdom"]
    assert "_meta" not in result["united_kingdom"]


def test_get_features_global_returns_world_baseline(api_data):
    from persona.api.handler import get_features

    result = get_features("global", api_data)
    assert set(result["global"]) == {
        "age",
        "sex",
        "religion",
        "residence",
        "marital status",
        "education",
        "employment status",
        "location",
    }


def test_location_paths_preserve_duplicate_location_names(api_data):
    from persona.api.app import _location_paths

    paths = _location_paths(api_data)

    assert paths == sorted(paths)
    assert "georgia" in paths
    assert "united_states_of_america/georgia" in paths


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------


def test_get_enabled_features_returns_none_when_no_flags():
    from persona.cli import build_parser, get_enabled_features

    args = build_parser().parse_args(["england"])
    assert get_enabled_features(args) is None


@pytest.mark.parametrize("count", ["0", "-1"])
def test_cli_rejects_non_positive_count(count):
    from persona.cli import build_parser

    with pytest.raises(SystemExit):
        build_parser().parse_args(["england", "--count", count])


def test_get_enabled_features_returns_set_when_flags_set():
    from persona.cli import build_parser, get_enabled_features

    args = build_parser().parse_args(["england", "--age", "--sex"])
    assert get_enabled_features(args) == {"age", "sex"}


def test_format_label_underscores_and_title():
    from persona.lib.format import format_label

    assert format_label("united_kingdom") == "United Kingdom"
    assert format_label("england") == "England"


# ---------------------------------------------------------------------------
# clean_location — additional
# ---------------------------------------------------------------------------


def test_clean_location_hyphen_to_underscore():
    from persona.lib.format import clean_location

    assert clean_location("united-kingdom") == "united_kingdom"


def test_clean_location_no_alias_passthrough():
    from persona.lib.format import clean_location

    assert clean_location("England") == "england"
    assert clean_location("AUSTRALIA") == "australia"


# ---------------------------------------------------------------------------
# _parse_age_bucket — additional
# ---------------------------------------------------------------------------


def test_parse_age_bucket_zero():
    rng = np.random.default_rng()
    assert _parse_age_bucket("0", rng) == 0


# ---------------------------------------------------------------------------
# Cities: nested leaves reached by bare-name expansion, not country descent
# ---------------------------------------------------------------------------


def test_country_query_never_yields_a_citys_detail():
    """A country query is internally consistent: it never descends into a nested
    city, so no city-level (ward/district) detail leaks into its personas."""
    tokyo_wards = {"Setagaya", "Suginami", "Shibuya", "Meguro", "Adachi", "Nerima", "Ōta"}
    japan_locs = [s.get("location", "") for s in gen_samples("japan", N=500, seed=1)]
    assert japan_locs and not any(w in loc for loc in japan_locs for w in tokyo_wards)
    ist_districts = {"Fatih", "Pendik", "Kartal", "Maltepe", "Tuzla"}
    turkey_locs = [s.get("location", "") for s in gen_samples("turkey", N=500, seed=1)]
    assert not any(d in loc for loc in turkey_locs for d in ist_districts)


def test_uk_composite_yields_only_its_nations():
    """The retained sub-national composite distributes over the four nations at a
    uniform granularity — it never descends three levels into a city."""
    from persona.lib.generate import resolve_location

    rng = np.random.default_rng(2)
    innermost = {resolve_location("united_kingdom", rng)[0][-1].parent.name for _ in range(400)}
    assert innermost <= {"england", "scotland", "wales", "northern_ireland"}


def test_bare_city_expands_through_parent_leaf_chain():
    """A bare city name resolves as its ancestor-leaf chain (england -> london),
    inheriting the parent baseline; a bare country is left single-segment."""
    from persona.lib.generate import _expand_to_path, _segments

    assert _expand_to_path(_segments("london")) == ["england", "london"]
    assert _expand_to_path(_segments("tokyo")) == ["japan", "tokyo"]
    assert _expand_to_path(_segments("england")) == ["england"]


def test_bare_london_is_complete_and_overrides_religion():
    """A bare London persona inherits England's baseline (so it is complete) and
    applies London's own religion distribution rather than England's."""
    import json

    from persona.lib.generate import DATA_DIR

    for sample in gen_samples("london", N=200, seed=3):
        assert "age" in sample and "sex" in sample and isinstance(sample["age"], int)
    london = json.loads((DATA_DIR / "united_kingdom/england/london/london.json").read_text())
    seen = {
        s["religion"] for s in gen_samples("london", enabled_features={"religion"}, N=400, seed=5)
    }
    assert seen <= set(london["religion"])  # London's own religion labels, not England's


def test_country_features_endpoint_excludes_nested_city():
    """A country's /features/ lists its own schema; a nested city is a separate
    location and is not unioned into the country's feature set."""
    from persona.api.handler import get_features, load_location_data, resolve_key

    data = load_location_data()
    england = set(get_features("england", data)["england"])
    england_leaf = {k for k in data[resolve_key("england", data)]["leaf"] if k != "_meta"}
    assert england == england_leaf


def test_bare_city_inherits_parent_baseline():
    """A bare city name inherits its parent country's baseline via overlay, so
    a London/Paris/etc persona is complete rather than the sparse city leaf."""
    for city, parent_feature in [("london", "sex"), ("paris", "sex"), ("madrid", "sex")]:
        samples = gen_samples(city, N=40, seed=8)
        for s in samples:
            assert "age" in s and parent_feature in s
        # an adult draw carries the inherited adult-only marital status
        assert any(s["age"] >= 16 and "marital status" in s for s in samples)


def test_bare_london_location_is_city_not_suffixed():
    """Bare `london` labels location plainly as London (london.json has no
    location of its own); a bare parent is unaffected and keeps district labels."""
    assert {s["location"] for s in gen_samples("london", N=20, seed=8)} == {"London"}
    paris = {s["location"] for s in gen_samples("paris", N=20, seed=8)}
    assert all(p.endswith("Paris") for p in paris)


def test_bare_city_features_endpoint_matches_generation():
    """The /features/ listing for a bare city includes the inherited features."""
    from persona.api.handler import get_features, load_location_data

    data = load_location_data()
    london = set(get_features("london", data)["london"])
    england = set(get_features("england", data)["england"])
    assert {"age", "sex", "marital status", "education"} <= london
    assert london <= england  # London inherits England's set, overriding some


def test_new_cities_inherit_parent_and_override_location():
    """Cities added under a country (tokyo, rome, mexico_city) or a US state
    (new_york_city) inherit that parent's schema and label location by district."""
    for city, parent_feature, districts in [
        ("tokyo", "religion", {"Setagaya", "Shinjuku", "Adachi"}),
        ("rome", "religion", {"EUR", "Aurelia", "Monteverde"}),
        ("new_york_city", "ethnicity", {"Brooklyn", "Queens", "Manhattan"}),
    ]:
        samples = gen_samples(city, N=60, seed=9)
        for s in samples:
            assert "age" in s and parent_feature in s and "residence" in s
        assert sum(s["residence"] == "Urban" for s in samples) >= 0.8 * len(samples)
        seen_districts = {s["location"].split(",")[0] for s in samples}
        assert seen_districts & districts  # location drawn from the city's districts
        assert all(s["location"].endswith(city.replace("_", " ").title()) for s in samples)


def test_second_city_batch_inherits_and_labels():
    """Buenos Aires, Istanbul and Jakarta inherit their country and label by
    district; their parents yield them via a population-share composite."""
    for city, city_label in [
        ("buenos_aires", "Buenos Aires"),
        ("istanbul", "Istanbul"),
        ("jakarta", "Jakarta"),
    ]:
        samples = gen_samples(city, N=40, seed=11)
        for s in samples:
            assert "age" in s and "religion" in s
        assert sum(s["residence"] == "Urban" for s in samples) >= 0.8 * len(samples)
        assert all(s["location"].endswith(city_label) for s in samples)


def test_third_city_batch_inherits_and_stays_explicit():
    """Seoul, Shanghai and Bangkok resolve explicitly with parent inheritance;
    their countries never leak the city districts into a country query."""
    for city, label in [("seoul", "Seoul"), ("shanghai", "Shanghai"), ("bangkok", "Bangkok")]:
        samples = gen_samples(city, N=40, seed=12)
        for s in samples:
            assert "age" in s and "religion" in s
        assert all(s["location"].endswith(label) for s in samples)
    kr_districts = {"Gangnam", "Songpa", "Mapo"}
    kr_locs = [s.get("location", "") for s in gen_samples("south_korea", N=400, seed=1)]
    assert not any(d in loc for loc in kr_locs for d in kr_districts)


def test_metro_manila_and_delhi_inherit():
    """Metro Manila (under the Philippines) and Delhi (under India) inherit their
    country baseline and label location by their own subdivisions."""
    for city, label in [("metro_manila", "Metro Manila"), ("delhi", "Delhi")]:
        samples = gen_samples(city, N=40, seed=13)
        for s in samples:
            assert {"age", "sex", "religion", "education"} <= set(s)  # inherited baseline
        assert all(s["location"].endswith(label) for s in samples)


def test_latin_american_cities_inherit_newly_added_countries():
    """Lima, Santiago and Caracas sit under countries added this round; they
    inherit the country baseline and label location by their own subdivisions."""
    for city, label in [("lima", "Lima"), ("santiago", "Santiago"), ("caracas", "Caracas")]:
        samples = gen_samples(city, N=30, seed=14)
        for s in samples:
            assert {"age", "sex", "religion", "education"} <= set(s)
        assert all(s["location"].endswith(label) for s in samples)


def test_asia_africa_cities_inherit_and_alias():
    """Beijing, Hong Kong and Addis Ababa inherit their parent and label by
    district; the peking alias resolves to beijing."""
    from persona.lib.format import clean_location

    assert clean_location("peking") == "beijing"
    cities = [("beijing", "Beijing"), ("hong_kong", "Hong Kong"), ("addis_ababa", "Addis Ababa")]
    for city, label in cities:
        samples = gen_samples(city, N=30, seed=15)
        for s in samples:
            assert {"age", "sex", "religion"} <= set(s)
        assert all(s["location"].endswith(label) for s in samples)


def test_city_alias_resolves():
    from persona.lib.format import clean_location

    assert clean_location("nyc") == "new_york_city"
    assert clean_location("cdmx") == "mexico_city"
    assert clean_location("caba") == "buenos_aires"
    assert clean_location("constantinople") == "istanbul"
    assert clean_location("manila") == "metro_manila"
    assert gen_samples("nyc", N=1, seed=1)[0]["location"].endswith("New York City")


def test_bare_us_state_unaffected_by_expansion():
    """A US state sits under a composite-only parent, so bare addressing is not
    expanded: it keeps its own schema and gains no inherited country baseline
    (and, having no location feature of its own, no location label)."""
    for s in gen_samples("alabama", N=10, seed=8):
        assert "ethnicity" in s  # its own US-state schema is intact
        assert "location" not in s  # not expanded into a usa/alabama path


# ---------------------------------------------------------------------------
# Path addressing (disambiguating shared names by descending the tree)
# ---------------------------------------------------------------------------


def test_bare_name_resolves_to_top_level_country():
    # "georgia" alone is the country, not the US state
    for s in gen_samples("georgia", N=20, seed=1):
        assert "ethnicity" not in s  # country dataset has no ethnicity feature


def test_path_targets_nested_us_state():
    samples = gen_samples("united_states_of_america georgia", N=20, seed=1)
    for s in samples:
        assert "ethnicity" in s  # US-state schema
        assert s["location"] == "Georgia"


def test_path_accepts_slash_and_alias():
    a = gen_samples("us/georgia", N=5, seed=1)
    b = gen_samples("united_states_of_america georgia", N=5, seed=1)
    assert all("ethnicity" in s for s in a)
    assert a == b  # "us" alias + slash separator == full name + space


def test_partial_path_then_random_remainder():
    # uk england -> forces England, then fills in an English region at random
    locs = {s["location"] for s in gen_samples("united_kingdom england", N=300, seed=2)}
    assert any(loc.endswith("England") for loc in locs)


def test_api_path_key_disambiguation():
    from persona.api.handler import load_location_data, resolve_path_key

    data = load_location_data()
    assert resolve_path_key("georgia", data) == "georgia"
    assert resolve_path_key("us/georgia", data) == "united_states_of_america/georgia"
    assert resolve_path_key("united_states_of_america georgia", data) == (
        "united_states_of_america/georgia"
    )
    assert resolve_path_key("nowhere/georgia", data) is None
