import importlib

importlib.import_module("_0_get_data.get_data")
# scrape leaderboard data in jupyter

importlib.import_module("_1_preprocessing.0_merge_data")
importlib.import_module("_1_preprocessing.1_outlier_cleansing")
importlib.import_module("_1_preprocessing.2_feature_engineering")

importlib.import_module("_2_model_training._RF")
importlib.import_module("_2_model_training._KNN")
importlib.import_module("_2_model_training._polynomial")
importlib.import_module("_2_model_training._tree")
