import pandas as pd

df = pd.read_csv("datasets/final-usables/merged_housing_dataset.csv")

print("\n=== BASIC SHAPE ===")
print(df.shape)
print(df.columns.tolist())

print("\n=== MISSING GEOID ===")
print(df["geoid"].isna().sum())

print("\n=== DUPLICATE GEOID ===")
print(df["geoid"].duplicated().sum())

print("\n=== MISSING NAME ===")
print(df["name"].isna().sum())

print("\n=== SAMPLE ROWS ===")
print(df[df["geoid"] == "06000US3600508510"][["geoid", "name"]])
print(df[df["geoid"] == "16000US3651000"][["geoid", "name"]])
print(df[df["geoid"] == "86000US07024"][["geoid", "name"]])

print("\n=== CHECK EXPECTED COLUMNS ===")
expected_cols = [
    "geoid",
    "name",
    "rent_burden_total_renter_households",
    "housing_units_total",
    "median_gross_rent",
    "median_household_income",
    "occupancy_total_units",
    "occupied_units",
    "vacant_units",
    "tenure_total_occupied_units",
    "owner_occupied_units",
    "renter_occupied_units",
    "total_population",
    "year_built_total_units"
]

missing = [col for col in expected_cols if col not in df.columns]
print("Missing expected columns:", missing)

print("\n=== CHECK NO OLD ACS CODES LEFT FOR MAIN COLUMNS ===")
old_cols = [
    "B25070001",
    "B25001001",
    "B25064001",
    "B19013001",
    "B25002001",
    "B25003001",
    "B01003001",
    "B25034001"
]
still_old = [col for col in old_cols if col in df.columns]
print("Old ACS columns still present:", still_old)

print("\n=== CHECK NO ERROR COLUMNS LEFT ===")
error_cols = [col for col in df.columns if "Error" in col]
print("Error columns:", error_cols)

print("\n=== LOGIC CHECKS ===")
# owner + renter should equal total occupied tenure
tenure_check = df[
    (
        df["owner_occupied_units"].fillna(0)
        + df["renter_occupied_units"].fillna(0)
    ) != df["tenure_total_occupied_units"].fillna(0)
][[
    "geoid", "name", "tenure_total_occupied_units",
    "owner_occupied_units", "renter_occupied_units"
]]
print("Tenure mismatches:", len(tenure_check))
print(tenure_check.head())

# occupied + vacant should equal total housing units
occupancy_check = df[
    (
        df["occupied_units"].fillna(0)
        + df["vacant_units"].fillna(0)
    ) != df["occupancy_total_units"].fillna(0)
][[
    "geoid", "name", "occupancy_total_units",
    "occupied_units", "vacant_units"
]]
print("Occupancy mismatches:", len(occupancy_check))
print(occupancy_check.head())

# total renter households should equal sum of rent burden categories
rent_cols = [
    "rent_lt_10pct_income",
    "rent_10_to_14_9pct_income",
    "rent_15_to_19_9pct_income",
    "rent_20_to_24_9pct_income",
    "rent_25_to_29_9pct_income",
    "rent_30_to_34_9pct_income",
    "rent_35_to_39_9pct_income",
    "rent_40_to_49_9pct_income",
    "rent_50pct_or_more_income",
    "rent_not_computed"
]

rent_check = df[
    df[rent_cols].fillna(0).sum(axis=1) != df["rent_burden_total_renter_households"].fillna(0)
][[
    "geoid", "name", "rent_burden_total_renter_households"
] + rent_cols]
print("Rent burden mismatches:", len(rent_check))
print(rent_check.head())