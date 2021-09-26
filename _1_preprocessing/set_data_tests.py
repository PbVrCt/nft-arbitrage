import json

from great_expectations import get_context
from great_expectations.core.expectation_configuration import ExpectationConfiguration

from _0_get_data.queries import tail_parts, back_parts, horn_parts, mouth_parts

context = get_context()

# Suite 1
suite1 = context.create_expectation_suite(
    expectation_suite_name="suite1", overwrite_existing=True
)
# Expectation 1
expt_config = ExpectationConfiguration(
    expectation_type="expect_table_row_count_to_be_between",
    kwargs={"min_value": 1500, "max_value": None},
)
# Save suite
suite1.add_expectation(expectation_configuration=expt_config)
context.save_expectation_suite(
    expectation_suite=suite1, expectation_suite_name="suite1"
)

# Suite 2
suite2 = context.create_expectation_suite(
    expectation_suite_name="suite2", overwrite_existing=True
)
# Expectation 1
class_types = [
    "Aquatic",
    "Beast",
    "Bird",
    "Bug",
    "Plant",
    "Reptile",
    "Mech",
    "Dawn",
    "Dusk",
]
expt_config = ExpectationConfiguration(
    expectation_type="expect_column_distinct_values_to_equal_set",
    kwargs={"column": "Class", "value_set": class_types},
)
suite2.add_expectation(expectation_configuration=expt_config)
# Expectation 2
part_types = ["Aquatic", "Beast", "Bird", "Bug", "Plant", "Reptile"]
part_type_cols = [
    "EyesType",
    "EarsType",
    "BackType",
    "MouthType",
    "HornType",
    "TailType",
]
for column in part_type_cols:
    expt_config = ExpectationConfiguration(
        expectation_type="expect_column_distinct_values_to_equal_set",
        kwargs={"column": column, "value_set": part_types},
    )
    suite2.add_expectation(expectation_configuration=expt_config)
# Expectation 3
# df = pd.read_json("./data/full_raw.json")
for column, values in zip(
    ["Tail", "Back", "Horn", "Mouth"], [tail_parts, back_parts, horn_parts, mouth_parts]
):
    # print(list(set(df[column].unique()) - set(values)))
    expt_config = ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_in_set",
        kwargs={"column": column, "value_set": values, "result_format": "SUMMARY"},
    )
    suite2.add_expectation(expectation_configuration=expt_config)
# Expectation 4
for column in ["Id", "BreedCount"]:
    expt_config = ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": column, "mostly": 1},
    )
    suite2.add_expectation(expectation_configuration=expt_config)
    # Expectation 5
    expt_config = ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_of_type",
        kwargs={"column": column, "type_": "int64"},
    )
    suite2.add_expectation(expectation_configuration=expt_config)
# Expectation 6
expt_config = ExpectationConfiguration(
    expectation_type="expect_column_values_to_not_be_null",
    kwargs={"column": "Price", "mostly": 1},
)
suite2.add_expectation(expectation_configuration=expt_config)
# Expectation 7
expt_config = ExpectationConfiguration(
    expectation_type="expect_column_values_to_be_of_type",
    kwargs={"column": "Price", "type_": "float64"},
)
suite2.add_expectation(expectation_configuration=expt_config)
# Save suite
context.save_expectation_suite(
    expectation_suite=suite2, expectation_suite_name="suite2"
)
