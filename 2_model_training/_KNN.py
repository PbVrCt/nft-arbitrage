import pickle

import pandas as pd
from sklearn import neighbors
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline

df = pd.read_csv(".\data\\full_engineered.csv", index_col=[0])
features = df.iloc[:95000].loc[:, df.columns != "Price"].to_numpy()
labels = df.iloc[:95000].loc[:, "Price"].to_numpy()
test_features = df.loc[95000:].loc[:, df.columns != "Price"].to_numpy()
test_labels = df.loc[95000:].loc[:, "Price"].to_numpy()

# Define the model and hyperpameters
model = neighbors.KNeighborsRegressor()
n_neighbors = range(5, 25, 2)
weights = ["uniform", "distance"]
metric = ["euclidean", "manhattan", "minkowski"]
p = [1, 2]
# Define the grid search
grid = dict(n_neighbors=n_neighbors, weights=weights, metric=metric, p=p)
cv = model_selection.RepeatedKFold(n_splits=5, n_repeats=3, random_state=1)
grid_search = model_selection.GridSearchCV(
    estimator=model,
    param_grid=grid,
    n_jobs=-1,
    cv=cv,
    scoring=metrics.make_scorer(metrics.mean_squared_error, greater_is_better=False),
    verbose=1,
)
# Hyperparameter tuning
grid_result = grid_search.fit(features, labels)
# Print results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_["mean_test_score"]
stds = grid_result.cv_results_["std_test_score"]
params = grid_result.cv_results_["params"]
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))
# Get the model with the optimal hyperparameters
best_hps = grid_search.best_params_
best_model = grid_search.best_estimator_

# Do the final test on the test set
best_model.fit(features, labels)
predictions = best_model.predict(test_features)
print(
    "\n",
    "Score on the test set: ",
    metrics.mean_squared_error(test_labels, predictions),
)
# Save the model
with open("model_training/_KNN.pkl", "wb") as f:
    pickle.dump(best_model, f)
