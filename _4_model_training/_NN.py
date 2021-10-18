import os
import json
import datetime
import pickle

import pandas as pd
import tensorflow as tf
import keras_tuner as kt

from _3_preprocessing.preprocessing_fns import preprocessing_fn_3
from _4_model_training.reduce_mem_usage import reduce_mem_usage
from _4_model_training._NNmodel import NNmodel

# Load the feature engineering utilities
with open("./features/feature_set_3_ohe.pickle", "rb") as f:
    ohe = pickle.load(f)
with open("./features/feature_set_3_scaler.pickle", "rb") as f:
    scaler = pickle.load(f)
with open("./features/combo_scores.txt") as f:
    for i in f.readlines():
        combo_scores = i
combo_scores = eval(combo_scores)
# Load the data
train = pd.read_csv(".\data\\set_train_val.csv", index_col=[0, 1])
holdout = pd.read_csv(".\data\\set_holdout1.csv", index_col=[0, 1])
# Use preprocessing_fn_n to engineer feature set n
train = preprocessing_fn_3(combo_scores, scaler=scaler, encoder=ohe).transform(train)
holdout = preprocessing_fn_3(combo_scores, scaler=scaler, encoder=ohe).transform(
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
# Split in training and validation sets
train_features = (
    df.iloc[: -int(train_val.shape[0] * 0.2)]
    .loc[:, train_val.columns.difference(["Priceby100", "PriceUSD"])]
    .to_numpy()
)
train_labels = (
    train_val.iloc[: -int(train_val.shape[0] * 0.2)].loc[:, "PriceBy100"].to_numpy()
)
val_features = (
    train_val.iloc[-int(train_val.shape[0] * 0.2) :]
    .loc[:, train_val.columns.difference(["Priceby100", "PriceUSD"])]
    .to_numpy()
)
val_labels = (
    train_val.iloc[-int(train_val.shape[0] * 0.2) :].loc[:, "PriceBy100"].to_numpy()
)
# Define the model: NN
hypermodel = NNmodel()
# Find optimal hyperparameters
# # Define a class to implement tunable callbacks
class MyTuner(kt.BayesianOptimization):
    def run_trial(self, *args, **kwargs):
        patience = hp.Int("patience", 0, 10, default=5)
        early_stopping = tf.keras.callbacks.EarlyStopping(patience=patience)
        log_dir = "TensorBoard_logs/NN/" + datetime.datetime.now().strftime(
            "%H%M%S-%Y%m%d"
        )
        tensorboard_callback = tf.keras.callbacks.TensorBoard(
            log_dir=log_dir, histogram_freq=1
        )
        reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
            factor=0.8,
            patience=patience,
            min_lr=0.000001,
            verbose=0,
            monitor="val_rmse",
        )
        callbacks = [
            reduce_lr,
            # early_stopping,
            tensorboard_callback,
        ]
        super(MyTuner, self).run_trial(*args, **kwargs, callbacks=callbacks)


# # Initialize the tuner
hp = kt.HyperParameters()
# hp.Fixed("clipnorm", value=1)
# hp.Fixed("clipvalue", value=0.5)
# hp.Fixed("batchnorm", value=True)
# hp.Fixed("hidden_activation", value="relu")
# hp.Fixed("optimizer", value="adam")
# hp.Fixed("patience", value=100)
tuner = MyTuner(
    hypermodel=hypermodel,
    hyperparameters=hp,
    objective=kt.Objective("val_loss", direction="min"),
    max_trials=5,
    seed=50,
    project_name="Keras_tuner_metadata/NN",
    overwrite=False,
)
# # Try hyperparameter combinations
tuner.search(
    train_features,
    train_labels,
    epochs=15,
    validation_data=(val_features, val_labels),
    # batch_size=32,
    verbose=1,
    use_multiprocessing=True,
)
# Build the model with the optimal hyperparameters
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
best_model = tuner.hypermodel.build(best_hps)
# Fit the final model to the train and validation sets
# # Callbacks
patience = best_hps.get("patience")
early_stopping = tf.keras.callbacks.EarlyStopping(patience=patience)
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    factor=0.7, patience=patience, min_lr=0.000001, verbose=0
)
# # Fit
history = best_model.fit(
    train_features,
    train_labels,
    epochs=50,
    validation_data=(val_features, val_labels),
    callbacks=[early_stopping, reduce_lr],
    batch_size=32,
    verbose=0,
)
# Show the results on the train and validation sets
print("\n")
tuner.results_summary(num_trials=1)
best_model.summary()

# # Do the final test on the test set
# result = best_model.evaluate(test_features, test_labels, verbose = 0)
# print("[test loss, test metrics]:", result)

# # Save the model
best_model.save("models/_NN.tf")
