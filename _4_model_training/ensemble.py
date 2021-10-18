import pickle

import pandas as pd
from numpy import mean
from numpy import std
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import StackingRegressor
from sklearn.base import ClassifierMixin, TransformerMixin
from sklearn.pipeline import Pipeline
from matplotlib import pyplot as plt
import seaborn as sns

from _3_preprocessing.preprocessing_fns import (
    preprocessing_fn_1,
    preprocessing_fn_2,
    preprocessing_fn_3,
)
from _4_model_training.reduce_mem_usage import reduce_mem_usage

# Load the data
train = pd.read_csv(".\data\\set_train_val.csv", index_col=[0, 1])
holdout = pd.read_csv(".\data\\set_holdout1.csv", index_col=[0, 1])
holdout2 = pd.read_csv(".\data\\set_holdout2.csv", index_col=[0, 1])
train = reduce_mem_usage(train)
holdout = reduce_mem_usage(holdout)
holdout2 = reduce_mem_usage(holdout2)
# Split the data in features and labels
features = train.loc[:, train.columns.difference(["PriceBy100", "PriceUSD"])].to_numpy()
labels = train.loc[:, "PriceBy100"].to_numpy()
test_features = holdout.loc[
    :, holdout.columns.difference(["PriceBy100", "PriceUSD"])
].to_numpy()
test_labels = holdout.loc[:, "PriceBy100"].to_numpy()
final_test_features = holdout2.loc[
    :, holdout2.columns.difference(["PriceBy100", "PriceUSD"])
].to_numpy()
final_test_labels = holdout2.loc[:, "PriceBy100"].to_numpy()

# Load the feature engineering utilities
with open("./features/feature_set_1_ohe.pickle", "rb") as f:
    ohe1 = pickle.load(f)
with open("./features/feature_set_1_scaler.pickle", "rb") as f:
    scaler1 = pickle.load(f)
with open("./features/feature_set_2_ohe.pickle", "rb") as f:
    ohe2 = pickle.load(f)
with open("./features/feature_set_2_scaler.pickle", "rb") as f:
    scaler2 = pickle.load(f)
with open("./features/feature_set_3_ohe.pickle", "rb") as f:
    ohe3 = pickle.load(f)
with open("./features/feature_set_3_scaler.pickle", "rb") as f:
    scaler3 = pickle.load(f)
with open("./features/combo_scores.txt") as f:
    for i in f.readlines():
        scores = i
scores = eval(scores)
# Load the base models and pair them with the feature sets used to train each model
models = dict()
with open("./models/_GBM.pkl", "rb") as f:
    models["GBM"] = Pipeline(
        [("_", preprocessing_fn_3(scores, ohe3, scaler3)), ("GBM", pickle.load(f))]
    )
with open("./models/_lightGBM.pkl", "rb") as f:
    models["lGBM"] = Pipeline(
        [("_", preprocessing_fn_2(scores, ohe3, scaler3)), ("lGBM", pickle.load(f))]
    )
with open("./models/_tree.pkl", "rb") as f:
    models["tree"] = Pipeline(
        [("_", preprocessing_fn_1(scores, ohe3, scaler3)), ("tree", pickle.load(f))]
    )
with open("./models/_KNN.pkl", "rb") as f:
    models["KNN"] = Pipeline(
        [("_", preprocessing_fn_1(scores, ohe3, scaler3)), ("KNN", pickle.load(f))]
    )
with open("./models/_polynomial.pkl", "rb") as f:
    models["poly"] = Pipeline(
        [("_", preprocessing_fn_1(scores, ohe3, scaler3)), ("poly", pickle.load(f))]
    )

# Check how the base model predictions correlate
pred = pd.DataFrame()
for name, model in models.items():
    data = pd.DataFrame({name: model.predict(features)})
    pred = pd.concat([pred, data], axis=1)
sns.heatmap(pred.corr(), xticklabels=pred.columns, yticklabels=pred.columns, annot=True)
plt.show()
# plt.draw()
# plt.pause(10)

# Compare the models on a holdout set
def compare_models():
    results, names = list(), list()
    cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
    for name, model in models.items():
        preds = model.predict(test_features)
        scores = test_labels - preds
        results.append(scores)
        names.append(name)
        print(">%s %.3f (%.3f)" % (name, mean(scores), std(scores)))
    plt.boxplot(results, labels=names, showmeans=True)
    plt.show()
    # plt.draw()
    # plt.pause(10)


compare_models()
# Create the ensemble

# level0 = list()
# for name, model in models.items():
#     level0.append((name, model))
# level1 = LinearRegression()
# ensemble = StackingRegressor(estimators=level0, final_estimator=level1, cv=5)


class IdentityPassthrough(ClassifierMixin):
    def __init__(self):
        pass

    def fit(self, X, y):
        return self

    def predict(self, X):
        return X


partial_passthrough = Pipeline(
    [
        (
            "pass",
            ColumnTransformer([("pass", "passthrough", ["a", "b"])]),
        ),
        ("ident", IdentityPassthrough()),
    ]
)
feature_set1 = ColumnTransformer([("_", preprocessing_fn_1, ["a", "b"])])
feature_set2 = ColumnTransformer([("_", preprocessing_fn_2, ["a", "b"])])
feature_set3 = ColumnTransformer([("_", preprocessing_fn_3, ["a", "b"])])
ensemble = StackingRegressor(
    estimators=[
        ("pass", partial_passthrough),
        ("GBM", Pipeline([("_", feature_set3), ("GBM", model["GBM"])])),
        ("lGBM", Pipeline([("_", feature_set2), ("lGBM", model["lGBM"])])),
        ("tree", Pipeline([("_", feature_set1), ("tree", model["tree"])])),
        ("KNN", Pipeline([("_", feature_set1), ("KNN", model["KNN"])])),
        ("poly", Pipeline([("_", feature_set1), ("poly", model["poly"])])),
    ],
    final_estimator=LinearRegression(),
    cv=5,
)


ensemble.fit(features, labels)
models["ensemble"] = ensemble
# Save the model
with open("models/ensemble.pkl", "wb") as f:
    pickle.dump(ensemble, f)
    print("saved")

# Compare the models again
compare_models()

# # Do the final test on the test set
# predictions = ensemble.predict(final_test_features)
# print(
#     "\n",
#     "Score on the test set: ",
#     metrics.mean_absolute_error(final_test_labels, predictions),
# )
