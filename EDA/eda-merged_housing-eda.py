import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

print("\n==============================")
print(" LOADING DATASET")
print("==============================\n")

df_raw = pd.read_csv("datasets/final-usables/merged_housing_dataset.csv")

# new df focusing only on (5-digit) ZIP codes - removing the county and borough rows
df = df_raw[df_raw['name'].str.match(r'^\d{5}$')].copy()
df['zipcode'] = df['name']

df = df[(df['median_gross_rent'] > 0) & (df['median_household_income'] > 0)]

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


print("\n==============================")
print(" RENT & INCOME OVERVIEW")
print("==============================\n")

print("--- Median Gross Rent ---")
print(df['median_gross_rent'].describe())

print("\n--- Median Household Income ---")
print(df['median_household_income'].describe())

# Rent Distribution Plot
plt.figure(figsize=(9,5))
plt.hist(df['median_gross_rent'], bins=25, color='skyblue', edgecolor='black', label="ZIP Codes")
plt.title("Distribution of Median Gross Rent")
plt.xlabel("Monthly Rent ($)")
plt.ylabel("Count")
plt.legend()
plt.tight_layout()
plt.savefig('EDA/housing_rent_dist.png')

print("\n==============================")
print(" RENT BURDEN ANALYSIS")
print("==============================\n")

# Calculating % of households with Severe Rent Burden (spending >50% of income on rent)
df['severe_rent_burden_pct'] = (df['rent_50pct_or_more_income'] / df['rent_burden_total_renter_households']) * 100
print("Severe Rent Burden Statistics (% spending >50% income):")
print(df['severe_rent_burden_pct'].describe())

# Income vs. Severe Rent Burden Plot
plt.figure(figsize=(8,6))
sns.regplot(data=df, x='median_household_income', y='severe_rent_burden_pct', 
            scatter_kws={'alpha':0.5, 'color':'purple'}, line_kws={'color':'red'})
plt.title("Income vs. Severe Rent Burden")
plt.xlabel("Median Household Income ($)")
plt.ylabel("% Households spending >50% on Rent")
plt.tight_layout()
plt.savefig('EDA/housing_income_vs_burden.png')


print("\n==============================")
print(" RENT BURDEN SCALE ANALYSIS")
print("==============================\n")
# Low Burden: < 20% of income
df['burden_low_pct'] = ((df['rent_lt_10pct_income'] + 
                         df['rent_10_to_14_9pct_income'] + 
                         df['rent_15_to_19_9pct_income']) / df['rent_burden_total_renter_households']) * 100
# Moderate Burden: 20% - 30% of income
df['burden_moderate_pct'] = ((df['rent_20_to_24_9pct_income'] + 
                              df['rent_25_to_29_9pct_income']) / df['rent_burden_total_renter_households']) * 100
# High Burden: 30% - 50% of income
df['burden_high_pct'] = ((df['rent_30_to_34_9pct_income'] + 
                           df['rent_35_to_39_9pct_income'] + 
                           df['rent_40_to_49_9pct_income']) / df['rent_burden_total_renter_households']) * 100
# Severe Burden: > 50% of income (already calculated as severe_rent_burden_pct)
df['burden_severe_pct'] = df['severe_rent_burden_pct']

# Calculating Dataset Averages for the Scale
burden_scale_means = {
    'Low (<20%)': df['burden_low_pct'].mean(),
    'Moderate (20-30%)': df['burden_moderate_pct'].mean(),
    'High (30-50%)': df['burden_high_pct'].mean(),
    'Severe (>50%)': df['burden_severe_pct'].mean()
}

print("Average Rent Burden Scale across all ZIP codes:")
for category, value in burden_scale_means.items():
    print(f"{category}: {value:.2f}%")

# Pie Chart Visualizing Scale
plt.figure(figsize=(8,8))
colors = ['#66b3ff','#99ff99','#ffcc99','#ff9999'] # Blue, Green, Orange, Red
plt.pie(burden_scale_means.values(), labels=burden_scale_means.keys(), 
        autopct='%1.1f%%', startangle=140, colors=colors, explode=(0.05, 0, 0, 0.1))

plt.title("Average NYC Rent Burden Scale")
plt.tight_layout()
plt.savefig('EDA/housing_burden_scale_pie.png')

# Stacked Bar for top 10 ZIPs Visualizing Scale
top_10_zips = df.nlargest(10, 'median_gross_rent')
top_10_zips[['name', 'burden_low_pct', 'burden_moderate_pct', 'burden_high_pct', 'burden_severe_pct']].set_index('name').plot(
    kind='bar', stacked=True, figsize=(12,7), color=colors)

plt.title("Rent Burden Scale in the 10 Most Expensive ZIP Codes")
plt.ylabel("Percentage of Renter Households")
plt.xlabel("ZIP Code")
plt.legend(title="Burden Level", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('EDA/housing_burden_scale_bars.png')


print("\n==============================")
print(" HOUSING AGE PROFILE")
print("==============================\n")

# List of housing age columns
age_cols = ['built_2020_or_later', 'built_2010_2019', 'built_2000_2009',
            'built_1990_1999', 'built_1980_1989', 'built_1970_1979',
            'built_1960_1969', 'built_1950_1959', 'built_1940_1949',
            'built_1939_or_earlier']

total_units_by_age = df[age_cols].sum().sort_index(ascending=False)

plt.figure(figsize=(10,6))
total_units_by_age.plot(kind='barh', color='darkgreen', label="Total Units")
plt.title("Total Housing Units by Construction Era")
plt.xlabel("Number of Units")
plt.ylabel("Year Built")
plt.legend()
plt.tight_layout()
plt.savefig('EDA/housing_age_profile.png')
