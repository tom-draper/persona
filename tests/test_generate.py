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
    preprocess_location_data,
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
    age_data = {'25-29': 1.0}
    for _ in range(20):
        age = gen_age(age_data, rng)
        assert isinstance(age, int)
        assert 25 <= age <= 29


def test_gen_age_open_ended_capped_at_100():
    rng = np.random.default_rng()
    age_data = {'65+': 1.0}
    for _ in range(30):
        age = gen_age(age_data, rng)
        assert isinstance(age, int)
        assert 65 <= age <= 100


def test_gen_age_high_open_ended_does_not_exceed_100():
    rng = np.random.default_rng()
    age_data = {'90+': 1.0}
    for _ in range(30):
        age = gen_age(age_data, rng)
        assert 90 <= age <= 100


# ---------------------------------------------------------------------------
# collapsed_dict
# ---------------------------------------------------------------------------

def test_collapsed_dict_flat():
    result = collapsed_dict({'a': 0.5, 'b': 0.5})
    assert len(result) == 2
    keys = [r[0] for r in result]
    assert ['a'] in keys and ['b'] in keys


def test_collapsed_dict_nested():
    d = {'White': {'British': 0.8, 'Irish': 0.1}, 'Asian': {'Indian': 0.1}}
    result = collapsed_dict(d)
    assert len(result) == 3


def test_collapsed_dict_deep_nesting():
    d = {'A': {'B': {'C': 1.0}}}
    result = collapsed_dict(d)
    assert len(result) == 1
    assert result[0][0] == ['A', 'B', 'C']


# ---------------------------------------------------------------------------
# gen_feature
# ---------------------------------------------------------------------------

def test_gen_feature_flat():
    rng = np.random.default_rng()
    feature = gen_feature({'Male': 0.49, 'Female': 0.51}, rng)
    assert feature in ('Male', 'Female')


def test_gen_feature_nested_joins_path():
    rng = np.random.default_rng()
    feature = gen_feature({'White': {'British': 1.0}}, rng)
    assert feature == 'British, White'


def test_gen_feature_returns_native_str():
    rng = np.random.default_rng()
    feature = gen_feature({'Male': 0.49, 'Female': 0.51}, rng)
    assert type(feature) is str


# ---------------------------------------------------------------------------
# gen_sample / gen_samples with real data
# ---------------------------------------------------------------------------

def test_gen_samples_england_returns_expected_keys():
    samples = gen_samples('england', N=1)
    assert len(samples) == 1
    sample = samples[0]
    assert 'age' in sample
    assert 'sex' in sample
    assert isinstance(sample['age'], int)
    assert 0 <= sample['age'] <= 100


def test_gen_samples_england_count():
    samples = gen_samples('england', N=5)
    assert len(samples) == 5


def test_gen_samples_enabled_features_subset():
    samples = gen_samples('england', enabled_features={'age', 'sex'}, N=3)
    assert len(samples) == 3
    for sample in samples:
        assert set(sample.keys()) <= {'age', 'sex'}
        assert 'religion' not in sample


def test_gen_samples_meta_not_in_output():
    samples = gen_samples('england', N=5)
    for sample in samples:
        assert '_meta' not in sample


def test_gen_samples_australia():
    samples = gen_samples('australia', N=1)
    assert len(samples) == 1


def test_gen_samples_uk_composite():
    samples = gen_samples('united_kingdom', N=3)
    assert len(samples) == 3
    for sample in samples:
        assert 'age' in sample


def test_gen_samples_invalid_location_raises():
    with pytest.raises(ValueError, match="not found"):
        gen_samples('nonexistent_place', N=1)


# ---------------------------------------------------------------------------
# _parse_age_bucket
# ---------------------------------------------------------------------------

def test_parse_age_bucket_range():
    rng = np.random.default_rng()
    assert 25 <= _parse_age_bucket('25-29', rng) <= 29


def test_parse_age_bucket_open_ended():
    rng = np.random.default_rng()
    age = _parse_age_bucket('65+', rng)
    assert 65 <= age <= 100


def test_parse_age_bucket_exact():
    rng = np.random.default_rng()
    assert _parse_age_bucket('5', rng) == 5


# ---------------------------------------------------------------------------
# preprocess_location_data + gen_api_samples
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def api_data():
    from persona.api.handler import load_location_data
    return load_location_data()


def test_preprocess_adds_processed_key(api_data):
    assert 'processed' in api_data['england']


def test_preprocess_composite_adds_subloc_keys(api_data):
    assert 'subloc_keys' in api_data['united_kingdom']
    assert 'subloc_probs' in api_data['united_kingdom']


def test_gen_api_samples_england(api_data):
    samples = gen_api_samples('england', api_data, N=1)
    assert len(samples) == 1
    sample = samples[0]
    assert 'age' in sample
    assert isinstance(sample['age'], int)
    assert 0 <= sample['age'] <= 100
    assert type(sample['sex']) is str


def test_gen_api_samples_count(api_data):
    samples = gen_api_samples('england', api_data, N=5)
    assert len(samples) == 5


def test_gen_api_samples_meta_not_in_output(api_data):
    samples = gen_api_samples('england', api_data, N=3)
    for sample in samples:
        assert '_meta' not in sample


def test_gen_api_samples_uk_composite(api_data):
    samples = gen_api_samples('united_kingdom', api_data, N=3)
    assert len(samples) == 3
    for sample in samples:
        assert 'age' in sample
        assert 'location' in sample


# ---------------------------------------------------------------------------
# list_locations
# ---------------------------------------------------------------------------

def test_list_locations_returns_sorted_list():
    locs = list_locations()
    assert isinstance(locs, list)
    assert locs == sorted(locs)


def test_list_locations_includes_expected():
    locs = list_locations()
    assert 'england' in locs
    assert 'united_kingdom' in locs  # composite
    assert 'australia' in locs


def test_list_locations_excludes_meta():
    locs = list_locations()
    assert '_meta' not in locs


# ---------------------------------------------------------------------------
# clean_location aliases
# ---------------------------------------------------------------------------

def test_clean_location_aliases():
    from persona.lib.format import clean_location
    assert clean_location('uk') == 'united_kingdom'
    assert clean_location('usa') == 'united_states_of_america'
    assert clean_location('united_states') == 'united_states_of_america'
    assert clean_location('United States') == 'united_states_of_america'
    assert clean_location('world') == 'global'


def test_gen_samples_relationship_only_if_age_16_plus():
    # Run many times to catch a variety of ages including under-16
    for _ in range(50):
        sample = gen_samples('england', N=1)[0]
        if sample.get('age', 16) < 16:
            assert 'relationship' not in sample


# ---------------------------------------------------------------------------
# Seed reproducibility
# ---------------------------------------------------------------------------

def test_gen_samples_seed_is_reproducible():
    a = gen_samples('england', N=3, seed=42)
    b = gen_samples('england', N=3, seed=42)
    assert a == b


def test_gen_samples_different_seeds_differ():
    a = gen_samples('england', N=1, seed=1)
    b = gen_samples('england', N=1, seed=2)
    assert a != b


def test_gen_api_samples_seed_is_reproducible(api_data):
    a = gen_api_samples('england', api_data, N=3, seed=99)
    b = gen_api_samples('england', api_data, N=3, seed=99)
    assert a == b


def test_gen_api_samples_composite_seed_is_reproducible(api_data):
    a = gen_api_samples('united_kingdom', api_data, N=5, seed=7)
    b = gen_api_samples('united_kingdom', api_data, N=5, seed=7)
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
    result = collapsed_dict({'a': 1.0})
    assert result == [(['a'], 1.0)]


# ---------------------------------------------------------------------------
# gen_sample — direct unit tests
# ---------------------------------------------------------------------------

def test_gen_sample_excludes_meta():
    rng = np.random.default_rng(0)
    data = {'_meta': {'sources': []}, 'sex': {'Male': 0.5, 'Female': 0.5}}
    sample = gen_sample(data, None, rng)
    assert '_meta' not in sample
    assert 'sex' in sample


def test_gen_sample_enabled_features_filter():
    rng = np.random.default_rng(0)
    data = {'age': {'20-29': 1.0}, 'sex': {'Male': 1.0}, 'religion': {'None': 1.0}}
    sample = gen_sample(data, {'age', 'sex'}, rng)
    assert 'religion' not in sample
    assert 'age' in sample
    assert 'sex' in sample


def test_gen_sample_relationship_gated_below_16():
    data = {'age': {'0-10': 1.0}, 'relationship': {'Single': 1.0}}
    for _ in range(10):
        sample = gen_sample(data, None, np.random.default_rng())
        assert 'relationship' not in sample


# ---------------------------------------------------------------------------
# get_file_path / get_composite_path
# ---------------------------------------------------------------------------

def test_get_file_path_known_location():
    from persona.lib.generate import get_file_path
    path = get_file_path('england')
    assert path is not None
    assert path.name == 'england.json'
    assert path.exists()


def test_get_file_path_unknown_location():
    from persona.lib.generate import get_file_path
    assert get_file_path('nonexistent_xyz') is None


def test_get_composite_path_composite_location():
    from persona.lib.generate import get_composite_path
    path = get_composite_path('united_kingdom')
    assert path is not None
    assert path.name == 'composite.json'
    assert path.exists()


def test_get_composite_path_non_composite():
    from persona.lib.generate import get_composite_path
    assert get_composite_path('england') is None


# ---------------------------------------------------------------------------
# select_sublocation
# ---------------------------------------------------------------------------

def test_select_sublocation_returns_known_location():
    from persona.lib.generate import get_composite_path, select_sublocation
    path = get_composite_path('united_kingdom')
    rng = np.random.default_rng(0)
    subloc = select_sublocation(path, rng)
    assert isinstance(subloc, str)
    assert subloc in list_locations()


# ---------------------------------------------------------------------------
# gen_api_samples — additional
# ---------------------------------------------------------------------------

def test_gen_api_samples_enabled_features(api_data):
    samples = gen_api_samples('england', api_data, enabled_features={'age', 'sex'}, N=3)
    assert len(samples) == 3
    for sample in samples:
        assert set(sample.keys()) <= {'age', 'sex'}
        assert 'religion' not in sample


# ---------------------------------------------------------------------------
# handler.get_features
# ---------------------------------------------------------------------------

def test_get_features_regular_location(api_data):
    from persona.api.handler import get_features
    result = get_features('england', api_data)
    assert 'england' in result
    assert 'age' in result['england']
    assert '_meta' not in result['england']


def test_get_features_composite_location(api_data):
    from persona.api.handler import get_features
    result = get_features('united_kingdom', api_data)
    assert isinstance(result, dict)
    assert len(result) > 1  # multiple sublocations


def test_get_features_global_returns_empty(api_data):
    from persona.api.handler import get_features
    result = get_features('global', api_data)
    assert result == {}


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def test_get_enabled_features_returns_none_when_no_flags():
    from persona.cli import build_parser, get_enabled_features
    args = build_parser().parse_args(['england'])
    assert get_enabled_features(args) is None


def test_get_enabled_features_returns_set_when_flags_set():
    from persona.cli import build_parser, get_enabled_features
    args = build_parser().parse_args(['england', '--age', '--sex'])
    assert get_enabled_features(args) == {'age', 'sex'}


def test_format_location_underscores_and_title():
    from persona.cli import format_location
    assert format_location('united_kingdom') == 'United Kingdom'
    assert format_location('england') == 'England'


# ---------------------------------------------------------------------------
# clean_location — additional
# ---------------------------------------------------------------------------

def test_clean_location_hyphen_to_underscore():
    from persona.lib.format import clean_location
    assert clean_location('united-kingdom') == 'united_kingdom'


def test_clean_location_no_alias_passthrough():
    from persona.lib.format import clean_location
    assert clean_location('England') == 'england'
    assert clean_location('AUSTRALIA') == 'australia'


# ---------------------------------------------------------------------------
# _parse_age_bucket — additional
# ---------------------------------------------------------------------------

def test_parse_age_bucket_zero():
    rng = np.random.default_rng()
    assert _parse_age_bucket('0', rng) == 0
