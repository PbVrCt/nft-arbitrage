import pickle

import pandas as pd
import keras_tuner as kt
from sklearn.svm import SVR, LinearSVC
from sklearn import metrics
from sklearn import model_selection
from sklearn import pipeline
from sklearn.metrics import accuracy_score

# Load the
df = pd.read_csv(".\data\\full_engineered.csv", index_col=[0])
features = df.iloc[:-3000].loc[:, df.columns != "Price"].to_numpy()
labels = df.iloc[:-3000].loc[:, "Price"].to_numpy()
test_features = df.loc[-3000:].loc[:, df.columns != "Price"].to_numpy()
test_labels = df.loc[-3000:].loc[:, "Price"].to_numpy()
# Define the model: Support Vector Regressor
class SVM(kt.HyperModel):
    def build(self, hp):
        C = hp.Float("C", 1.0, 20.0, step=5)
        # kernel = hp.Choice("kernel", ["linear", "rbf", "poly", "sigmoid"])
        gamma = gamma = hp.Float("gamma", 0.01, 1, step=0.01)
        model = SVR(C=C, gamma=gamma, kernel="linear")
        return model


hypermodel = SVM()
# Find optimal hyperparameters
tuner = kt.tuners.SklearnTuner(
    oracle=kt.oracles.BayesianOptimizationOracle(
        # Keras docs: "Note that for this Tuner, the objective for the Oracle should always be set to Objective('score', direction='max')"
        objective=kt.Objective("score", "max"),
        max_trials=5,
    ),
    hypermodel=hypermodel,
    scoring=metrics.make_scorer(metrics.mean_squared_error, greater_is_better=False),
    # Would be more appropiate to prune the sets based on label overlap, and possibly also to do the kind of CV described in "Advances in Financial ML"
    # but for now using .TimeSeriesSplit() with the gap parameter does the job
    cv=model_selection.RepeatedKFold(n_splits=10, n_repeats=3, random_state=1),
    project_name="Keras_tuner_metadata/SVM",
    overwrite=True,
)
tuner.search(features, labels)
# Show the results
tuner.results_summary(num_trials=3)
# Build the model with the optimal hyperparameters
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
best_model = tuner.hypermodel.build(best_hps)

# # Do the final test on the test set
best_model.fit(features, labels)
predictions = best_model.predict(test_features)
print(
    "\n",
    "Score on the test set: ",
    metrics.mean_squared_error(test_labels, predictions),
)

# Save the model
with open("model_training/_SVM.pkl", "wb") as f:
    pickle.dump(best_model, f)
