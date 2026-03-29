import pandas as pd
import os

# Loading Dataframes
csv_folder_path = "./../datasets"
csv_name = "ZipCode - Merged Housing Dataset.csv"
csv_path = os.path.join(csv_folder_path, csv_name)

df = pd.read_csv(csv_path)
df = df.copy()


stab_folder_path = "./../datasets/final-usables"
stab_name = "final_zip_stabilization_dataset.csv"
stab_path = os.path.join(stab_folder_path, stab_name)

stab = pd.read_csv(stab_path)
stab = stab.copy()


df["zip"] = df["zip"].astype(str).str.zfill(5)
stab["zipcode"] = stab["zipcode"].astype(str).str.zfill(5)

df = df.merge(
    stab[["zipcode", "stabilization_share"]],
    left_on="zip",
    right_on="zipcode",
    how="left"
)

df["stabilization_share"] = df["stabilization_share"].fillna(0)
df = df.drop(columns=["zipcode"])

# List Features
print("Merged DF Features:")
print(df.columns.tolist())



# --- 1. Create borough dummy variables ---
df["borough_Manhattan"] = (df["borough"] == "Manhattan").astype(int)
df["borough_Queens"] = (df["borough"] == "Queens").astype(int)
df["borough_Staten_Island"] = (df["borough"] == "Staten Island").astype(int)

df["vacancy_rate"] = df["vacant_units"] / df["housing_units_total"].replace(0, pd.NA)
df["homeownership_rate"] = df["owner_occupied_units"] / df["occupied_units"].replace(0, pd.NA)
df[["vacancy_rate", "homeownership_rate"]] = df[["vacancy_rate", "homeownership_rate"]].fillna(0)


# --- 2. Predicted rent WITH stabilization ---
df["predicted_rent_with_stab"] = (
    901.233
    + 0.013 * df["median_household_income"]
    + 0.074 * df["built_2010_2019"]
    + 0.135 * df["built_1980_1989"]
    + 640.627 * df["vacancy_rate"]
    - 27.327 * df["borough_Manhattan"]
    + 118.401 * df["borough_Queens"]
    - 233.030 * df["borough_Staten_Island"]
    - 0.118 * df["built_1990_1999"]
    - 0.167 * df["rent_lt_10pct_income"]
    - 599.515 * df["homeownership_rate"]
    - 0.297 * df["built_2020_or_later"]
    + 0.057 * df["rent_not_computed"]
    + 22.971 * df["stabilization_share"]
)

# --- 3. Predicted rent WITHOUT stabilization ---
df["predicted_rent_without_stab"] = (
    df["predicted_rent_with_stab"]
    - 22.971 * df["stabilization_share"]
)

# --- 4. difference column ---
df["stabilization_effect"] = (
    df["predicted_rent_with_stab"]
    - df["predicted_rent_without_stab"]
)


# Saving File


output_path = "../datasets/final-usables/final_merged_nyc_zip.csv"

print("Saving to:", os.path.abspath(output_path))

df.to_csv(output_path, index=False)

print("File exists after save:", os.path.exists(output_path))


#output_file = os.path.join("./../datasets/final-usables/final-usables", "final_merged_nyc_zip.csv")
#print("Merge complete. Saved to:", output_file)