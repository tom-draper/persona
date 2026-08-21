from persona.lib.generate import gen_samples, list_all_features, list_locations


def generate(
    location: str,
    *,
    count: int = 1,
    features: set[str] | None = None,
    seed: int | None = None,
) -> list[dict]:
    """Generate one or more personas for a location.

    Args:
        location: Target location, such as ``"england"``.
        count: Number of personas to generate.
        features: Optional set of features to include.
        seed: Optional random seed for reproducible output.
    """
    return gen_samples(location, enabled_features=features, N=count, seed=seed)


__all__ = ["gen_samples", "generate", "list_all_features", "list_locations"]
