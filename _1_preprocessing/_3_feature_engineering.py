import time
import pickle

import pandas as pd

from _1_preprocessing.feature_eng_utils import (
    generate_combo_scores,
    fit_one_hot_encoder,
    score_df,
)

# Load the data
leaderboard = pd.read_csv("./_0_get_data_leaderboard/leaderboard.csv")
df = pd.read_csv(f"./data/full_cleansed.csv", index_col=[0]).set_index(["Id"])  # Figure out where the col 0 comes from

# Fit, save, and load the one hot encoder
fit_one_hot_encoder(df)
with open("./_1_preprocessing/one_hot_encoder.pickle", "rb") as f:
    oh_enc = pickle.load(f)

# Calculate combo scores
combo_scores = generate_combo_scores(leaderboard)
with open("./_1_preprocessing/combo_scores.txt", "w") as f:
    f.write(str(combo_scores))

# # Check if the feature engineering is done fast enough for real time inference
start = time.time()
row = score_df(df.iloc[-100:, :], combo_scores, oh_enc, fit_scaler=True)
end = time.time()
print("Time elapsed in feature engineering 100 nft: ", end - start, "s")
print(row.head(), "\n\n")

# Do the feature engineering on the data and save it
df = score_df(df, combo_scores, oh_enc, fit_scaler=True)
print(df.head())
df.to_csv(f"./data/full_engineered.csv")
print("\nSaved")
