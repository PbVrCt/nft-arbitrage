import pandas as pd

leaderboard = pd.read_csv(".\leaderboard\leaderboard.csv")
leaderboard.drop(["User_Addr", "Winrate"], axis=1, inplace=True)
df = pd.read_json("axie_dataset_30_000.json")
df.columns = [
    "Id",
    "BreedCount",
    "Pureness",
    "Class",
    "Eyes",
    "Ears",
    "Back",
    "Mouth",
    "Horn",
    "Tail",
    "Price",
]


def assign_score(row, frecuencies, combo):
    try:
        return frecuencies[row["Class"], row[combo]]
    except KeyError:
        return 0


def card_score(df, leaderboard):
    for part in ["Back", "Mouth", "Horn", "Tail"]:
        frecuencies = leaderboard.loc[:, ["Class", part]].value_counts(normalize=True)
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
        frecuencies = leaderboard.loc[:, ["Class", combo]].value_counts(normalize=True)
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
        frecuencies = leaderboard.loc[:, ["Class", tricombo]].value_counts(
            normalize=True
        )
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
    frecuencies = leaderboard.loc[:, ["Class", "Build"]].value_counts(normalize=True)
    df.loc[:, "Build_score"] = df.apply(
        lambda df: assign_score(df, frecuencies, "Build"), axis=1
    )
    for dtset in [df, leaderboard]:
        dtset.drop("Build", axis=1, inplace=True)


card_score(df, leaderboard)
combo_score(df, leaderboard)
tricombo_score(df, leaderboard)
build_score(df, leaderboard)
df.drop(
    ["Id", "Class", "Eyes", "Ears", "Back", "Mouth", "Horn", "Tail"],
    axis=1,
    inplace=True,
)
print(df.head())
