import pickle

import pandas as pd
import keras_tuner as kt
from sklearn import tree
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline
import matplotlib.pyplot as plt


from _2_model_training.reduce_mem_usage import reduce_mem_usage

# Load data and split sets
df = pd.read_csv(".\data\\full_engineered.csv", index_col=[0])
df = reduce_mem_usage(df)
features = (
    df.iloc[:-3000]
    .loc[:, df.columns.difference(["Priceby100", "PriceUSD", "Price"])]
    .to_numpy()
)
labels = df.iloc[:-3000].loc[:, "Price"].to_numpy()
test_features = (
    df.iloc[-3000:]
    .loc[:, df.columns.difference(["Priceby100", "PriceUSD", "Price"])]
    .to_numpy()
)
test_labels = df.iloc[-3000:].loc[:, "Price"].to_numpy()

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
    index=df.loc[:, df.columns != "Price"].columns,
)
feat_imp.nlargest(20).plot(kind="barh", figsize=(10, 6))
plt.tight_layout()
plt.draw()
plt.pause(10)

# Do the final test on the test set
predictions = best_model.predict(test_features)
print(
    "\n",
    "Score on the test set: ",
    metrics.mean_squared_error(test_labels, predictions),
)

# Save the model
with open("_2_model_training/_tree.pkl", "wb") as f:
    pickle.dump(best_model, f)
