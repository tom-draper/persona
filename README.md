# Persona

A easy tool to probabilistically generate personas based on an input location using real world demographic data, with features including age, sex, sexuality and ethnicity. This project was originally intended for building representative and inclusive characters for stories.

## Usage

First install the Python dependencies listed inside the `requirements.txt` file.

```py
python3 -m pip install -r requirements.txt
```

Then run the program.

```py
python3 main.py <location>
```

The persona can be limited to specific features using flags.

```py
python3 main.py <location> --age --location --language
```

### Example

```bash
main.py england

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
- [ ] United Kingdom
- [x] England
- [x] Wales
- [ ] Scotland
- [ ] Northern Ireland
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

The data is carefully sourced from reputable surveyors for each country. Citations for each feature for each country can be found in the `README.md` in `/data`.

## Note

Persona generated are approximations. If multiple features are generated for a single persona, they have been generated under the assumption that are independent of each other. This naive approach is not ideal, as for example, knowing a person's age could help you better predict their religion, however, the availability of accurate and large scale data necessary for the joint probabilities for all feature combinations makes this highly difficult to achieve. As a result, occasionally personas will be generated that have a combination of features that seems extremely unlikely. More realistic approximations are generated the fewer the number of included features.
