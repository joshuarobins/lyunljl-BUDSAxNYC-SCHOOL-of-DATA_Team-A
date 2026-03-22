import geopandas as gpd
import pandas as pd
import os


geojson_folder_path = "./../datasets/tl_2023_us_zcta520"
geojson_name = "tl_2023_us_zcta520.geojson"

csv_folder_path = "./../datasets/final-usables"
csv_name = "merged_housing_dataset.csv"


geojson_path = os.path.join(geojson_folder_path, geojson_name)
csv_path = os.path.join(csv_folder_path, csv_name)

geo = gpd.read_file(geojson_path)

csv = pd.read_csv(csv_path)

csv = csv.copy()
csv['name'] = csv['name'].astype(str).str.zfill(5)

geo = geo.copy()
geo['GEOID20'] = geo['GEOID20'].astype(str).str.strip()
geo = geo.merge(csv, left_on='GEOID20', right_on='name', how='inner')

geo = geo.drop(columns=['name'])

output_file = os.path.join(csv_folder_path, "merged_nyc_zcta.geojson")
geo.to_file(output_file, driver="GeoJSON")

print("Merge complete. Saved to:", output_file)