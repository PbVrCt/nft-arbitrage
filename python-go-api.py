"""This api serves the preprocessing utilies and ml model for real time inference on the data extracted with go.
 It loads the same preprocessing utilitiles that were used for model training"""
import pickle

import pandas as pd
import numpy as np
from flask import Flask, redirect, request, jsonify, make_response, send_file
from flask_restful import Resource, Api, abort

from _1_preprocessing.feature_eng_utils import preprocessing_fn

# Model
with open("./_2_model_training/_GBM.pkl", "rb") as f:
    model = pickle.load(f)
# from tensorflow.keras.models import load_model # Tensorflow's "model.predict()" is too slow
# model = load_model("./_2_model_training/_NN.tf")

# One hot encoder
with open("./_1_preprocessing/one_hot_encoder.pickle", "rb") as f:
    oh_enc = pickle.load(f)
# Scaler
with open("./_1_preprocessing/scaler.pickle", "rb") as f:
    scaler = pickle.load(f)
# Card and combo scores
with open("./_1_preprocessing/combo_scores.txt") as f:
    for i in f.readlines():
        combo_scores = i
combo_scores = eval(combo_scores)

app = Flask(__name__, static_url_path="", static_folder="dist")
api = Api(app)


class NewR(Resource):
    def post(self):
        # form coming from Go
        form = request.get_json()
        df = pd.DataFrame(form)
        df = df.set_index("Id")
        basic_info = df.loc[
            :,
            [
                "Class",
                "Eyes",
                "Ears",
                "Back",
                "Mouth",
                "Horn",
                "Tail",
                "Image",
                "PriceBy100",
                "PriceUSD",
            ],
        ]
        df = df.drop(["Image", "PriceBy100", "PriceUSD"], axis=1)
        # Feature engineering
        df = preprocessing_fn(
            df,
            combo_scores,
            encoder=oh_enc,
            scaler=scaler,
            fit_encoder=False,
            fit_scaler=False,
        )
        # Predictions; Sklearn
        price_predictions = df.apply(
            lambda row: model.predict(row.values.reshape(1, -1))[0], axis=1
        ).rename("Prediction")

        # Predictions; Tensorflow
        # price_predictions = df.apply(
        #     lambda row: model.predict(
        #         row.values.reshape(1, -1), batch_size=len(row.values.reshape(1, -1))
        #     )[0][0],
        #     axis=1,
        # ).rename("Prediction")

        # Output back to Go
        df = (
            pd.concat(
                [
                    basic_info,
                    price_predictions,
                    df["BreedCount"],
                ],
                axis=1,
            )
            # .rename({0: "Prediction"}, axis=1)
            .reset_index()
        )
        form = df.to_dict(orient="records")
        return form


api.add_resource(NewR, "/api/predict")
