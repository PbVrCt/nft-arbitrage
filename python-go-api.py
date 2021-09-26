import pickle

import pandas as pd
from flask import Flask, redirect, request, jsonify, make_response, send_file
from flask_restful import Resource, Api, abort

from _1_preprocessing.feature_eng_utils import score_df

# Model
with open("./_2_model_training/_XGBOOST.pkl", "rb") as f:  # XGBOOST,lightGBM,KNN,tree
    model = pickle.load(f)
# One hot encoder for the axie class
with open("./_1_preprocessing/one_hot_encoder.pickle", "rb") as f:
    oh_enc = pickle.load(f)
# Card and combo scores
with open("./_1_preprocessing/scores_lookup.txt") as f:
    for i in f.readlines():
        scores_lookup = i
scores_lookup = eval(scores_lookup)

app = Flask(__name__, static_url_path="", static_folder="dist")
api = Api(app)


class NewR(Resource):
    def post(self):
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
                "Price",
            ],
        ]
        df = df.drop(["Image", "Price"], axis=1)
        df = score_df(df, scores_lookup, class_encoder=oh_enc)  # feature engineering
        price_predictions = df.apply(
            lambda row: model.predict(row.values.reshape(1, -1))[0], axis=1
        )  # predictions
        df = (
            pd.concat(
                [basic_info, price_predictions, df[["Hp", "Sp", "Sk", "Mr"]]], axis=1
            )
            .rename({0: "Prediction"}, axis=1)
            .reset_index()
        )
        form = df.to_dict(orient="records")
        return form


api.add_resource(NewR, "/api/predict")
