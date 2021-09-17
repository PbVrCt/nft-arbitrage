import pickle

import pandas as pd
from sklearn import preprocessing
from sklearn import linear_model
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline

df = pd.read_csv(".\data\\full_engineered.csv", index_col=[0])
features = df.iloc[:-3000].loc[:, df.columns != "Price"].to_numpy()
labels = df.iloc[:-3000].loc[:, "Price"].to_numpy()
test_features = df.iloc[-3000:].loc[:, df.columns != "Price"].to_numpy()
test_labels = df.iloc[-3000:].loc[:, "Price"].to_numpy()

# Define the model and hyperpameters
model = pipeline.Pipeline(
    steps=[
        ("poly", preprocessing.PolynomialFeatures(include_bias=False)),
        ("model", linear_model.LinearRegression()),
    ]
)
degree = range(1, 6)
order = ["C", "F"]
# Define the grid search
grid = dict(poly__degree=degree, poly__order=order)
cv = model_selection.RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
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
# Build the model with the optimal hyperparameters
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
with open("_2_model_training/_polynomial.pkl", "wb") as f:
    pickle.dump(best_model, f)
