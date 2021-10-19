"""This api does real time inference by serving an ML model trained in Python to predict on data extracted with Go.
 """
import pickle
import time

import pandas as pd
import numpy as np
from flask import Flask, redirect, request, jsonify, make_response, send_file
from flask_restful import Resource, Api, abort

from _3_preprocessing.preprocessing_fns import features_to_show

# Model
with open("./models/ensemble.pkl", "rb") as f:
    model = pickle.load(f)
# Api
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
                "BreedCount",
                "Image",
                "PriceBy100",
                "PriceUSD",
            ],
        ]
        df = df.drop(["Image", "PriceBy100", "PriceUSD"], axis=1)
        # Model serving

        # start = time.time()
        price_predictions = pd.Series(model.predict(df)).rename("Prediction")
        # end = time.time()
        # print("Time elapsed in doing predictions: ", end - start, "s")

        # Output back to Go
        df = pd.concat(
            [
                basic_info.reset_index(),
                price_predictions,
                features_to_show(df).reset_index(),
            ],
            axis=1,
        )
        form = df.to_dict(orient="records")
        return form


api.add_resource(NewR, "/api/predict")
