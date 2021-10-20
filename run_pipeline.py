import importlib

# _0_data_collection: Runs auto on cloud

# _1_retrieve_data_from_cloud: Run the go packages

# importlib.import_module("_2_data_tests.set_data_tests")
# importlib.import_module("_2_data_tests.run_data_tests")

# importlib.import_module("_3_preprocessing._1_data_cleansing")
# importlib.import_module("_3_preprocessing._2_prepare_feature_sets")
# importlib.import_module("_3_preprocessing._3_split_data_in_sets")

importlib.import_module("_4_model_training._GBM")
importlib.import_module("_4_model_training._lightGBM")
importlib.import_module("_4_model_training._tree")
importlib.import_module("_4_model_training._polynomial")
importlib.import_module("_4_model_training._KNN")
importlib.import_module("_4_model_training.ensemble")

# _5_inference: First run the python offline server by executing the "run-app.bat" file
#               and then run the Go package inside "_5_inference/ml"
