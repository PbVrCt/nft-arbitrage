import time
import pickle

import pandas as pd

from _3_preprocessing.feature_eng_utils import (
    generate_combo_scores,
    fit_one_hot_encoder,
    preprocessing_fn,
)

# Load the data
leaderboard = pd.read_json("./data/leaderboard_aggregated.json")
df = pd.read_csv(f"./data/full_cleansed.csv", index_col=[0, 1])

# Calculate combo scores
combo_scores = generate_combo_scores(leaderboard)
with open("./_3_preprocessing/combo_scores.txt", "w") as f:
    f.write(str(combo_scores))

# Check if the feature engineering is done fast enough for real time inference
start = time.time()
row = preprocessing_fn(
    df.iloc[-100:, :], combo_scores, fit_scaler=True, fit_encoder=True
)
end = time.time()
print("Time elapsed in feature engineering 100 nft: ", end - start, "s")
print(row.head(), "\n\n")

# Do the feature engineering on the data and save it
df = preprocessing_fn(df, combo_scores, fit_scaler=True, fit_encoder=True)
print(df.head())
df.to_csv(f"./data/full_engineered.csv")
print("\nSaved")
