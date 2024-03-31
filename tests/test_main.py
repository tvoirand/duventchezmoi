"""Unit tests for duventchezmoi main script."""

# standard library
import datetime
import tempfile
from pathlib import Path

# third party
import numpy as np

# current project
from duventchezmoi.main import compute_mean_wind_speed
from duventchezmoi.main import write_report


def test_compute_mean_speed():
    grib2_file = Path(__file__).parent / "20240330_0000.grib2"
    units = "km/h"
    expected_result = 18.65
    value = compute_mean_wind_speed(grib2_file, units)
    assert np.round(value, decimals=2) == expected_result
    units = "m/s"
    expected_result = 5.18
    value = compute_mean_wind_speed(grib2_file, units)
    assert np.round(value, decimals=2) == expected_result


def test_write_report():
    mock_data = [
        {
            "date_str": "20220330_0000",
            "date_obj": datetime.datetime(year=2022, month=3, day=30, hour=0, minute=0),
            "wind_speed": 35.0,
            "alert": False,
        },
        {
            "date_str": "20220330_0100",
            "date_obj": datetime.datetime(year=2022, month=3, day=30, hour=1, minute=0),
            "wind_speed": 41.0,
            "alert": True,
        },
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "duventchezmoi_test_report.pdf"
        write_report(mock_data, 40.0, "km/h", output_file)
        assert output_file.exists()
