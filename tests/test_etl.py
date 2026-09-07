from unittest.mock import MagicMock, patch

import pandas as pd

from pipeline.cleaning.cleaner import clean_dataframe
from pipeline.run_etl import run_etl
from pipeline.validation.validator import validate_dataframe


def test_clean_and_validate_dataframe():
    df = pd.DataFrame(
        [
            {"Customer ID": 1, "Order Amount": "100.50", "Segment": " Enterprise "},
            {"Customer ID": 1, "Order Amount": "100.50", "Segment": " Enterprise "},
            {"Customer ID": 2, "Order Amount": "", "Segment": None},
        ]
    )

    cleaned = clean_dataframe(df)
    validation = validate_dataframe(cleaned)

    assert validation["rows"] == 2
    assert validation["duplicates"] == 0
    assert validation["columns"] == ["customer_id", "order_amount", "segment"]
    assert validation["missing_values"]["segment"] == 0


def test_run_etl_with_replace_truncates_tables_before_load():
    empty_df = pd.DataFrame()
    mock_transform = MagicMock(return_value=empty_df)
    mock_dataset = {
        "customers": {
            "file": "customers.csv",
            "transform": mock_transform,
        },
    }

    with (
        patch("pipeline.run_etl.truncate_tables") as mock_truncate,
        patch("pipeline.run_etl.load_dataframe_to_db", return_value=0) as mock_load,
        patch("pipeline.run_etl.load_csv", return_value=empty_df),
        patch("pipeline.run_etl.clean_dataframe", return_value=empty_df),
        patch("pipeline.run_etl.validate_dataframe", return_value={}),
        patch.dict("pipeline.run_etl.DATASETS", mock_dataset, clear=False),
    ):
        run_etl(datasets=["customers"], replace=True)

    mock_truncate.assert_called_once_with(["customers"])
    mock_load.assert_called_once()


def test_run_etl_without_replace_does_not_truncate():
    empty_df = pd.DataFrame()
    mock_transform = MagicMock(return_value=empty_df)
    mock_dataset = {
        "customers": {
            "file": "customers.csv",
            "transform": mock_transform,
        },
    }

    with (
        patch("pipeline.run_etl.truncate_tables") as mock_truncate,
        patch("pipeline.run_etl.load_dataframe_to_db", return_value=0),
        patch("pipeline.run_etl.load_csv", return_value=empty_df),
        patch("pipeline.run_etl.clean_dataframe", return_value=empty_df),
        patch("pipeline.run_etl.validate_dataframe", return_value={}),
        patch.dict("pipeline.run_etl.DATASETS", mock_dataset, clear=False),
    ):
        run_etl(datasets=["customers"], replace=False)

    mock_truncate.assert_not_called()
