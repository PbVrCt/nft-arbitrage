import pickle

import pandas as pd
import keras_tuner as kt
from sklearn import ensemble
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline
import matplotlib.pyplot as plt


from _2_model_training.reduce_mem_usage import reduce_mem_usage

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
class XGBOOST(kt.HyperModel):  # TODO: change the names to GBM
    def build(self, hp):
        model_type = hp.Choice("model_type", ["xgboost", "random_forest"])
        n_estimators = hp.Int("n_estimators", 10, 200)
        max_depth = hp.Int("max_depth", 3, 20)
        max_samples = hp.Float("max_samples", min_value=0.4, max_value=0.99)
        max_features = hp.Choice(
            "max_features", ["sqrt", "log2"]
        )  # rule of thumb: root(n_features)
        if model_type == "random_forest":
            with hp.conditional_scope("model_type", "random_forest"):
                model = ensemble.RandomForestRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    max_samples=max_samples,
                    max_features=max_features,
                )
        else:
            with hp.conditional_scope("model_type", "xgboost"):
                learning_rate = hp.Float(
                    "learning_rate", min_value=0.001, max_value=0.12
                )
                model = ensemble.GradientBoostingRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    subsample=max_samples,
                    max_features=max_features,
                    learning_rate=learning_rate,
                )
        return model


hypermodel = XGBOOST()
# Find optimal hyperparameters
tuner = kt.tuners.SklearnTuner(
    oracle=kt.oracles.BayesianOptimizationOracle(
        # Keras docs: "Note that for this Tuner, the objective for the Oracle should always be set to Objective('score', direction='max')"
        objective=kt.Objective("score", "max"),
        max_trials=10,
    ),
    hypermodel=hypermodel,
    scoring=metrics.make_scorer(
        metrics.mean_squared_error, greater_is_better=False, squared=False
    ),  # mean_absolute_error, mean_squared_error, max_error
    cv=model_selection.RepeatedKFold(n_splits=7, n_repeats=1, random_state=1),
    project_name="Keras_tuner_metadata/XGBOOST",
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
    metrics.mean_squared_error(test_labels, predictions, squared=False),
)

# Save the model
with open("_2_model_training/_XGBOOST.pkl", "wb") as f:
    pickle.dump(best_model, f)
