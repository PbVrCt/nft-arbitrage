"""
Great Expectations is a library meant for data validation. In this project it is showcased by using it for checking
for missing values and for the number of rows for each stock. Although it was not really needed for just that, 
the library is modular, fairly simple to use, and has hooks for many popular technologies: it could be easily implemented 
without much effort in bigger projects to do more exhaustive data validation
"""
import os
import pathlib
import json

import pandas as pd
import numpy as np
import great_expectations as ge
from great_expectations.core.expectation_configuration import ExpectationConfiguration

# Load data
PATH = pathlib.Path(__file__).resolve().parent / "0_raw data"
df_ohlcv = ge.read_csv(
    os.path.join(PATH, "raw_ohlcv.csv"), index_col=[0, 1], parse_dates=["Date"]
)
df_fndmt = ge.read_csv(
    os.path.join(PATH, "raw_fundamental.csv"),
    index_col=[0, 1],
    parse_dates=["Date", "Period_beginning"],
)
context = ge.get_context()
# Print info on the data
print(
    "Number of stocks in the ohlcv data: ",
    len(df_ohlcv.index.get_level_values(0).unique()),
)
print(
    "Number of stocks in the fndmt data: ",
    len(df_fndmt.index.get_level_values(0).unique()),
)
og_stocks = set(df_ohlcv.index.get_level_values(0).unique()).intersection(
    df_fndmt.index.get_level_values(0).unique()
)
stocks = og_stocks.copy()
print("Number of stocks common to both: ", len(stocks))
print("Number of fundamental features: ", len(df_fndmt.columns))
og_fndmt_features = set(df_fndmt.columns)
fndmt_features = og_fndmt_features.copy()

# DATA SOURCE 1: OHLCV
df_ohlcv = df_ohlcv.replace([np.inf, -np.inf], np.nan)
# Check stock expectations
MIN_ROWS = 1000
MAX_FRACTION_NANS = 0.4
suite = context.create_expectation_suite(
    expectation_suite_name="suite", overwrite_existing=True
)
expt_config = ExpectationConfiguration(
    expectation_type="expect_table_row_count_to_be_between",
    kwargs={"min_value": MIN_ROWS},
)
suite.add_expectation(expectation_configuration=expt_config)
for stock in df_ohlcv.index.get_level_values(0).unique():
    results = df_ohlcv.loc[stock].validate(
        expectation_suite=suite, only_return_failures=False
    )
    fraction_nans = df_ohlcv.loc[stock].isnull().sum().sum() / df_ohlcv.loc[stock].size
    if (results.success == False) or (
        fraction_nans > MAX_FRACTION_NANS
    ):  # Not enough rows or Too many missing values
        stocks.discard(stock)
# Check feature/column expectations
for col in df_ohlcv.columns:
    suite = context.create_expectation_suite(
        expectation_suite_name="suite", overwrite_existing=True
    )
    expt_config = ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": col, "mostly": 0.97},
    )
    suite.add_expectation(expectation_configuration=expt_config)
    results = df_ohlcv.validate(expectation_suite=suite, only_return_failures=False)
    if results.success == False:  # Too many missing values
        raise ValueError("Ohlcv data has null values")

# DATA SOURCE 2: FUNDAMENTAL
df_fndmt = df_fndmt.replace([np.inf, -np.inf], np.nan)
# Check stock expectations
MIN_ROWS = 10
MAX_FRACTION_NANS = 0.4
suite = context.create_expectation_suite(
    expectation_suite_name="suite", overwrite_existing=True
)
expt_config = ExpectationConfiguration(
    expectation_type="expect_table_row_count_to_be_between",
    kwargs={"min_value": MIN_ROWS},
)
suite.add_expectation(expectation_configuration=expt_config)
for stock in df_fndmt.index.get_level_values(0).unique():
    results = df_fndmt.loc[stock].validate(
        expectation_suite=suite, only_return_failures=False
    )
    fraction_nans = df_fndmt.loc[stock].isnull().sum().sum() / df_fndmt.loc[stock].size
    if (results.success == False) or (
        fraction_nans > MAX_FRACTION_NANS
    ):  # Not enough rows or Too many missing values
        stocks.discard(stock)
# Check feature/column expectations
MIN_FRACTION_NON_NULLS_PER_COLUMN = 0.75
for col in df_fndmt.columns:
    suite = context.create_expectation_suite(
        expectation_suite_name="suite", overwrite_existing=True
    )
    expt_config = ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": col, "mostly": MIN_FRACTION_NON_NULLS_PER_COLUMN},
    )
    suite.add_expectation(expectation_configuration=expt_config)
    results = df_fndmt.validate(expectation_suite=suite, only_return_failures=False)
    if results.success == False:  # Too many missing values
        fndmt_features.discard(col)
# # Add some features found to be promising in previous analysis
# fndmt_features = fndmt_features.union(['interestExpense','incomeTaxExpense','capitalExpenditures','netIncome','incomeBeforeTax','operatingIncome','sellingGeneralAdministrative','otherCurrentAssets','totalStockholderEquity'])
# Print results
print(
    "Number of stocks common to both without the ones with too much missing data: ",
    len(stocks),
)
print(
    "Number of fundamental features without the ones with too much missing data: ",
    len(fndmt_features),
)
# Save the results
PATH = pathlib.Path(__file__).resolve().parent / "preprocessing_metadata"
PATH.mkdir(parents=True, exist_ok=True)
with open("preprocessing_metadata/metadata_raw_data.json", "w") as f:
    json.dump(
        {
            "Stocks": list(stocks),
            "Fundamental features": list(fndmt_features),
            "Initial stocks": list(og_stocks),
            "Initial fundamental features": list(og_fndmt_features),
        },
        f,
    )
