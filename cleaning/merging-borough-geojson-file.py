import geopandas as gpd
import pandas as pd
import os

geojson_folder_path = "./../datasets/geojson-raw"
geojson_name = "borough.geo.json" #https://github.com/nycehs/NYC_geography/blob/master/borough.geo.json?short_path=75f3184

csv_folder_path = "./../datasets/final-usables"
csv_name = "Revised - Merged Housing Dataset (by Borough).csv"


geojson_path = os.path.join(geojson_folder_path, geojson_name)
csv_path = os.path.join(csv_folder_path, csv_name)

geo = gpd.read_file(geojson_path)

csv = pd.read_csv(csv_path)

csv = csv.copy()

geo = geo.copy()
geo['BoroName'] = geo['BoroName'].astype(str).str.strip() # example -- "BoroName":"Queens"
geo = geo.merge(csv, left_on='BoroName', right_on='borough', how='inner')

output_file = os.path.join(csv_folder_path, "merged_nyc_county.geojson")
geo.to_file(output_file, driver="GeoJSON")

print("Merge complete. Saved to:", output_file)