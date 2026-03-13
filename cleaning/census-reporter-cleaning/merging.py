import pandas as pd
import glob
from functools import reduce

files = glob.glob("datasets/census-reporter-raw/*.csv")

dfs = []

for i, file in enumerate(files):
    df = pd.read_csv(file)
    df.columns = [c.strip() for c in df.columns]

    # drop margin-of-error columns
    df = df[[c for c in df.columns if "Error" not in c]]

    # rename later 'name' columns instead of dropping them
    if i > 0 and "name" in df.columns:
        df = df.rename(columns={"name": f"name_{i}"})

    dfs.append(df)

merged = reduce(lambda left, right: pd.merge(left, right, on="geoid", how="outer"), dfs)

# combine all name columns into one
name_cols = [c for c in merged.columns if c == "name" or c.startswith("name_")]
merged["name"] = merged[name_cols].bfill(axis=1).iloc[:, 0]

# drop extra name columns
extra_name_cols = [c for c in name_cols if c != "name"]
merged = merged.drop(columns=extra_name_cols)

# rename ACS columns to readable names
rename_map = {
    "B25070001": "rent_burden_total_renter_households",
    "B25070002": "rent_lt_10pct_income",
    "B25070003": "rent_10_to_14_9pct_income",
    "B25070004": "rent_15_to_19_9pct_income",
    "B25070005": "rent_20_to_24_9pct_income",
    "B25070006": "rent_25_to_29_9pct_income",
    "B25070007": "rent_30_to_34_9pct_income",
    "B25070008": "rent_35_to_39_9pct_income",
    "B25070009": "rent_40_to_49_9pct_income",
    "B25070010": "rent_50pct_or_more_income",
    "B25070011": "rent_not_computed",

    "B25001001": "housing_units_total",

    "B25064001": "median_gross_rent",

    "B19013001": "median_household_income",

    "B25002001": "occupancy_total_units",
    "B25002002": "occupied_units",
    "B25002003": "vacant_units",

    "B25003001": "tenure_total_occupied_units",
    "B25003002": "owner_occupied_units",
    "B25003003": "renter_occupied_units",

    "B01003001": "total_population",

    "B25034001": "year_built_total_units",
    "B25034002": "built_2020_or_later",
    "B25034003": "built_2010_2019",
    "B25034004": "built_2000_2009",
    "B25034005": "built_1990_1999",
    "B25034006": "built_1980_1989",
    "B25034007": "built_1970_1979",
    "B25034008": "built_1960_1969",
    "B25034009": "built_1950_1959",
    "B25034010": "built_1940_1949",
    "B25034011": "built_1939_or_earlier"
}

merged = merged.rename(columns=rename_map)

# put geoid and name first
front_cols = [col for col in ["geoid", "name"] if col in merged.columns]
other_cols = [col for col in merged.columns if col not in front_cols]
merged = merged[front_cols + other_cols]

merged.to_csv("datasets/final-usables/merged_housing_dataset.csv", index=False)

print("Merged dataset saved.")