import pickle

import pandas as pd
from sklearn import preprocessing
from sklearn import linear_model
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline

from _3_preprocessing.preprocessing_fns import preprocessing_fn_1
from _4_model_training.reduce_mem_usage import reduce_mem_usage

# Load the feature engineering utilities
with open("./features/feature_set_1_ohe.pickle", "rb") as f:
    ohe = pickle.load(f)
with open("./features/feature_set_1_scaler.pickle", "rb") as f:
    scaler = pickle.load(f)
with open("./features/combo_scores.txt") as f:
    for i in f.readlines():
        combo_scores = i
combo_scores = eval(combo_scores)
# Load the data
train = pd.read_csv(".\data\\set_train_val.csv", index_col=[0, 1])
holdout = pd.read_csv(".\data\\set_holdout1.csv", index_col=[0, 1])
# Use preprocessing_fn_n to engineer feature set n
train = preprocessing_fn_1(combo_scores, scaler=scaler, encoder=ohe).transform(train)
holdout = preprocessing_fn_1(combo_scores, scaler=scaler, encoder=ohe).transform(
    holdout
)
# Split in features and labels
train = reduce_mem_usage(train)
holdout = reduce_mem_usage(holdout)
features = train.loc[:, train.columns.difference(["PriceBy100", "PriceUSD"])].to_numpy()
labels = train.loc[:, "PriceBy100"].to_numpy()
test_features = holdout.loc[
    :, holdout.columns.difference(["PriceBy100", "PriceUSD"])
].to_numpy()
test_labels = holdout.loc[:, "PriceBy100"].to_numpy()

# Define the model and hyperpameters
model = pipeline.Pipeline(
    steps=[
        ("poly", preprocessing.PolynomialFeatures(include_bias=False, order="C")),
        ("model", linear_model.LinearRegression()),
    ]
)

# Only hyperparameter
degree = range(2, 4)


def mse_scorer(*args):
    score = metrics.mean_squared_error(*args)
    print("score is {}".format(score))
    return score


# Define the grid search
grid = dict(poly__degree=degree)
cv = model_selection.RepeatedKFold(n_splits=7, n_repeats=1, random_state=1)
gs = model_selection.GridSearchCV(
    estimator=model,
    param_grid=grid,
    n_jobs=1,
    cv=cv,
    scoring=metrics.make_scorer(mse_scorer, greater_is_better=False),
    verbose=1,
)
# Hyperparameter tuning
gs.fit(features, labels)
# Print results
print("\nBest score: {} with params: {} ".format(gs.best_score_, gs.best_params_))
print("\nBest 5 fits:")
means = gs.cv_results_["mean_test_score"][-5:]
stds = gs.cv_results_["std_test_score"][-5:]
params = gs.cv_results_["params"][-5:]
for mean, stdev, param in zip(means, stds, params):
    print("%f +- %f with: %r" % (mean, stdev, param))

# Build the model with the optimal hyperparameters
best_hps = gs.best_params_
best_model = gs.best_estimator_
best_model.fit(features, labels)

# Save the model
with open("models/_polynomial.pkl", "wb") as f:
    pickle.dump(best_model, f)
