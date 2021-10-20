import pickle

import pandas as pd
from sklearn import preprocessing
from sklearn import linear_model
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline

from _3_preprocessing.preprocessing_fns import PreprocessingFn1

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
features = pd.read_csv(".\data\\set_train_val_features.csv", index_col=[0])
labels = pd.read_csv(".\data\\set_train_val_labels.csv", index_col=[0])

# Define the model and hyperpameters
model = pipeline.Pipeline(
    steps=[
        ("featr eng", PreprocessingFn1(combo_scores, ohe, scaler)),
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
gs.fit(features, labels.to_numpy().ravel())
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
best_model.fit(features, labels.to_numpy().ravel())

# Save the model
with open("models/_polynomial.pkl", "wb") as f:
    pickle.dump(best_model, f)
