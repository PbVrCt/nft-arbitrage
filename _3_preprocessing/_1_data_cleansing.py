import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_context("paper")
sns.set_theme()

# Overwrites loads function due to this issue: https://github.com/pandas-dev/pandas/issues/26068
import json

pd.io.json._json.loads = lambda s, *a, **kw: json.loads(s)
#

# Load the data
df = pd.read_json(f"./data/full_raw.json")

# Check the number or rows
print(df.head())
print("\nTotal rows: ", df.shape[0])
# Drop duplicaterows
df = df.drop_duplicates(["Id", "PriceUSD"]).set_index(["Id", "PriceUSD"])
print("Total rows wtihout duplicates: ", df.shape[0])
# Drop empty rows
df["Class"].replace("", np.nan, inplace=True)
df.dropna(subset=["Class"], inplace=True)
# Drop prices above treshold
df = df[df["PriceBy100"] < 40].copy()
print("Total rows below price treshold: ", df.shape[0])

# Subsample, weighting by the 'class' feature; so that the less frequent classes are weighted more
probs = 1 / df["Class"].map(df["Class"].value_counts())
df = df.sample(n=int(df.shape[0] * 0.6), weights=probs)
print("Total rows after subsampling by class: ", df.shape[0])

# # Subsample, weighting more the less frequent prices
# probs = 1 / df["PriceBy100"].map(df["PriceBy100"].value_counts(normalize=True)) + 1
# df = df.sample(n=int(df.shape[0] * 0.6), weights=probs)
# print("Total rows after subsampling by price: ", df.shape[0])

features = df.loc[:, df.columns.difference(["Priceby100", "PriceUSD"])]
labels = df.loc[:, "PriceBy100"]

# Check the data after cleansing and subssampling. Outliers, class frequencies, and price distributions
assert df.index[np.isinf(df.select_dtypes(np.number)).any(1)].empty  # No infs
assert df.index[np.isnan(df.select_dtypes(np.number)).any(1)].empty  # No nans
fig, axes = plt.subplots(2, 2, figsize=(13, 13))
sns.boxplot(data=features.loc[:, ["BreedCount"]], orient="h", ax=axes[0, 0])
sns.kdeplot(data=labels, ax=axes[0, 1])
sns.countplot(x="Class", data=df, ax=axes[1, 0])
sns.kdeplot(data=df, x="PriceBy100", hue="Class", fill=True, ax=axes[1, 1])

# Save the data
df.to_csv(f"./data/full_cleansed.csv")
print("\nSaved")

plt.show()
# # Unsupervised anomaly detection model
# ANOMALY_QUANTILE = 0.05  #  "auto"
# model_isof = IsolationForest(
#     n_estimators=1000,
#     max_samples="auto",
#     contamination=ANOMALY_QUANTILE,
#     n_jobs=-1,
#     random_state=123,
# )
# model_isof.fit(X=labels.to_numpy().reshape(-1, 1))

# # Show the anomaly score distribution
# anomaly_score = model_isof.score_samples(X=labels.to_numpy().reshape(-1, 1))
# quantile_01 = np.quantile(anomaly_score, q=ANOMALY_QUANTILE)
# sns.displot(
#     data=anomaly_score,
#     kind="kde",
#     color="blue",
#     height=5,
#     aspect=2,
# ).set(title="Distribution of anomaly values", xlabel="Anomaly score")
# plt.axvline(quantile_01, c="red", linestyle="--", label="0.01 quantile")
# plt.draw()
# plt.pause(10)

# # Discard anomalies      -1 = anomaly, 1 = ok
# anomaly_prediction = model_isof.predict(X=labels.to_numpy().reshape(-1, 1))
# df = df.loc[(anomaly_prediction != -1), :]
# print("Total rows after discarding anomalies: ", df.shape[0])
