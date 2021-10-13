import importlib

# _0_data_collection: Run the Go package
# scrape leaderboard data in jupyter
# _1_retrieve_data_from_clod: Run the go package

# importlib.import_module("_2_data_tests.set_data_tests")
# importlib.import_module("_2_data_tests.run_data_tests")

# importlib.import_module("_3_preprocessing._1_cleansing")
importlib.import_module("_3_preprocessing._2_feature_engineering")

importlib.import_module("_4_model_training._GBM")
# importlib.import_module("_4_model_training._lightGBM")
# importlib.import_module("_4_model_training._polynomial")
# importlib.import_module("_4_model_training._tree")
# importlib.import_module("_4_model_training._KNN")

# _5_inference: Run the python offline server by executing the "run-app.bat" file and then run the Go package
