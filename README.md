# Persona

**Make your characters more representative and realistic.** 

A REST API, CLI tool and Python package for probabilistically generating random character profiles from a given input location using real-world demographic data. Generating a new persona rolls the dice on features such as age, sex, sexuality, ethnicity, language and religion. This project was born out of a lack of tools for building representative and realistic characters for stories.

<p align="center">
	<img src="https://user-images.githubusercontent.com/41476809/200411754-969a4cc5-12de-4d3d-9189-bd258270cfc6.png">
</p>

## REST API

### Generate Persona

```
https://persona-api.vercel.app/v1/<location>/
```

```bash
$ curl https://persona-api.vercel.app/v1/england/

[
  {
    "age": 21,
    "sex": "Female",
    "sexuality": "Heterosexual",
    "ethnicity": "British, White",
    "religion": "Christianity",
    "language": "English",
    "occupation": "Skilled trades",
    "education": "Level 4+",
    "marital status": "Single (never married)",
    "housing tenure": "Social rented",
    "country of birth": "UK",
    "location": "Oldham, North West"
  }
]

```

#### Count Query

Multiple personas from the same location can be generated at once by providing a `count` query parameter (max 100).

```
https://persona-api.vercel.app/v1/<location>/?count=5
```

#### Feature Filtering

Limit the response to specific features using the `features` query parameter.

```
https://persona-api.vercel.app/v1/<location>/?features=age,sex,religion
```

#### Reproducible Output

Pass a `seed` integer to get the same persona(s) back every time.

```
https://persona-api.vercel.app/v1/<location>/?seed=42
```

### List Locations

All locations currently included can be listed with the `/v1/locations/` endpoint.

```bash
https://persona-api.vercel.app/v1/locations/
```

```bash
$ curl https://persona-api.vercel.app/v1/locations/

[
  "australia",
  "canada",
  "germany",
  "global",
  "united_kingdom",
  "england",
  "london",
  "northern_ireland",
  "scotland",
  "wales",
  "california",
  "florida",
  "texas",
  ...
]

```

### Location Features

Currently, not all features are available for each location. For a given location, all features available for generation can be retrieved with the `/v1/<location>/features/` endpoint.

```
https://persona-api.vercel.app/v1/<location>/features/
```

```bash
$ curl https://persona-api.vercel.app/v1/england/features/

{
  "england": [
    "age",
    "sex",
    "sexuality",
    "ethnicity",
    "religion",
    "language",
    "occupation",
    "education",
    "marital status",
    "housing tenure",
    "country of birth",
    "location"
  ]
}
```

## Command-line Tool

### Installation

With [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/tom-draper/persona.git

# or locally...
git clone https://github.com/tom-draper/persona.git
cd persona
uv tool install .

persona <location>
```

With pip:

```bash
pip install git+https://github.com/tom-draper/persona.git

# or locally...
git clone https://github.com/tom-draper/persona.git
cd persona
pip install .

persona <location>
```

### Generate Persona

```bash
persona <location>
```

Limit to specific features using feature flags:

```bash
persona <location> --age --sex --language
```

Generate multiple personas at once with `-n`:

```bash
persona <location> -n <count>
```

Output as JSON (useful for scripting):

```bash
persona <location> --json
```

Use `--seed` for reproducible output:

```bash
persona <location> --seed 42
```

List all available locations:

```bash
persona --list
```

### Example

```bash
persona united_kingdom

> United Kingdom
Age: 48
Sex: Female
Sexuality: Heterosexual
Ethnicity: British, White
Religion: No religion
Language: English
Location: Blackburn with Darwen, North West, England
```

## Python Package

```bash
pip install persona
```

```python
import persona

persona.generate("wales")
```

```python
{'age': 34, 'sex': 'Female', 'sexuality': 'Heterosexual', 'ethnicity': 'British, White',
 'religion': 'No religion', 'language': 'English', 'occupation': 'Caring, leisure and other services',
 'education': 'Level 3', 'marital status': 'Married', 'housing tenure': 'Owned with mortgage',
 'country of birth': 'Wales', 'location': 'Conwy'}
```

Personas are plain dictionaries, so they are JSON-serialisable and work with
`pandas` or anything else that takes records.

### Generating in Bulk

`generate_many` is considerably faster than looping over `generate`, which
re-reads the location's data on each call.

```python
people = persona.generate_many("united_kingdom", 1000)
```

### Feature Filtering

```python
persona.generate("wales", features={"age", "sex", "religion"})
```

```python
{'age': 71, 'sex': 'Male', 'religion': 'Christianity'}
```

### Reproducible Output

```python
persona.generate("england", seed=42) == persona.generate("england", seed=42)  # True
```

### Discovering What Is Available

```python
persona.locations()          # ['australia', 'california', 'canada', 'england', ...]
persona.features("canada")   # {'age', 'education', 'ethnicity', 'housing tenure', ...}
persona.features()           # every feature across all datasets
```

Feature coverage varies by location: UK datasets carry `sexuality`, Canada does
not. `persona.features(location)` tells you what a given location supports.

### Error Handling

```python
try:
    persona.generate("canada", features={"sexuality"})
except persona.UnknownFeatureError as e:
    print(e.invalid)     # ['sexuality']
    print(e.available)   # ['age', 'education', 'ethnicity', ...]
```

`UnknownLocationError` and `UnknownFeatureError` both derive from
`persona.PersonaError`, and from `ValueError` for backwards compatibility.

The package ships type annotations (`py.typed`), so `mypy` and `pyright` will
type-check calls against it.

## Data

The demographic data is carefully sourced from reputable census data for each location. Sources for each location can be found alongside the data in each `README.md` in `src/persona/data/`. The data is stored in a raw JSON format to make it as transparent, accessible and modifiable as possible.

### Locations

The full list of locations currently available can be found [here](src/persona/data/README.md). It includes countries, groups of locations (e.g. UK, USA), and cities. More locations and features will continue to be added in future.

## Limitations

Personas generated are basic <b>approximations</b>. Character features are naively generated under the assumption that each feature is independent from one another. This assumption is not true; knowing a person's age could help you better predict their religion. However, the sourcing of accurate and large scale data necessary for the joint probabilities for all feature combinations is exponentially harder to achieve. As a result, generated characters should be taken with a pinch of salt, and very occasionally personas will be generated that have a combination of features that may seem extremely unlikely or even impossible. Obviously, the fewer features included in the persona, the easier it is to approximate, and the less likely this is to occur.

Demographic data can change quite rapidly, and surveys take a long time to conduct, so the data used to generate profiles will always be somewhat outdated. Although, I still believe using outdated data in this way is an improvement over manual character creation in terms of representation as it will bypass any biases or misconceptions you may hold.

With this aim, this project is only as good as its data. There will certainly be minorities that make up a tiny proportion of the population that are missing from survey data (or grouped into an 'other' category) and therefore cannot surface during character generation. Improvement to data is an imperative and continuous goal for this project.

## Contributions

Contributions, issues and feature requests are welcome.

1. Fork it (https://github.com/tom-draper/persona)
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am "Add some feature"`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new pull request
