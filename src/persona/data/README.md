# Data

## Schema

Every dataset is a JSON object of demographic features plus a `_meta.sources`
list. A feature is a distribution: either `{label: weight}`, or nested
`{region: {sub-region: weight}}` for `location`. Weights are population shares;
a feature's weights should sum to roughly 1 (long tails are routinely
truncated, so falling short is fine — exceeding 1 is not). Every feature must be
attributed to a source in `_meta.sources`, and every source must give
`features`, `name`, an `https://` `url`, and an integer `year`.

Features fall into two tiers.

**Core** features are meant to generalise to every place and are being brought
to parity across all datasets:

| Feature | Values |
| --- | --- |
| `age` | Five-year bands `0-4` … `80-84`, open-ended `85+`, contiguous from 0. |
| `sex` | `Male`, `Female`. |
| `religion` | Canonical labels (`Roman Catholicism`, `Islam`, `No religion`, …). |
| `residence` | `Urban`, `Rural`. |
| `marital status` | `Single (never married)`, `Married`, `Cohabiting`, `Widowed`, `Divorced` (national datasets may add e.g. `Separated`, `Civil partnership (PACS)`). |
| `education` | Highest level attained. `No schooling`, `Primary education`, `Secondary education`, `Tertiary education` where harmonised; national datasets keep their own qualification framework (US degrees, UK levels, …). |
| `location` | Region (optionally nested), weighted by population. |

**Extended** features are kept wherever a good national source reports them, but
are *not* forced onto every dataset — coverage is inherently uneven across
countries:

`occupation`, `ethnicity`, `language`, `housing tenure`, `country of birth`,
`sexuality`.

`occupation` is now available for most countries from a single harmonised source
(see below), but it stays in the extended tier: it describes only *employed*
people (it is assigned to adults, alongside marital status), its labels are not
globally uniform, and a handful of countries have no labour-force survey.

Whatever tier it belongs to, a feature name means the same thing in every
dataset that carries it; the shared category labels are enforced by
`tests/test_data_integrity.py` (`CANONICAL_FEATURES` and `FORBIDDEN_LABELS`).
`education` is the one core feature whose *labels* are not globally uniform:
its meaning (highest level attained) is shared, but the harmonised datasets use
ISCED-style levels while datasets built from a national source keep that
country's qualification framework.

`residence` comes from the World Bank *Urban population (% of total)* series for
countries (one consistent method worldwide), the 2020 US Census urban/rural
split for the states, and is set to urban for the standalone city datasets. The
UK nations reuse the UK-wide World Bank figure because the four nations classify
rural and urban against different population thresholds.

`marital status`, where a national source does not supply it, comes from the UN
*World Marriage Data 2019*: the population-aged-15+ distribution for each
country's most recent census/survey (2002–2019), reweighted to that year's
age-sex structure. Consensual unions are reported as their own `Cohabiting`
category (large in much of Latin America); separated persons are counted with
`Divorced`. Because it leans on the latest available census, it is an
approximation and can differ from a country's current national figures by a few
points — the per-country source year is recorded in `_meta`.

`education`, where a national source does not supply it, comes from the
Wittgenstein Centre Human Capital Data Explorer (v3, SSP2, 2020): the population
aged 15 and over collapsed to no schooling, primary, secondary and tertiary as
the highest level attained.

`occupation`, where a national source does not supply it, comes from ILOSTAT
(International Labour Organization): the distribution of employed people across
the ISCO-08 (or, as a fallback, ISCO-88) major occupational groups, from each
country's most recent labour-force survey.

## Cities

A city is a partial dataset nested inside its country (or, for New York City,
its US state): it carries its own districts and is flagged urban, and inherits
every other feature from the parent. It is reached by bare name (`tokyo`) or
through the parent, which yields the city in proportion to its population share.

- [X] `london`
- [X] `paris`
- [X] `berlin`
- [X] `madrid`
- [X] `new_york_city` (`nyc`)
- [X] `tokyo`
- [X] `mexico_city` (`cdmx`)
- [X] `rome`

## Countries

- [X] `england`
- [X] `wales`
- [X] `scotland`
- [X] `northern_ireland`
- [X] `france`
- [X] `germany`
- [X] `spain`
- [X] `italy`
- [X] `ireland`
- [X] `australia`
- [X] `canada`
- [X] `brazil`
- [X] `mexico`
- [X] `russia`
- [X] `china`
- [X] `india`
- [X] `nigeria`
- [X] `indonesia`
- [X] `pakistan`
- [X] `bangladesh`
- [X] `japan`
- [X] `philippines`
- [X] `ethiopia`
- [X] `egypt`
- [X] `vietnam`
- [X] `iran`
- [X] `turkey`
- [X] `thailand`
- [X] `south_africa`
- [X] `south_korea`
- [X] `ukraine`
- [X] `poland`
- [X] `morocco`
- [X] `colombia`
- [X] `argentina`
- [X] `kenya`
- [X] `tanzania`
- [X] `democratic_republic_of_the_congo`
- [X] `myanmar`
- [X] `saudi_arabia`
- [X] `malaysia`
- [X] `iraq`
- [X] `afghanistan`
- [X] `uganda`
- [X] `algeria`
- [X] `sudan`
- [X] `angola`
- [X] `ghana`
- [X] `nepal`
- [X] `netherlands`
- [X] `belgium`
- [X] `portugal`
- [X] `yemen`
- [X] `mozambique`
- [X] `cote_divoire`
- [X] `madagascar`
- [X] `kazakhstan`
- [X] `czechia`
- [X] `hungary`
- [X] `austria`
- [X] `switzerland`
- [X] `romania`
- [X] `syria`
- [X] `sri_lanka`
- [X] `cameroon`
- [X] `north_korea`
- [X] `guatemala`
- [X] `ecuador`
- [X] `cambodia`
- [X] `mali`
- [X] `senegal`
- [X] `zambia`
- [X] `serbia`
- [X] `niger`
- [X] `burkina_faso`
- [X] `chad`
- [X] `somalia`
- [X] `zimbabwe`
- [X] `tunisia`
- [X] `bolivia`
- [X] `bulgaria`
- [X] `rwanda`
- [X] `benin`
- [X] `guinea`
- [X] `haiti`
- [X] `dominican_republic`
- [X] `jordan`
- [X] `azerbaijan`
- [X] `tajikistan`
- [X] `honduras`
- [X] `paraguay`
- [X] `el_salvador`
- [X] `slovakia`
- [X] `croatia`
- [X] `denmark`
- [X] `laos`
- [X] `georgia`
- [X] `papua_new_guinea`
- [X] `uruguay`
- [X] `panama`
- [X] `costa_rica`
- [X] `lebanon`
- [X] `oman`
- [X] `kuwait`
- [X] `mongolia`
- [X] `armenia`
- [X] `kyrgyzstan`
- [X] `moldova`
- [X] `lithuania`
- [X] `albania`
- [X] `bosnia_and_herzegovina`
- [X] `nicaragua`
- [X] `togo`
- [X] `turkmenistan`
- [X] `latvia`
- [X] `estonia`
- [X] `slovenia`
- [X] `north_macedonia`
- [X] `botswana`
- [X] `namibia`
- [X] `gabon`
- [X] `qatar`
- [X] `bahrain`
- [X] `cyprus`
- [X] `montenegro`
- [X] `eritrea`
- [X] `south_sudan`
- [X] `republic_of_the_congo`
- [X] `mauritania`
- [X] `liberia`
- [X] `sierra_leone`
- [X] `central_african_republic`
- [X] `lesotho`
- [X] `eswatini`
- [X] `jamaica`
- [X] `iceland`
- [X] `malta`
- [X] `djibouti`
- [X] `gambia`
- [X] `guinea_bissau`
- [X] `equatorial_guinea`
- [X] `bhutan`
- [X] `timor_leste`
- [X] `trinidad_and_tobago`
- [X] `fiji`
- [X] `greece`
- [X] `norway`
- [X] `finland`
- [X] `sweden`
- [X] `new_zealand`
- [X] `united_arab_emirates` / `uae`

## US States

- [X] `alabama`
- [X] `alaska`
- [X] `arizona`
- [X] `arkansas`
- [X] `california`
- [X] `colorado`
- [X] `connecticut`
- [X] `delaware`
- [X] `florida`
- [X] `georgia`
- [X] `hawaii`
- [X] `idaho`
- [X] `illinois`
- [X] `indiana`
- [X] `iowa`
- [X] `kansas`
- [X] `kentucky`
- [X] `louisiana`
- [X] `maine`
- [X] `maryland`
- [X] `massachusetts`
- [X] `michigan`
- [X] `minnesota`
- [X] `mississippi`
- [X] `missouri`
- [X] `montana`
- [X] `nebraska`
- [X] `nevada`
- [X] `new_hampshire`
- [X] `new_jersey`
- [X] `new_mexico`
- [X] `new_york`
- [X] `north_carolina`
- [X] `north_dakota`
- [X] `ohio`
- [X] `oklahoma`
- [X] `oregon`
- [X] `pennsylvania`
- [X] `rhode_island`
- [X] `south_carolina`
- [X] `south_dakota`
- [X] `tennessee`
- [X] `texas`
- [X] `utah`
- [X] `vermont`
- [X] `virginia`
- [X] `washington`
- [X] `west_virginia`
- [X] `wisconsin`
- [X] `wyoming`

## Composite Locations

A random sub-location is selected, weighted by population.

- [x] `united_states_of_america` / `usa` (California, Florida and Texas only)
- [x] `united_kingdom` / `uk`

## Global

The `global` location is a self-contained world-baseline dataset: it draws age and sex from the UN's world population estimates, religion from Pew's Global Religious Landscape, and a `location` that is a random country weighted by share of world population. It is deliberately **not** a composite over every country (that would only ever be as representative as the handful of countries with datasets). A future enhancement could layer the interior-composite mechanism on top so that when `global` lands on a country that does have a dataset, it yields that country's richer persona instead of the world baseline.

- [X] `global`
