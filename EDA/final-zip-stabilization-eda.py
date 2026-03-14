import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("\n==============================")
print(" LOADING DATASET")
print("==============================\n")

df = pd.read_csv("datasets/final-usables/final_zip_stabilization_dataset.csv", low_memory=False)

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n==============================")
print(" COLUMN OVERVIEW")
print("==============================\n")

print(df.columns.tolist())

print("\nData types:\n")
print(df.dtypes)

print("\nSummary Statistics:\n")
print(df.describe())


plt.figure()
plt.hist(df["total_units"], bins=30)
plt.title("Total Units by ZIP")
plt.xlabel("Total Units")
plt.ylabel("ZIP Codes")

plt.xscale("log")


plt.figure()
plt.hist(df["stabilization_share"], bins=30)
plt.title("Stabilization Share Distribution")
plt.xlabel("Share")
plt.ylabel("ZIP Codes")

print("\n==============================")
print(" RANKING ANALYSIS")
print("==============================\n")

print("Top ZIPs by Stabilization Share:\n")
print(df.sort_values("stabilization_share", ascending=False).head(10))

print("\nTop ZIPs by Total Stabilized Units:\n")
print(df.sort_values("stabilized_units", ascending=False).head(10))

plt.figure()
plt.scatter(df["total_units"], df["stabilized_units"], alpha=0.6)
plt.xlabel("Total Units")
plt.ylabel("Stabilized Units")
plt.title("Total vs Stabilized Units")


plt.figure()
plt.scatter(df["total_buildings"], df["stabilized_buildings"], alpha=0.6)
plt.xlabel("Total Buildings")
plt.ylabel("Stabilized Buildings")
plt.title("Total vs Stabilized Buildings")


plt.figure()
plt.scatter(df["total_units"], df["stabilization_share"], alpha=0.6)
plt.xlabel("Total Units")
plt.ylabel("Stabilization Share")
plt.title("ZIP Size vs Stabilization Share")

print("\n==============================")
print(" CORRELATION MATRIX")
print("==============================\n")

df.drop(columns=["zipcode"]).corr()
print(df.corr())


plt.figure()
sns.heatmap(df.corr(), annot=True)


print("\n==============================")
print(" CONCENTRATION ANALYSIS")
print("==============================\n")

print("% of stabilized units come from top 10 ZIPs:")
top10 = df.sort_values("stabilized_units", ascending=False).head(10)
print(top10["stabilized_units"].sum() / df["stabilized_units"].sum())


print("\nTotal Units per Quantile:")
quantiles = df["total_units"].quantile([0.5, 0.75, 0.9, 0.95, 0.99])
for q, value in quantiles.items():
    print(f"{int(q*100)}% quantile: {int(value):,} units")


plt.show()