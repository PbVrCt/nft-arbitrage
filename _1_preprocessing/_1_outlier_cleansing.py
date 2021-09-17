# TODO: Using AWS, the RandomCutForest algorithm is available, which can be useful for anomaly detection in streaming data, unlike this one
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_context("paper")
sns.set_theme()

# Check the number or rows, drop duplicate rows, drop prices above treshold
df = pd.read_json(f"./data/full_raw.json")
print("\nTotal rows: ", df.shape[0])
df = df.drop_duplicates(subset=["Id", "Price"]).drop(columns=["Id"])
print("Total rows wtihout duplicates: ", df.shape[0])
df = df[df["Price"] < 800].copy()
print("Total rows wtih prices below 800: ", df.shape[0])

# Subsample, weighting more the less frequent classes
probs = 1 / df["Class"].map(df["Class"].value_counts())
df = df.sample(n=220000, weights=probs)
print("Total rows after subsampling: ", df.shape[0])

features = df.loc[:, df.columns != "Price"]
labels = df.loc[:, "Price"]

# Check outliers, class frequencies, and price distributions
assert df.index[np.isinf(df.select_dtypes(np.number)).any(1)].empty  # No infs
assert df.index[np.isnan(df.select_dtypes(np.number)).any(1)].empty  # No nans
fig, axes = plt.subplots(2, 2, figsize=(13, 13))
sns.boxplot(data=features.loc[:, ["BreedCount", "Pureness"]], orient="h", ax=axes[0, 0])
sns.kdeplot(data=labels, ax=axes[0, 1])
sns.countplot(x="Class", data=df, ax=axes[1, 0])
sns.kdeplot(data=df, x="Price", hue="Class", fill=True, ax=axes[1, 1])

# Unsupervised anomaly detection model
ANOMALY_QUANTILE = 0.04  #  "auto"
model_isof = IsolationForest(
    n_estimators=1000,
    max_samples="auto",
    contamination=ANOMALY_QUANTILE,
    n_jobs=-1,
    random_state=123,
)
model_isof.fit(X=labels.to_numpy().reshape(-1, 1))

# Show the anomaly score distribution
anomaly_score = model_isof.score_samples(X=labels.to_numpy().reshape(-1, 1))
quantile_01 = np.quantile(anomaly_score, q=ANOMALY_QUANTILE)
sns.displot(
    data=anomaly_score,
    kind="kde",
    color="blue",
    height=5,
    aspect=2,
).set(title="Distribution of anomaly values", xlabel="Anomaly score")
plt.axvline(quantile_01, c="red", linestyle="--", label="0.01 quantile")
plt.draw()
plt.pause(0.1)

# Discard anomalies      -1 = anomaly, 1 = ok
anomaly_prediction = model_isof.predict(X=labels.to_numpy().reshape(-1, 1))
df = df.loc[(anomaly_prediction != -1), :]

# Save the data
df.to_csv(f"./data/full_cleansed.csv")
print("\nSaved")
