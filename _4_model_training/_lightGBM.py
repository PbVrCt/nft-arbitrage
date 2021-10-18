import pickle

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn import model_selection
import lightgbm as lgb
from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_uniform
import matplotlib.pyplot as plt

from _3_preprocessing.preprocessing_fns import preprocessing_fn_2
from _4_model_training.reduce_mem_usage import reduce_mem_usage

# Load the feature engineering utilities
with open("./features/feature_set_2_ohe.pickle", "rb") as f:
    ohe = pickle.load(f)
with open("./features/feature_set_2_scaler.pickle", "rb") as f:
    scaler = pickle.load(f)
with open("./features/combo_scores.txt") as f:
    for i in f.readlines():
        combo_scores = i
combo_scores = eval(combo_scores)
# Load the data
train = pd.read_csv(".\data\\set_train_val.csv", index_col=[0, 1])
holdout = pd.read_csv(".\data\\set_holdout1.csv", index_col=[0, 1])
# Use preprocessing_fn_n to engineer feature set n
train = preprocessing_fn_2(combo_scores, scaler=scaler, encoder=ohe).transform(train)
holdout = preprocessing_fn_2(combo_scores, scaler=scaler, encoder=ohe).transform(
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


def learning_rate_010_decay_power_099(current_iter):
    base_learning_rate = 0.1
    lr = base_learning_rate * np.power(0.99, current_iter)
    return lr if lr > 1e-3 else 1e-3


def learning_rate_010_decay_power_0995(current_iter):
    base_learning_rate = 0.1
    lr = base_learning_rate * np.power(0.995, current_iter)
    return lr if lr > 1e-3 else 1e-3


def learning_rate_005_decay_power_099(current_iter):
    base_learning_rate = 0.05
    lr = base_learning_rate * np.power(0.99, current_iter)
    return lr if lr > 1e-3 else 1e-3


fit_params = {
    "early_stopping_rounds": 20,
    "eval_metric": "mse",
    "eval_set": [(features, labels)],
    "eval_names": ["Train set"],
    "verbose": False,
    "categorical_feature": "auto",
}
param_test = {
    "n_estimators": sp_randint(20, 200),
    "max_depth": sp_randint(10, 30),
    "num_leaves": sp_randint(6, 50),
    "min_child_samples": sp_randint(100, 500),
    "min_child_weight": [1e-5, 1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3, 1e4],
    "subsample": sp_uniform(loc=0.2, scale=0.8),
    "colsample_bytree": sp_uniform(loc=0.4, scale=0.6),
    # "reg_alpha": [0, 1e-1, 1, 2, 5, 7, 10, 50, 100],
    # "reg_lambda": [0, 1e-1, 1, 5, 10, 20, 50, 100],
}
clf = lgb.LGBMRegressor(
    max_depth=-1,
    random_state=314,
    silent=True,
    metric="mse",
    n_jobs=1,
    # n_estimators=50,
    # force_col_wise=True,
)


def mse_scorer(*args):
    score = metrics.mean_squared_error(*args)
    print("score is {}".format(score))
    return score


gs = model_selection.RandomizedSearchCV(
    estimator=clf,
    param_distributions=param_test,
    n_iter=30,
    scoring=metrics.make_scorer(mse_scorer, greater_is_better=False),
    cv=model_selection.RepeatedKFold(n_splits=7, n_repeats=1, random_state=1),
    refit=True,
    random_state=314,
    n_jobs=1,
    verbose=1,
)
gs.fit(
    features,
    labels,
    **fit_params,
    callbacks=[lgb.reset_parameter(learning_rate=learning_rate_010_decay_power_099)]
)
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

# Refit the best model with higher lr decay
best_model = lgb.LGBMRegressor(**gs.best_estimator_.get_params())
best_model.fit(
    features,
    labels,
    **fit_params,
    callbacks=[lgb.reset_parameter(learning_rate=learning_rate_010_decay_power_0995)]
)
# Feature importances
feat_imp = pd.Series(
    best_model.feature_importances_,
    index=train.loc[:, train.columns.difference(["PriceBy100", "PriceUSD"])].columns,
)
feat_imp.nlargest(20).plot(kind="barh", figsize=(10, 6))
plt.tight_layout()
plt.draw()
plt.pause(10)

# Save the model
with open("models/_lightGBM.pkl", "wb") as f:
    pickle.dump(best_model, f)
