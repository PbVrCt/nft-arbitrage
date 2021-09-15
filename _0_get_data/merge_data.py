import json
import glob
import pathlib

import pandas as pd

START_DATE = "2021-09-14"

# Open all the batches saved
full_file = []
for f in glob.glob(f"./data/{START_DATE}/*.json"):
    with open(f, "rb") as infile:
        full_file.append(json.load(infile))
        print("Rows from batch: ", pd.read_json(f).shape[0])
# Save the full dataset made of all of the batches
full_file = [axie for batch in full_file for axie in batch]
with open(f"./data/full.json", "w") as outfile:
    json.dump(full_file, outfile)
# Check the dataset
df = pd.read_json(f"./data/full.json")
print("\nTotal rows: ", df.shape[0])
df = df.drop_duplicates(subset=["Id", "Price"])
print("Total rows wtihout duplicates: ", df.shape[0])
print(df.head())
