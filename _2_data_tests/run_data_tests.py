import yaml

from great_expectations import get_context
from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest

# Overwrites loads function due to this issue: https://github.com/pandas-dev/pandas/issues/26068
import pandas as pd
import json

pd.io.json._json.loads = lambda s, *a, **kw: json.loads(s)
#

context = get_context()

# Create the checkpoint
checkpoint_name = "1st_checkpoint"
yaml_config = f"""
name: {checkpoint_name}
config_version: 1.0
class_name: SimpleCheckpoint
run_name_template: "%Y%m%d-%H%M%S-my-run-name-template"
"""
# Run the checkpoint
context.add_checkpoint(**yaml.load(yaml_config, Loader=yaml.FullLoader))
results = context.run_checkpoint(
    checkpoint_name=checkpoint_name,
    validations=[
        {
            "batch_request": {
                "datasource_name": "mysource",
                "data_connector_name": "default_inferred_data_connector_name",
                "data_asset_name": "full_raw.json",
                "data_connector_query": {
                    "index": -1,
                },
            },
            "expectation_suite_name": "suite2",
        },
    ],
)
context.open_data_docs()
