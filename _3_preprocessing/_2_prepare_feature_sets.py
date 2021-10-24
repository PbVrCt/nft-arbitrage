import time
import pickle

import pandas as pd

from _3_preprocessing.preprocessing_fns import (
    generate_combo_scores,
    PreprocessingFn1,
    PreprocessingFn2,
    PreprocessingFn3,
)

# Load the data
leaderboard = pd.read_json("./data/leaderboard_aggregated.json")
df = pd.read_csv(f"./data/full_cleansed.csv", index_col=[0, 1])

# Calculate combo scores
scores = generate_combo_scores(leaderboard)
with open("./features/combo_scores.txt", "w") as f:
    f.write(str(scores))

# Check if the feature engineering is done fast enough for real time inference
PreprocessingFn3(scores).fit_ohe_and_scaler(df)
with open("./features/feature_set_3_ohe.pickle", "rb") as f:
    ohe = pickle.load(f)
with open("./features/feature_set_3_scaler.pickle", "rb") as f:
    scaler = pickle.load(f)
start = time.time()
test_df = PreprocessingFn3(scores, scaler=scaler, encoder=ohe).preprocessing(
    df.iloc[-100:, :]
)
end = time.time()
print("Time elapsed in feature engineering 100 nft: ", end - start, "s")
# print(test_df.head())

# Fit the scalers and the one_hot_encoders to the data. Each fn engineers a different feature set
PreprocessingFn1(scores).fit_ohe_and_scaler(df)
PreprocessingFn2(scores).fit_ohe_and_scaler(df)
PreprocessingFn3(scores).fit_ohe_and_scaler(df)
