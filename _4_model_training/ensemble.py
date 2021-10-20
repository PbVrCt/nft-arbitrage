import pickle

import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import StackingRegressor
from sklearn.base import ClassifierMixin, TransformerMixin
from sklearn.pipeline import Pipeline
from matplotlib import pyplot as plt
import seaborn as sns

from _4_model_training.ensemble_model import EnsembleModel

# Load the data
features = pd.read_csv(".\data\\set_train_val_features.csv", index_col=[0])
labels = pd.read_csv(".\data\\set_train_val_labels.csv", index_col=[0])
test_features = pd.read_csv(".\data\\set_holdout1_features.csv", index_col=[0])
test_labels = pd.read_csv(".\data\\set_holdout1_labels.csv", index_col=[0])
final_test_features = pd.read_csv(".\data\\set_holdout2_features.csv", index_col=[0])
final_test_labels = pd.read_csv(".\data\\set_holdout2_labels.csv", index_col=[0])
# Load the base models
models = dict()
with open("./models/_GBM.pkl", "rb") as f:
    models["GBM"] = pickle.load(f)
with open("./models/_lightGBM.pkl", "rb") as f:
    models["lGBM"] = pickle.load(f)
with open("./models/_tree.pkl", "rb") as f:
    models["tree"] = pickle.load(f)
with open("./models/_KNN.pkl", "rb") as f:
    models["KNN"] = pickle.load(f)
with open("./models/_polynomial.pkl", "rb") as f:
    models["poly"] = pickle.load(f)
# Create the ensemble
estimators = list()
for _, model in models.items():
    estimators.append(model)
ensemble = EnsembleModel(estimators=estimators, final_estimator=LinearRegression())
# Fit the ensemble
ensemble.fit(features, labels)
models["ensemble"] = ensemble
# Save the model
with open("models/ensemble.pkl", "wb") as f:
    pickle.dump(ensemble, f)
    print("saved")
# Check how the models' predictions correlate
pred, names = list(), list()
for name, model in models.items():
    pred.append(model.predict(features))
    names.append(name)
pred = np.array(pred)
sns.heatmap(np.corrcoef(pred), xticklabels=names, yticklabels=names, annot=True)
plt.show()
# Compare the model results on a holdout set
results, names = list(), list()
for name, model in models.items():
    pred = model.predict(test_features)
    scores = np.subtract(test_labels.to_numpy().ravel(), pred)
    results.append(scores)
    names.append(name)
    print(">%s %.3f (%.3f)" % (name, np.mean(scores), np.std(scores)))
plt.boxplot(results, labels=names, showmeans=True)
plt.show()

# # Do the final test on the test set
# predictions = ensemble.predict(final_test_features)
# print(
#     "\n",
#     "Score on the test set: ",
#     metrics.mean_absolute_error(final_test_labels, predictions),
# )
