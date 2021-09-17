import pickle

import pandas as pd
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline

import lightgbm as lgb
from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_uniform

df = pd.read_csv(".\data\\full_engineered.csv", index_col=[0])
features = df.iloc[:-3000].loc[:, df.columns != "Price"].to_numpy()
labels = df.iloc[:-3000].loc[:, "Price"].to_numpy()
test_features = df.iloc[-3000:].loc[:, df.columns != "Price"].to_numpy()
test_labels = df.iloc[-3000:].loc[:, "Price"].to_numpy()


# def learning_rate_010_decay_power_099(current_iter):
#     base_learning_rate = 0.1
#     lr = base_learning_rate  * np.power(.99, current_iter)
#     return lr if lr > 1e-3 else 1e-3

# def learning_rate_010_decay_power_0995(current_iter):
#     base_learning_rate = 0.1
#     lr = base_learning_rate  * np.power(.995, current_iter)
#     return lr if lr > 1e-3 else 1e-3

# def learning_rate_005_decay_power_099(current_iter):
#     base_learning_rate = 0.05
#     lr = base_learning_rate  * np.power(.99, current_iter)
#     return lr if lr > 1e-3 else 1e-3

fit_params = {
    "early_stopping_rounds": 30,
    "eval_metric": "auc",
    "eval_set": [(features, labels)],
    "eval_names": ["valid"],
    #'callbacks': [lgb.reset_parameter(learning_rate=learning_rate_010_decay_power_099)],
    "verbose": 100,
    "categorical_feature": "auto",
}

param_test = {
    "num_leaves": sp_randint(6, 50),
    "min_child_samples": sp_randint(100, 500),
    "min_child_weight": [1e-5, 1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3, 1e4],
    "subsample": sp_uniform(loc=0.2, scale=0.8),
    "colsample_bytree": sp_uniform(loc=0.4, scale=0.6),
    "reg_alpha": [0, 1e-1, 1, 2, 5, 7, 10, 50, 100],
    "reg_lambda": [0, 1e-1, 1, 5, 10, 20, 50, 100],
}

# This parameter defines the number of HP points to be tested
n_HP_points_to_test = 100

# n_estimators is set to a "large value". The actual number of trees build will depend on early stopping and 5000 define only the absolute maximum
clf = lgb.LGBMRegressor(
    max_depth=-1,
    random_state=314,
    silent=True,
    metric="rmse",
    n_jobs=4,
    n_estimators=5000,
)
grid_search = model_selection.RandomizedSearchCV(
    estimator=clf,
    param_distributions=param_test,
    n_iter=n_HP_points_to_test,
    scoring=metrics.make_scorer(metrics.mean_squared_error, greater_is_better=False),
    cv=3,
    refit=True,
    random_state=314,
    verbose=True,
)

grid_result = grid_search.fit(features, labels, **fit_params)

# gs.fit(X_train, y_train, **fit_params)
# print('Best score reached: {} with params: {} '.format(gs.best_score_, gs.best_params_))
# opt_parameters = {'colsample_bytree': 0.9234, 'min_child_samples': 399, 'min_child_weight': 0.1, 'num_leaves': 13, 'reg_alpha': 2, 'reg_lambda': 5, 'subsample': 0.855}


# # Define the model and hyperpameters
# model = neighbors.KNeighborsRegressor()
# n_neighbors = range(5, 25, 2)
# weights = ["uniform", "distance"]
# metric = ["euclidean", "manhattan", "minkowski"]
# p = [1, 2]
# # Define the search space
# grid = dict(n_neighbors=n_neighbors, weights=weights, metric=metric, p=p)
# cv = model_selection.RepeatedKFold(n_splits=7, n_repeats=3, random_state=1)
# grid_search = model_selection.GridSearchCV(
#     estimator=model,
#     param_grid=grid,
#     n_jobs=-1,
#     cv=cv,
#     scoring=metrics.make_scorer(metrics.mean_squared_error, greater_is_better=False),
#     verbose=1,
# )
# # Hyperparameter tuning
# grid_result = grid_search.fit(features, labels)
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
with open("_2_model_training/_lightGBM.pkl", "wb") as f:
    pickle.dump(best_model, f)
