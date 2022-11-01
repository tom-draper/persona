# Persona

A tool to probabilistically generate representative personas, with features including age, sex, sexuality and ethnicity, based on an input location using real world demographic data. This project was originally intended for building representative and inclusive characters for stories.

## Usage

```py
main.py <location>
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

- [x] England
- [x] Wales
- [ ] Scotland
- [ ] Northern Ireland
- [ ] Ireland
- [ ] France
- [ ] Germany
- [ ] Spain
- [ ] Italy
- [ ] Portugal
- [ ] USA
- [ ] Canada
- [ ] Brazil
- [ ] Columbia
- [ ] Mexico
- [ ] Russia
- [ ] China
- [ ] India

## Note

Persona generated are approximations. If multiple features are generated for a single persona, they have been generated under the assumption that are independent of each other. This naive approach is not ideal, as for example, knowing a person's age could help you better predict their religion, however, the availability of accurate and large scale data necessary for the joint probabilities for all feature combinations makes this highly difficult to achieve. As a result, occasionally personas will be generated that have a combination of features that seems extremely unlikely. More realistic approximations are generated the fewer the number of included features.
