import pandas as pd

from _4_model_training.reduce_mem_usage import reduce_mem_usage

df = pd.read_csv(f"./data/full_cleansed.csv", index_col=[0])
df = reduce_mem_usage(df)


# Split in train val and holdout/test sets
nrows = len(df)
train_val = df.iloc[: -int(nrows * 0.2)]
holdout1 = df.iloc[int(nrows * 0.8) : -int(nrows * 0.1)]
holdout2 = df.iloc[int(nrows * 0.9) :]

# Split in features and labels
t_features = train_val.loc[:, train_val.columns.difference(["PriceBy100", "PriceUSD"])]
t_labels = train_val.loc[:, "PriceBy100"]
h1_features = holdout1.loc[:, holdout1.columns.difference(["PriceBy100", "PriceUSD"])]
h1_labels = holdout1.loc[:, "PriceBy100"]
h2_features = holdout2.loc[:, holdout2.columns.difference(["PriceBy100", "PriceUSD"])]
h2_labels = holdout2.loc[:, "PriceBy100"]

# Save data
t_features.to_csv(f"./data/set_train_val_features.csv")
t_labels.to_csv(f"./data/set_train_val_labels.csv")
h1_features.to_csv(f"./data/set_holdout1_features.csv")
h1_labels.to_csv(f"./data/set_holdout1_labels.csv")
h2_features.to_csv(f"./data/set_holdout2_features.csv")
h2_labels.to_csv(f"./data/set_holdout2_labels.csv")
