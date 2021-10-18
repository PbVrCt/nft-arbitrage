import pickle

import pandas as pd
import keras_tuner as kt
from sklearn import tree
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline
import matplotlib.pyplot as plt


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

# Define the model: Random Forest
class RF(kt.HyperModel):
    def build(self, hp):
        splitter = hp.Choice("splitter", ["best", "random"])
        max_features = hp.Choice("max_features", ["auto", "log2", "sqrt"])
        max_depth = hp.Int("max_depth", 2, 12)
        min_samples_leaf = hp.Int("min_samples_leaf", 1, 10)
        max_leaf_nodes = hp.Int("max_leaf_nodes", 10, 100)
        min_weight_fraction_leaf = hp.Float(
            "min_weight_fraction_leaf", min_value=0.1, max_value=0.5
        )
        ccp_alpha = hp.Float("ccp_alpha", min_value=0.01, max_value=4)
        model = tree.DecisionTreeRegressor(
            splitter=splitter,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            max_leaf_nodes=max_leaf_nodes,
        )
        return model


hypermodel = RF()
# Find optimal hyperparameters
tuner = kt.tuners.SklearnTuner(
    oracle=kt.oracles.BayesianOptimizationOracle(
        # Keras docs: "Note that for this Tuner, the objective for the Oracle should always be set to Objective('score', direction='max')"
        objective=kt.Objective("score", "max"),
        max_trials=25,
    ),
    hypermodel=hypermodel,
    scoring=metrics.make_scorer(
        metrics.mean_squared_error, greater_is_better=False
    ),  # mean_absolute_error, mean_squared_error, max_error
    cv=model_selection.RepeatedKFold(n_splits=7, n_repeats=1, random_state=1),
    project_name="Keras_tuner_metadata/tree",
    overwrite=True,
)
tuner.search(features, labels)
# Show the results
tuner.results_summary(num_trials=3)
# Build the model with the optimal hyperparameters
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
best_model = tuner.hypermodel.build(best_hps)
best_model.fit(features, labels)

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
with open("models/_tree.pkl", "wb") as f:
    pickle.dump(best_model, f)
