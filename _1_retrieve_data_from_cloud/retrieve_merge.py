import json
import glob
import pathlib

import pandas as pd

# Open all the batches saved
full_file = []
for f in glob.glob(f"./data/**/*.json"):
    with open(f, "rb") as infile:
        full_file.append(json.load(infile))
        print("Rows {}: ".format(infile.name.split("\\")[2]), pd.read_json(f).shape[0])
# Save the full dataset made of all of the batches
full_file = [axie for batch in full_file for axie in batch]
with open(f"./data/full_raw.json", "w") as outfile:
    json.dump(full_file, outfile)
print("\n Saved")
