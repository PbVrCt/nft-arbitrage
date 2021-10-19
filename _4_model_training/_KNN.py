import pickle

import pandas as pd
from sklearn import neighbors
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
test_features = pd.read_csv(".\data\\set_holdout1_features.csv", index_col=[0])
test_labels = pd.read_csv(".\data\\set_holdout1_labels.csv", index_col=[0])
# Use PreprocessingFnn to engineer feature set n. Returns a numpy array
features = PreprocessingFn1(combo_scores, scaler=scaler, encoder=ohe).transform(
    features
)
test_features = PreprocessingFn1(combo_scores, scaler=scaler, encoder=ohe).transform(
    test_features
)
labels = labels.to_numpy().ravel()
test_labels = test_labels.to_numpy().ravel()
# Define the model and hyperpameters
model = neighbors.KNeighborsRegressor()
n_neighbors = range(5, 15, 5)
leaf_size = range(20, 40, 10)
weights = ["uniform", "distance"]
algorithm = ["auto"]  # , "ball_tree", "kd_tree"]
metric = ["euclidean"]  # , "manhattan", "minkowski"]
p = [1, 2]
# Define the search space
grid = dict(
    n_neighbors=n_neighbors,
    weights=weights,
    metric=metric,
    p=p,
    leaf_size=leaf_size,
    algorithm=algorithm,
)
cv = model_selection.RepeatedKFold(n_splits=5, n_repeats=1, random_state=1)


def mse_scorer(*args):
    score = metrics.mean_absolute_error(*args)
    print("score is {}".format(score))
    return score


gs = model_selection.GridSearchCV(
    estimator=model,
    param_grid=grid,
    n_jobs=1,
    cv=cv,
    scoring=metrics.make_scorer(mse_scorer, greater_is_better=False),
    verbose=2,
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
# Get the model with the optimal hyperparameters
best_hps = gs.best_params_
best_model = gs.best_estimator_
best_model.fit(features, labels)
# Save the model
with open("models/_KNN.pkl", "wb") as f:
    pickle.dump(best_model, f)
