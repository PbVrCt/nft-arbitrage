import importlib

# _0_data_collection: Run the Go package
# scrape leaderboard data in jupyter

# importlib.import_module("_1_preprocessing.set_data_tests")
# importlib.import_module("_1_preprocessing._0_merge_data")
# importlib.import_module("_1_preprocessing._1_run_data_tests")
# importlib.import_module("_1_preprocessing._2_cleansing")
# importlib.import_module("_1_preprocessing._3_feature_engineering")

importlib.import_module("_2_model_training._GBM")
# importlib.import_module("_2_model_training._lightGBM")
# importlib.import_module("_2_model_training._polynomial")
# importlib.import_module("_2_model_training._tree")
# importlib.import_module("_2_model_training._KNN")

# _3_inference: Run the python offline server by executing the "run-app.bat" file and then run the Go package
