import time
import pickle

import pandas as pd

from _1_preprocessing.feature_eng_utils import (
    generate_frecuency_scores_lookup,
    fit_one_hot_encoder,
    score_df,
)

# Load the data
leaderboard = pd.read_csv("./_0_get_data_leaderboard/leaderboard.csv")
df = pd.read_csv(f"./data/full_cleansed.csv", index_col=[0]).set_index(
    ["Id"]
)  # Remove index_col or set_index, redundant. Check pipeline works after removing

# Fit, save, and load the one hot encoder
fit_one_hot_encoder(df)
with open("./_1_preprocessing/one_hot_encoder.pickle", "rb") as f:
    oh_enc = pickle.load(f)

# Calculate card and combo scores
scores_lookup = generate_frecuency_scores_lookup(leaderboard)
with open("./_1_preprocessing/scores_lookup.txt", "w") as f:
    f.write(str(scores_lookup))

# Check if the feature engineering is done fast enough for real time inference
# start = time.time()
# row = score_df(df.iloc[-100:], scores_lookup, oh_enc)
# end = time.time()
# print("Time elapsed in feature engineering 100 nft: ", end - start, "s")
# print(row)

# Do the feature engineering on the data and save it
df = score_df(df, scores_lookup, oh_enc, disable_progress_bar=False)
print(df.head())
df.to_csv(f"./data/full_engineered.csv")
print("\nSaved")
