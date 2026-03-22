import geopandas as gpd
import pandas as pd
import os


geojson_folder_path = "./../datasets/tl_2025_us_county"
geojson_name = "borough.geo.json" #https://github.com/nycehs/NYC_geography/blob/master/borough.geo.json?short_path=75f3184

csv_folder_path = "./../datasets/final-usables"
csv_name = "merged_housing_dataset.csv"


geojson_path = os.path.join(geojson_folder_path, geojson_name)
csv_path = os.path.join(csv_folder_path, csv_name)

geo = gpd.read_file(geojson_path)

csv = pd.read_csv(csv_path)

def extract_county(name):
    first_part = str(name).split(',')[0].strip()
    # check if it ends with 'Borough'
    if first_part.endswith('borough'):
        # remove the last word ('Borough')
        return ' '.join(first_part.split(' ')[:-1]).strip()
    else:
        # otherwise, leave as-is
        return first_part

csv = csv.copy()

csv['county'] = csv['name'].apply(extract_county)

geo = geo.copy()
#geo = geo[geo['STATEFP'] == '36']
geo['BoroName'] = geo['BoroName'].astype(str).str.strip() # example -- "BoroName":"Queens"
geo = geo.merge(csv, left_on='BoroName', right_on='county', how='inner')

# geo = geo.drop(columns=['name'])

output_file = os.path.join(csv_folder_path, "merged_nyc_county.geojson")
geo.to_file(output_file, driver="GeoJSON")

print("Merge complete. Saved to:", output_file)