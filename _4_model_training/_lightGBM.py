import pickle

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline
import lightgbm as lgb
from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_uniform
import matplotlib.pyplot as plt

from _3_preprocessing.preprocessing_fns import PreprocessingFn2

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
features = pd.read_csv(".\data\\set_train_val_features.csv", index_col=[0])
labels = pd.read_csv(".\data\\set_train_val_labels.csv", index_col=[0])

# Define model and hyperparam search


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
    # "model__early_stopping_rounds": 20, # No easy interplay between 'cv' from lightgbm's sklearn api and this param
    # "model__eval_metric": "mse",
    # "model__eval_set": [(_, _)], # To avoid information leakeage ideally this would not be the validaton fold from k-fold cv
    # "model__eval_names": ["Eval set"],
    "model__verbose": False,
    "model__categorical_feature": "auto",
}
param_test = {
    "model__n_estimators": sp_randint(20, 200),
    "model__max_depth": sp_randint(10, 30),
    "model__num_leaves": sp_randint(6, 50),
    "model__min_child_samples": sp_randint(100, 500),
    "model__min_child_weight": [1e-5, 1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3, 1e4],
    "model__subsample": sp_uniform(loc=0.2, scale=0.8),
    "model__colsample_bytree": sp_uniform(loc=0.4, scale=0.6),
    # "model__reg_alpha": [0, 1e-1, 1, 2, 5, 7, 10, 50, 100],
    # "model__reg_lambda": [0, 1e-1, 1, 5, 10, 20, 50, 100],
}

model = pipeline.Pipeline(
    steps=[
        ("featr eng", PreprocessingFn2(combo_scores, ohe, scaler)),
        (
            "model",
            lgb.LGBMRegressor(
                max_depth=-1,
                random_state=314,
                silent=True,
                metric="mse",
                n_jobs=1,
                # n_estimators=50,
                # force_col_wise=True,
            ),
        ),
    ]
)


def mse_scorer(*args):
    score = metrics.mean_squared_error(*args)
    print("score is {}".format(score))
    return score


gs = model_selection.RandomizedSearchCV(
    estimator=model,
    param_distributions=param_test,
    n_iter=35,
    scoring=metrics.make_scorer(mse_scorer, greater_is_better=False),
    cv=model_selection.RepeatedKFold(n_splits=7, n_repeats=1, random_state=1),
    refit=True,
    random_state=314,
    n_jobs=1,
    verbose=1,
)

# Train the model

gs.fit(
    features,
    labels.to_numpy().ravel(),
    **fit_params,
    model__callbacks=[
        lgb.reset_parameter(learning_rate=learning_rate_010_decay_power_099)
    ]
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

# Feature importances
feature_list = PreprocessingFn2(combo_scores, scaler=scaler, encoder=ohe).feature_list(
    features
)
feat_imp = pd.Series(
    best_model.named_steps["model"].feature_importances_, index=feature_list
)
feat_imp.nlargest(20).plot(kind="barh", figsize=(10, 6))
plt.tight_layout()
plt.draw()
plt.pause(10)

# Save the model
with open("models/_lightGBM.pkl", "wb") as f:
    pickle.dump(best_model, f)
