"""score_df() is the function that applies feature transformations
to the data, both during model training and model serving/inference"""
import pickle

import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler

from _3_preprocessing.utils import (
    class_stats,
    part_stats,
    card_scores,
    card_attributes,
    engineer_combos,
    combos,
    tricombos,
    build,
)


def normalize(series):
    return ((series - series.min()) / (series.max() - series.min())) * 0.8 + 0.2


def generate_combo_scores(leaderboard):
    leaderboard = engineer_combos(leaderboard)
    scores_lookup = pd.Series(dtype="object")
    # Calculate scores
    for part_groups in [combos, tricombos, build]:
        counts = list()
        for parts in part_groups:
            counts.append(leaderboard.loc[:, parts].value_counts())
        counts = pd.concat(counts)
        freqs = normalize(counts)
        # Append scores to a pandas series
        scores_lookup = scores_lookup.append(freqs)
    return scores_lookup.to_dict()


# twice as fast as using df.map()
def assign_combo_score(row, scores_lookup, combo_columns):
    try:
        score = 0
        for column in combo_columns:
            score += scores_lookup[row[column]]
            return score
    except KeyError:
        return 0


def assign_card_score(row):
    score = 0
    try:
        for column in ["Mouth", "Back", "Horn", "Tail"]:
            score += card_scores[row[column]]
        return score
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


def assign_gene_quality(row):
    if row["Class"] in ["Dusk", "Mech", "Dawn"]:
        return 0.5
    gene_quality = 0.0
    genes = str(bin(int(row["Genes"], base=16)))[2:].zfill(256)  # hex to binary
    classs = genes[0:4]
    # Eyes, Mouth, Ears, Horn, Back, Tail
    for part in [
        genes[64:96],
        genes[96:128],
        genes[128:160],
        genes[160:192],
        genes[192:224],
        genes[224:256],
    ]:
        if part[2:6] == classs:  # dclass
            gene_quality += 76.0 / 6
        if part[12:16] == classs:  # r1class
            gene_quality += 3
        if part[22:26] == classs:  # r2class
            gene_quality += 1
    return round(gene_quality * 100) / 10000


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


def assign_attributes(row, i):
    score = 0
    try:
        for column in ["Mouth", "Back", "Horn", "Tail"]:
            score += card_attributes[row[column]][i]
        return score
    except KeyError:
        return 0


def fit_one_hot_encoder(df, columns_to_encode, file_prefix):
    enc = OneHotEncoder(handle_unknown="ignore").fit(
        df.loc[:, columns_to_encode].to_numpy()
    )
    with open(f"./features/{file_prefix}_ohe.pickle", "wb") as f:
        pickle.dump(enc, f)


def fit_save_scaler(df, columns_to_fit, file_prefix):
    scaler = MinMaxScaler().fit(df.loc[:, columns_to_fit].to_numpy())
    with open(f"./features/{file_prefix}_scaler.pickle", "wb") as f:
        pickle.dump(scaler, f)


# Takes either a fitted sklearn scaler or 'fit_scaler' = True. Same for the one hot encoder
class preprocessing_fn_1:
    def __init__(self, scores_lookup, encoder=False, scaler=False):
        self.__scores = scores_lookup
        self.__encoder = encoder
        self.__scaler = scaler

    def fit_ohe_and_scaler(self, df):
        df = df.copy()
        fit_one_hot_encoder(df, ["Class"], "feature_set_1")
        df.loc[:, "card_score"] = df.apply(assign_card_score, axis=1)
        fit_save_scaler(df, ["card_score"], "feature_set_1")
        return self

    def fit(self, df):
        return self

    def fit_transform(self, df):
        return transform(df)

    def transform(self, df):
        df = df.copy()
        # Feature engineering
        df.loc[:, "multiplier_score"] = df.apply(assign_multiplier_score, axis=1)
        df.loc[:, "card_score"] = df.apply(assign_card_score, axis=1)

        df = engineer_combos(df)
        df.loc[:, "combo_score"] = df.apply(
            lambda df: assign_combo_score(df, self.__scores, combos), axis=1
        )
        df.loc[:, "tricombo_score"] = df.apply(
            lambda df: assign_combo_score(df, self.__scores, tricombos), axis=1
        )
        df.loc[:, "build_score"] = df.apply(
            lambda df: assign_combo_score(df, self.__scores, build), axis=1
        )
        df.loc[:, "gene_quality"] = df.apply(assign_gene_quality, axis=1)
        # One hot encode categorical columns
        columns = ["Class"]
        ohe = self.__encoder.transform(df.loc[:, columns].to_numpy()).toarray()
        ohe_df = pd.DataFrame(
            ohe, columns=self.__encoder.get_feature_names(columns)
        ).astype(int)
        ohe_df.index = df.index
        df = pd.concat([df.select_dtypes(exclude="object"), ohe_df], axis=1)
        # Normalize features
        columns = ["card_score"]
        df.loc[:, columns] = self.__scaler.transform(df.loc[:, columns].to_numpy())
        return df


# Takes either a fitted sklearn scaler or 'fit_scaler' = True. Same for the one hot encoder
class preprocessing_fn_2:
    def __init__(self, scores_lookup, encoder=False, scaler=False):
        self.__scores = scores_lookup
        self.__encoder = encoder
        self.__scaler = scaler

    def fit_ohe_and_scaler(self, df):
        df = df.copy()
        columns = ["Class", "Back", "Mouth", "Horn", "Tail"]
        fit_one_hot_encoder(df, columns, "feature_set_2")
        df.loc[:, "card_score"] = df.apply(assign_card_score, axis=1)
        fit_save_scaler(df, ["card_score"], "feature_set_2")
        return self

    def fit(self, df):
        return self

    def fit_transform(self, df):
        return transform(df)

    def transform(self, df):
        df = df.copy()
        # Feature engineering
        df.loc[:, "multiplier_score"] = df.apply(assign_multiplier_score, axis=1)
        df.loc[:, "card_score"] = df.apply(assign_card_score, axis=1)

        df = engineer_combos(df)
        df.loc[:, "combo_score"] = df.apply(
            lambda df: assign_combo_score(df, self.__scores, combos), axis=1
        )
        df.loc[:, "tricombo_score"] = df.apply(
            lambda df: assign_combo_score(df, self.__scores, tricombos), axis=1
        )
        df.loc[:, "build_score"] = df.apply(
            lambda df: assign_combo_score(df, self.__scores, build), axis=1
        )
        df.loc[:, "gene_quality"] = df.apply(assign_gene_quality, axis=1)
        # One hot encode categorical columns
        columns = ["Class", "Back", "Mouth", "Horn", "Tail"]
        ohe = self.__encoder.transform(df.loc[:, columns].to_numpy()).toarray()
        ohe_df = pd.DataFrame(
            ohe, columns=self.__encoder.get_feature_names(columns)
        ).astype(int)
        ohe_df.index = df.index
        df = pd.concat([df.select_dtypes(exclude="object"), ohe_df], axis=1)
        # Normalize features
        columns = ["card_score"]
        df.loc[:, columns] = self.__scaler.transform(df.loc[:, columns].to_numpy())
        return df


# Takes either a fitted sklearn scaler or 'fit_scaler' = True. Same for the one hot encoder
class preprocessing_fn_3:
    def __init__(self, scores_lookup, encoder=False, scaler=False):
        self.__scores = scores_lookup
        self.__encoder = encoder
        self.__scaler = scaler

    def fit_ohe_and_scaler(self, df):
        df = df.copy()
        columns = ["Class", "Back", "Mouth", "Horn", "Tail"]
        fit_one_hot_encoder(df, columns, "feature_set_3")
        df.loc[:, "card_score"] = df.apply(assign_card_score, axis=1)
        df.loc[:, "stats"] = df.apply(assign_stats, axis=1)
        df[["Hp", "Sp", "Sk", "Mr"]] = pd.DataFrame(df.stats.tolist(), index=df.index)
        fit_save_scaler(df, ["Hp", "Sp", "Sk", "Mr", "card_score"], "feature_set_3")
        return self

    def fit(self, df):
        return self

    def fit_transform(self, df):
        return transform(df)

    def transform(self, df):
        df = df.copy()
        # Feature engineering
        df.loc[:, "multiplier_score"] = df.apply(assign_multiplier_score, axis=1)
        df.loc[:, "card_score"] = df.apply(assign_card_score, axis=1)
        df = engineer_combos(df)
        df.loc[:, "combo_score"] = df.apply(
            lambda df: assign_combo_score(df, self.__scores, combos), axis=1
        )
        df.loc[:, "tricombo_score"] = df.apply(
            lambda df: assign_combo_score(df, self.__scores, tricombos), axis=1
        )
        df.loc[:, "build_score"] = df.apply(
            lambda df: assign_combo_score(df, self.__scores, build), axis=1
        )
        df.loc[:, "gene_quality"] = df.apply(assign_gene_quality, axis=1)
        df.loc[:, "stats"] = df.apply(assign_stats, axis=1)
        df[["Hp", "Sp", "Sk", "Mr"]] = pd.DataFrame(df.stats.tolist(), index=df.index)
        df.drop("stats", axis=1, inplace=True)

        df.loc[:, "Attack"] = df.apply(lambda df: assign_attributes(df, 0), axis=1)
        df.loc[:, "Shield"] = df.apply(lambda df: assign_attributes(df, 1), axis=1)
        df.loc[:, "EnergyCost"] = df.apply(lambda df: assign_attributes(df, 2), axis=1)
        df.loc[:, "Stunt"] = df.apply(lambda df: assign_attributes(df, 3), axis=1)
        df.loc[:, "Poison"] = df.apply(lambda df: assign_attributes(df, 4), axis=1)
        df.loc[:, "DmgCombo"] = df.apply(lambda df: assign_attributes(df, 5), axis=1)
        df.loc[:, "Targetting"] = df.apply(lambda df: assign_attributes(df, 6), axis=1)
        df.loc[:, "EnergyGain"] = df.apply(lambda df: assign_attributes(df, 7), axis=1)
        df.loc[:, "Buffs/Debuffs"] = df.apply(
            lambda df: assign_attributes(df, 8), axis=1
        )
        df.loc[:, "CardDraw/Discard"] = df.apply(
            lambda df: assign_attributes(df, 9), axis=1
        )
        df.loc[:, "Healing/Shielding"] = df.apply(
            lambda df: assign_attributes(df, 10), axis=1
        )
        # One hot encode categorical columns
        columns = ["Class", "Back", "Mouth", "Horn", "Tail"]
        ohe = self.__encoder.transform(df.loc[:, columns].to_numpy()).toarray()
        ohe_df = pd.DataFrame(
            ohe, columns=self.__encoder.get_feature_names(columns)
        ).astype(int)
        ohe_df.index = df.index
        df = pd.concat([df.select_dtypes(exclude="object"), ohe_df], axis=1)
        # Normalize features
        columns = ["Hp", "Sp", "Sk", "Mr", "card_score"]
        df.loc[:, columns] = self.__scaler.transform(df.loc[:, columns].to_numpy())
        return df
