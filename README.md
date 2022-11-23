# Persona

A tool for probabilistically generating random character profiles based from a given location using real-world demographic data. Generating a new persona rolls the dice on features such as age, sex, sexuality, ethnicity, language and religion. This project was born out of a lack of tools for building representative, inclusive and realistic characters for stories.

<p align="center">
	<img src="https://user-images.githubusercontent.com/41476809/200411754-969a4cc5-12de-4d3d-9189-bd258270cfc6.png">
</p>

## REST API

### Generate Persona

```
https://persona-api.vercel.app/v1/<location>/
```

```bash
> curl https://persona-api.vercel.app/v1/england/
[
  {
    "age": 21,
    "sex": "Female",
    "sexuality": "Heterosexual",
    "ethnicity": "British, White",
    "religion": "Christian",
    "language": "English",
    "location": "Oldham, North West"
  }
]

```

#### Count Query

Multiple personas from the same location can be generated at once by providing a `count` query parameter.

```
https://persona-api.vercel.app/v1/<location>/?count=5
```

### List Locations

All locations currently included can be listed with the `/locations/` endpoint.

```bash
https://persona-api.vercel.app/v1/locations/
```

```bash
> curl https://persona-api.vercel.app/v1/locations/
[
  "united_kingdom",
  "england",
  "london",
  "northern_ireland",
  "scotland",
  "wales"
]

```

### Location Features

For a given location, all possible features available to generate can be listed with the `/<location>/features/` endpoint.

```
https://persona-api.vercel.app/v1/<location>/features/
```

```bash
> curl https://persona-api.vercel.app/v1/england/features/
[
  "age",
  "sex",
  "sexuality",
  "religion",
  "ethnicity",
  "language",
  "location"
]
```

## Command-line Tool

### Installation

Install Python dependencies from `requirements.txt`.

```py
python -m pip install -r requirements.txt
```

### Generate Persona

Run `main.py` from the root directory.

```py
python src/main.py <location>
```

The generated persona can be limited to specific features using the feature flags to include.

```py
python src/main.py <location> --age --location --language
```

Multiple personas can be generated at once using the `-n` flag.

```py
python src/main.py <location> -n <count>
```

### Example

```bash
python src/main.py england

> England
Age: 48
Sex: Female
Sexuality: Heterosexual
Ethnicity: British, White
Religion: No religion
Language: English
Location: Blackburn with Darwen, North West
```

## Data

The demographic data is carefully sourced from reputable organisations for each location. Sources for each location can be found alongside the data in each `README.md` in `/data`.

### Locations

Currently 6 countries are available for persona generation. More countries and features will continue to be included in future.

- [ ] `united_states_of_america` / `usa`
- [x] `united_kingdom` / `uk`
- [x] `england`
- [x] `wales`
- [x] `scotland`
- [x] `northern_ireland`
- [ ] `france`
- [ ] `germany`
- [ ] `spain`
- [ ] `italy`
- [ ] `ireland`
- [X] `australia`
- [X] `canada`
- [ ] `brazil`
- [ ] `mexico`
- [ ] `russia`
- [ ] `china`
- [ ] `india`
- [ ] `nigeria`

## Limitations

Personas generated are basic approximations. Features generated for a single persona are generated under the assumption that each feature is independent from one another. This naive approach is not ideal, as, for example, knowing a person's age could help you better predict their religion. However, the sourcing of accurate and large scale data necessary for the joint probabilities for all feature combinations is exponentially harder to achieve. As a result, very occasionally personas will be generated that have a combination of features that may seem extremely unlikely. The fewer feature included in the persona, the less likely this is to occur.
