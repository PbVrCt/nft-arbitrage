import pickle

import pandas as pd
from sklearn import neighbors
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline

from _2_model_training.reduce_mem_usage import reduce_mem_usage

df = pd.read_csv(".\data\\full_engineered.csv", index_col=[0])
df = reduce_mem_usage(df)
features = df.iloc[:-3000].loc[:, df.columns != "Price"].to_numpy()
labels = df.iloc[:-3000].loc[:, "Price"].to_numpy()
test_features = df.iloc[-3000:].loc[:, df.columns != "Price"].to_numpy()
test_labels = df.iloc[-3000:].loc[:, "Price"].to_numpy()

# Define the model and hyperpameters
model = neighbors.KNeighborsRegressor()
n_neighbors = range(5, 25, 2)
weights = ["uniform"]  # , "distance"]
metric = ["euclidean"]  # , "manhattan", "minkowski"]
p = [1, 2]
# Define the search space
grid = dict(n_neighbors=n_neighbors, weights=weights, metric=metric, p=p)
cv = model_selection.RepeatedKFold(n_splits=7, n_repeats=1, random_state=1)


def mse_scorer(*args):
    score = metrics.mean_squared_error(*args)
    print("score is {}".format(score))
    return score


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
# Get the model with the optimal hyperparameters
best_hps = gs.best_params_
best_model = gs.best_estimator_
best_model.fit(features, labels)

# Do the final test on the test set
predictions = best_model.predict(test_features)
print(
    "\n",
    "Score on the test set: ",
    metrics.mean_squared_error(test_labels, predictions),
)
# Save the model
with open("_2_model_training/_KNN.pkl", "wb") as f:
    pickle.dump(best_model, f)
