# Data

## Cities

- [X] `london`
- [ ] `paris`
- [ ] `berlin`
- [ ] `madrid`

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
- [ ] `iran`
- [ ] `turkey`
- [ ] `thailand`
- [ ] `south_africa`
- [ ] `south_korea`
- [ ] `ukraine`
- [ ] `poland`
- [ ] `morocco`
- [ ] `greece`
- [ ] `norway`
- [ ] `finland`
- [ ] `sweden`
- [ ] `new_zealand`
- [ ] `united_arab_emirates` / `uae`

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
