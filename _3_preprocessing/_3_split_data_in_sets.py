import pandas as pd

from _4_model_training.reduce_mem_usage import reduce_mem_usage

df = pd.read_csv(f"./data/full_cleansed.csv", index_col=[0])
df = reduce_mem_usage(df)

nrows = len(df)

train_val = df.iloc[: -int(nrows * 0.2)]
holdout1 = df.iloc[int(nrows * 0.8) : -int(nrows * 0.1)]
holdout2 = df.iloc[int(nrows * 0.9) :]

train_val.to_csv(f"./data/set_train_val.csv")
holdout1.to_csv(f"./data/set_holdout1.csv")
holdout2.to_csv(f"./data/set_holdout2.csv")
