# Persona

A tool for probabilistically generating character profiles based on a given location using real-world demographic data, with features including age, sex, sexuality, ethnicity and religion. This project was originally intended for building representative and inclusive characters for stories.

<p align="center">
	<img src="https://user-images.githubusercontent.com/41476809/200411754-969a4cc5-12de-4d3d-9189-bd258270cfc6.png">
</p>

## Usage

First install the Python dependencies listed inside the `requirements.txt` file.

```py
python -m pip install -r requirements.txt
```

Then run the program.

```py
python src/main.py <location>
```

The persona can be limited to specific features using flags.

```py
python src/main.py <location> --age --location --language
```

The number of personas generated can be increased using the `-n` flag.

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

### Locations

- [ ] United States of America
- [x] United Kingdom
- [x] England
- [x] Wales
- [x] Scotland
- [x] Northern Ireland
- [ ] France
- [ ] Germany
- [ ] Spain
- [ ] Italy
- [ ] Ireland
- [ ] Canada
- [ ] Brazil
- [ ] Mexico
- [ ] Russia
- [ ] China
- [ ] India

## Data

The demographic data is carefully sourced from reputable organisations for each country. Citations for each feature for each country can be found in the `README.md` in `/data`.

## Limitations

The personas generated are approximations. If multiple features are generated for a single persona, then they have been generated under the assumption that are entirely independent of each other. This naive approach is not ideal, as, for example, knowing a person's age could help you better predict their religion. However, the sourcing of accurate and large scale data necessary for the joint probabilities for all feature combinations makes this highly difficult to achieve. As a result, occasionally personas will be generated that have a combination of features that may seem extremely unlikely.
