import json
import time
import pickle

import pandas as pd
from tqdm import tqdm
from sklearn.preprocessing import OneHotEncoder


def engineer_placeholder_columns(df):
    df = df.copy()
    df.loc[:, "Back-Mouth"] = df["Back"] + "/" + df["Mouth"]
    df.loc[:, "Back-Horn"] = df["Back"] + "/" + df["Horn"]
    df.loc[:, "Back-Tail"] = df["Back"] + "/" + df["Tail"]
    df.loc[:, "Mouth-Horn"] = df["Mouth"] + "/" + df["Horn"]
    df.loc[:, "Mouth-Tail"] = df["Mouth"] + "/" + df["Tail"]
    df.loc[:, "Horn-Tail"] = df["Horn"] + "/" + df["Tail"]
    df.loc[:, "Back-Mouth-Horn"] = df["Back"] + "/" + df["Mouth"] + "/" + df["Horn"]
    df.loc[:, "Back-Mouth-Tail"] = df["Back"] + "/" + df["Mouth"] + "/" + df["Tail"]
    df.loc[:, "Back-Horn-Tail"] = df["Back"] + "/" + df["Horn"] + "/" + df["Tail"]
    df.loc[:, "Mouth-Horn-Tail"] = df["Mouth"] + "/" + df["Horn"] + "/" + df["Tail"]
    df.loc[:, "Build"] = (
        df["Back"] + "/" + df["Mouth"] + "/" + df["Horn"] + "/" + df["Tail"]
    )
    return df


def normalize(series):
    return ((series - series.min()) / (series.max() - series.min())) * 0.8 + 0.2


def generate_frecuency_scores_lookup(leaderboard):
    leaderboard = engineer_placeholder_columns(leaderboard)
    scores_lookup = pd.Series(dtype="object")
    # Calculate scores
    for part_groups in [
        ["Back", "Mouth", "Horn", "Tail"],
        [
            "Back-Mouth",
            "Back-Horn",
            "Back-Tail",
            "Mouth-Horn",
            "Mouth-Tail",
            "Horn-Tail",
        ],
        ["Back-Mouth-Horn", "Back-Mouth-Tail", "Back-Horn-Tail", "Mouth-Horn-Tail"],
        ["Build"],
    ]:
        counts = list()
        for parts in part_groups:
            counts.append(leaderboard.loc[:, ["Class", parts]].value_counts())
        counts = pd.concat(counts)
        freqs = normalize(counts)
        # Assign scores
        scores_lookup = scores_lookup.append(freqs)
    return scores_lookup.to_dict()


# twice as fast as using df.map()
def assign_frecuency_score(row, scores_lookup, parts):
    try:
        return scores_lookup[(row["Class"], row[parts])]
    except KeyError:
        return 0


def assign_multiplier_score(row):
    score = 0
    core_classes = ["Aquatic", "Beast", "Bird", "Bug", "Plant", "Reptile"]
    if row["Class"] in core_classes:
        for column in ["BackType", "MouthType", "HornType", "TailType"]:
            if row[column] == row["Class"]:
                score += 0.25
    elif row["Class"] == "Dusk":
        for column in ["BackType", "MouthType", "HornType", "TailType"]:
            if (row[column] == "Reptile") or (row[column] == "Aquatic"):
                score += 0.25 * 0.75
    elif row["Class"] == "Mech":
        for column in ["BackType", "MouthType", "HornType", "TailType"]:
            if (row[column] == "Beast") or (row[column] == "Bug"):
                score += 0.25 * 0.75
    elif row["Class"] == "Dawn":
        for column in ["BackType", "MouthType", "HornType", "TailType"]:
            if (row[column] == "Plant") or (row[column] == "Bird"):
                score += 0.25 * 0.75
    return score


def fit_one_hot_encoder(df):
    enc = OneHotEncoder(handle_unknown="ignore").fit(
        df.loc[:, ["Class", "Back", "Mouth", "Horn", "Tail"]].to_numpy()
    )
    with open("./_1_preprocessing/one_hot_encoder.pickle", "wb") as f:
        pickle.dump(enc, f)


def score_df(df, scores_lookup, class_encoder, disable_progress_bar=True):
    df = engineer_placeholder_columns(df)
    placeholder_columns = [
        "Back",
        "Mouth",
        "Horn",
        "Tail",
        "Back-Mouth",
        "Back-Horn",
        "Back-Tail",
        "Mouth-Horn",
        "Mouth-Tail",
        "Horn-Tail",
        "Back-Mouth-Horn",
        "Back-Mouth-Tail",
        "Back-Horn-Tail",
        "Mouth-Horn-Tail",
        "Build",
    ]
    # Feature engineering
    df.loc[:, "Multiplier_score"] = df.apply(assign_multiplier_score, axis=1)
    for column in tqdm(
        placeholder_columns, disable=disable_progress_bar, desc="Assigning combo scores"
    ):
        df.loc[:, f"{column}_score"] = df.apply(
            lambda df: assign_frecuency_score(df, scores_lookup, column), axis=1
        )
    df["sum_card_score"] = (
        df["Back_score"] + df["Mouth_score"] + df["Horn_score"] + df["Tail_score"]
    )
    df["sum_combo_score"] = (
        df["Back-Mouth_score"]
        + df["Back-Horn_score"]
        + df["Back-Tail_score"]
        + df["Mouth-Horn_score"]
        + df["Mouth-Tail_score"]
        + df["Horn-Tail_score"]
    )
    df["sum_tricombo_score"] = (
        df["Back-Mouth-Horn_score"]
        + df["Back-Mouth-Tail_score"]
        + df["Back-Horn-Tail_score"]
        + df["Mouth-Horn-Tail_score"]
    )
    df["build_score"] = df["Build_score"]

    # Feature selection
    for column in placeholder_columns:
        # df.drop(column, axis=1, inplace=True)
        df.drop(f"{column}_score", axis=1, inplace=True)
    df.drop(["Eyes", "Ears"], axis=1, inplace=True)

    # One hot encode categorical columns
    ohe = class_encoder.transform(
        df.loc[:, ["Class", "Back", "Mouth", "Horn", "Tail"]].to_numpy()
    ).toarray()
    # Create a Pandas DataFrame out of the one hot encoded column
    ohe_df = pd.DataFrame(
        ohe,
        columns=class_encoder.get_feature_names(
            ["Class", "Back", "Mouth", "Horn", "Tail"]
        ),
    ).astype(int)
    ohe_df.index = df.index
    # Concat it with the original df
    df = pd.concat([df.select_dtypes(exclude="object"), ohe_df], axis=1)
    return df


# Load the data
leaderboard = pd.read_csv("./_0_get_data_leaderboard/leaderboard.csv")
df = pd.read_csv(f"./data/full_cleansed.csv", index_col=[0])

# Fit, save, and load the one hot encoder
# fit_one_hot_encoder(df)
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
