"""score_df() is the function that applies feature transformations
to to the data, both during model training and model serving/inference"""
import pickle

import pandas as pd
from tqdm import tqdm
from sklearn.preprocessing import OneHotEncoder

class_stats = {
    "Beast": [31, 35, 31, 43],
    "Aquatic": [39, 39, 35, 27],
    "Plant": [43, 31, 31, 35],
    "Bird": [27, 43, 35, 35],
    "Bug": [35, 31, 35, 39],
    "Reptile": [39, 35, 31, 35],
    "Dusk": [43, 39, 27, 31],
    "Mech": [31, 39, 43, 27],
    "Dawn": [35, 35, 39, 31],
}
part_stats = {
    "Beast": [0, 1, 0, 3],
    "Aquatic": [1, 3, 0, 0],
    "Plant": [3, 0, 0, 1],
    "Bird": [0, 3, 0, 1],
    "Bug": [1, 0, 0, 3],
    "Reptile": [3, 1, 0, 0],
}

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
def assign_frecuency_score(row, scores_lookup, part):
    try:
        return scores_lookup[(row["Class"], row[part])]
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
            if (row[column] == "Reptile") or (row[column] == "Plant"):
                score += 0.25 * 0.75
    elif row["Class"] == "Mech":
        for column in ["BackType", "MouthType", "HornType", "TailType"]:
            if (row[column] == "Beast") or (row[column] == "Bug"):
                score += 0.25 * 0.75
    elif row["Class"] == "Dawn":
        for column in ["BackType", "MouthType", "HornType", "TailType"]:
            if (row[column] == "Aquatic") or (row[column] == "Bird"):
                score += 0.25 * 0.75
    return score


def assign_stats(row):
    stats = class_stats[row["Class"]]
    for column in [
        "MouthType",
        "BackType",
        "HornType",
        "TailType",
        "EyesType",
        "EarsType",
    ]:
        one_part_stats = part_stats[row[column]]
        stats = [x + y for x, y in zip(stats, one_part_stats)]
    return stats


def fit_one_hot_encoder(df):
    enc = OneHotEncoder(handle_unknown="ignore").fit(
        df.loc[:, ["Class", "Back", "Mouth", "Horn", "Tail"]].to_numpy()
    )
    with open("./_1_preprocessing/one_hot_encoder.pickle", "wb") as f:
        pickle.dump(enc, f)


def score_df(df, scores_lookup, class_encoder, disable_progress_bar=True):
    df = engineer_placeholder_columns(df)
    # Feature engineering
    tqdm.pandas()
    df.loc[:, "multiplier_score"] = df.progress_apply(
        assign_multiplier_score,
        axis=1,
    )
    df.loc[:, "stats"] = df.progress_apply(assign_stats, axis=1)
    df[["Hp", "Sp", "Sk", "Mr"]] = pd.DataFrame(df.stats.tolist(), index=df.index)
    df.drop("stats", axis=1, inplace=True)
    for column in tqdm(
        placeholder_columns,
        disable=disable_progress_bar,
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
    ohe_df = pd.DataFrame(
        ohe,
        columns=class_encoder.get_feature_names(
            ["Class", "Back", "Mouth", "Horn", "Tail"]
        ),
    ).astype(int)
    ohe_df.index = df.index
    df = pd.concat([df.select_dtypes(exclude="object"), ohe_df], axis=1)
    return df
