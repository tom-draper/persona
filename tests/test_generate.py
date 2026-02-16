"""
Basic sanity tests for the persona generation logic.
Run with: pytest
"""
import pytest

from lib.generate import (
    collapsed_dict,
    gen_age,
    gen_feature,
    gen_sample,
    gen_samples,
    probabilities_from_dict,
    probabilities_from_list,
)


# ---------------------------------------------------------------------------
# Probability helpers
# ---------------------------------------------------------------------------

def test_probabilities_from_dict_sums_to_one():
    p = probabilities_from_dict({'a': 0.3, 'b': 0.3, 'c': 0.4})
    assert abs(p.sum() - 1.0) < 1e-9


def test_probabilities_from_dict_normalises_unequal_weights():
    p = probabilities_from_dict({'a': 1.0, 'b': 1.0})
    assert abs(p.sum() - 1.0) < 1e-9
    assert abs(p[0] - 0.5) < 1e-9


def test_probabilities_from_dict_zero_raises():
    with pytest.raises(ValueError):
        probabilities_from_dict({'a': 0.0})


def test_probabilities_from_list_sums_to_one():
    p = probabilities_from_list([('a', 0.6), ('b', 0.4)])
    assert abs(p.sum() - 1.0) < 1e-9


def test_probabilities_from_list_zero_raises():
    with pytest.raises(ValueError):
        probabilities_from_list([('a', 0.0)])


# ---------------------------------------------------------------------------
# Age generation
# ---------------------------------------------------------------------------

def test_gen_age_range_returns_int_in_bounds():
    age_data = {'25-29': 1.0}
    for _ in range(20):
        age = gen_age(age_data)
        assert isinstance(age, int)
        assert 25 <= age <= 29


def test_gen_age_open_ended_capped_at_100():
    age_data = {'65+': 1.0}
    for _ in range(30):
        age = gen_age(age_data)
        assert isinstance(age, int)
        assert 65 <= age <= 100


def test_gen_age_high_open_ended_does_not_exceed_100():
    age_data = {'90+': 1.0}
    for _ in range(30):
        age = gen_age(age_data)
        assert 90 <= age <= 100


# ---------------------------------------------------------------------------
# collapsed_dict
# ---------------------------------------------------------------------------

def test_collapsed_dict_flat():
    result = collapsed_dict({'a': 0.5, 'b': 0.5}, [], [])
    assert len(result) == 2
    keys = [r[0] for r in result]
    assert ['a'] in keys and ['b'] in keys


def test_collapsed_dict_nested():
    d = {'White': {'British': 0.8, 'Irish': 0.1}, 'Asian': {'Indian': 0.1}}
    result = collapsed_dict(d, [], [])
    assert len(result) == 3


def test_collapsed_dict_deep_nesting():
    d = {'A': {'B': {'C': 1.0}}}
    result = collapsed_dict(d, [], [])
    assert len(result) == 1
    assert result[0][0] == ['A', 'B', 'C']


# ---------------------------------------------------------------------------
# gen_feature
# ---------------------------------------------------------------------------

def test_gen_feature_flat():
    feature = gen_feature({'Male': 0.49, 'Female': 0.51})
    assert feature in ('Male', 'Female')


def test_gen_feature_nested_joins_path():
    feature = gen_feature({'White': {'British': 1.0}})
    assert feature == 'British, White'


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


def test_gen_samples_invalid_location_returns_empty():
    samples = gen_samples('nonexistent_place', N=1)
    assert samples == []


def test_gen_samples_relationship_only_if_age_16_plus():
    # Run many times to catch a variety of ages including under-16
    for _ in range(50):
        sample = gen_samples('england', N=1)[0]
        if sample.get('age', 16) < 16:
            assert 'relationship' not in sample
