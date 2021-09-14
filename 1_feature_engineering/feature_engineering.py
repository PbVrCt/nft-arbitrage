import json
import pandas as pd


def assign_score(row, frecuencies, combo):
    try:
        return frecuencies[row["Class"], row[combo]]
    except KeyError:
        return 0


def normalize(series):
    return (series - series.min()) / (series.max() - series.min())


def card_score(df, leaderboard):
    for part in ["Back", "Mouth", "Horn", "Tail"]:
        frecuencies = normalize(leaderboard.loc[:, ["Class", part]].value_counts())
        df.loc[:, f"{part}_score"] = df.apply(
            lambda df: assign_score(df, frecuencies, part), axis=1
        )


def combo_score(df, leaderboard):
    for dtset in [df, leaderboard]:
        dtset["Back-Mouth"] = dtset["Back"] + "/" + dtset["Mouth"]
        dtset["Back-Horn"] = dtset["Back"] + "/" + dtset["Horn"]
        dtset["Back-Tail"] = dtset["Back"] + "/" + dtset["Tail"]
        dtset["Mouth-Horn"] = dtset["Mouth"] + "/" + dtset["Horn"]
        dtset["Mouth-Tail"] = dtset["Mouth"] + "/" + dtset["Tail"]
        dtset["Horn-Tail"] = dtset["Horn"] + "/" + dtset["Tail"]
    for combo in [
        "Back-Mouth",
        "Back-Horn",
        "Back-Tail",
        "Mouth-Horn",
        "Mouth-Tail",
        "Horn-Tail",
    ]:
        frecuencies = normalize(leaderboard.loc[:, ["Class", combo]].value_counts())
        df.loc[:, f"{combo}_score"] = df.apply(
            lambda df: assign_score(df, frecuencies, combo), axis=1
        )
        for dtset in [df, leaderboard]:
            dtset.drop(combo, axis=1, inplace=True)


def tricombo_score(df, leaderboard):
    for dtset in [df, leaderboard]:
        dtset["Back-Mouth-Horn"] = (
            dtset["Back"] + "/" + dtset["Mouth"] + "/" + dtset["Horn"]
        )
        dtset["Back-Mouth-Tail"] = (
            dtset["Back"] + "/" + dtset["Mouth"] + "/" + dtset["Tail"]
        )
        dtset["Back-Horn-Tail"] = (
            dtset["Back"] + "/" + dtset["Horn"] + "/" + dtset["Tail"]
        )
        dtset["Mouth-Horn-Tail"] = (
            dtset["Mouth"] + "/" + dtset["Horn"] + "/" + dtset["Tail"]
        )
    for tricombo in [
        "Back-Mouth-Horn",
        "Back-Mouth-Tail",
        "Back-Horn-Tail",
        "Mouth-Horn-Tail",
    ]:
        frecuencies = normalize(leaderboard.loc[:, ["Class", tricombo]].value_counts())
        df.loc[:, f"{tricombo}_score"] = df.apply(
            lambda df: assign_score(df, frecuencies, tricombo), axis=1
        )
        for dtset in [df, leaderboard]:
            dtset.drop(tricombo, axis=1, inplace=True)


def build_score(df, leaderboard):
    for dtset in [df, leaderboard]:
        dtset["Build"] = (
            dtset["Back"]
            + "/"
            + dtset["Mouth"]
            + "/"
            + dtset["Horn"]
            + "/"
            + dtset["Tail"]
        )
    frecuencies = normalize(leaderboard.loc[:, ["Class", "Build"]].value_counts())
    df.loc[:, "Build_score"] = df.apply(
        lambda df: assign_score(df, frecuencies, "Build"), axis=1
    )
    for dtset in [df, leaderboard]:
        dtset.drop("Build", axis=1, inplace=True)


def feature_eng_steps(df):
    # Feature engineering
    card_score(df, leaderboard)
    combo_score(df, leaderboard)
    # tricombo_score(df, leaderboard)
    build_score(df, leaderboard)
    df["BreedCount"] = normalize(df["BreedCount"])
    df["Pureness"] = normalize(df["Pureness"])
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

    # Feature selection
    df.drop(
        ["Id", "Class", "Eyes", "Ears", "Back", "Mouth", "Horn", "Tail"],
        axis=1,
        inplace=True,
    )
    df.drop(
        [
            "Back_score",
            "Mouth_score",
            "Horn_score",
            "Tail_score",
            "Back-Mouth_score",
            "Back-Horn_score",
            "Back-Tail_score",
            "Mouth-Horn_score",
            "Mouth-Tail_score",
            "Horn-Tail_score",
        ],
        axis=1,
        inplace=True,
    )
    return df


if __name__ == "__main__":
    DATE = "2021-09-13"
    leaderboard = pd.read_csv("./leaderboard/leaderboard.csv")
    leaderboard.drop(["User_Addr", "Winrate"], axis=1, inplace=True)
    df = pd.read_json(f"./data/full.json")
    df = df.drop_duplicates(subset=["Id", "Price"])

    df = feature_eng_steps(df)
    df.to_csv(f"./data/full_engineered.csv")
    print(df.head(-10))
