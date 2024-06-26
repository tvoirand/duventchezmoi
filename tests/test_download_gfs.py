"""Unit tests for the 'download_gfs.py' module."""

# standard library
import datetime
import tempfile
from pathlib import Path
from unittest.mock import patch

# third party
import pytest

# current project
from duventchezmoi.download_gfs import create_gfs_url
from duventchezmoi.download_gfs import download_from_url
from duventchezmoi.download_gfs import download_gfs


def test_create_gfs_url():

    # generate mock data
    run_date = "20220330"
    extent = [-0.75, 45.0, -0.50, 44.75]
    forecast_hours = 10

    # assert that the URL is generated as expected
    expected_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t00z.pgrb2.0p25.f010&lev_planetary_boundary_layer=on&var_UGRD=on&var_VGRD=on&subregion=&leftlon=-0.75&rightlon=-0.5&toplat=45.0&bottomlat=44.75&dir=%2Fgfs.20220330%2F00%2Fatmos"
    assert create_gfs_url(run_date, extent, forecast_hours) == expected_url


@pytest.mark.parametrize("response_size, expected_result", [(100, True), (0, False)])
@patch("duventchezmoi.download_gfs.urllib.request.urlopen")
def test_download_from_url(mock_urlopen, response_size, expected_result):

    # mock the result of reading the downloaded file
    mock_urlopen.return_value.read.return_value = b"X" * response_size

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "duventchezmoi_test_download.grib2"

        # check that the function returns the expected result (boolean)
        assert (
            download_from_url("https://example.com", output_path, verbose=False)
            == expected_result  # noqa W503
        )

        # check that the output file is created
        if response_size == 0:
            assert not output_path.exists()
        else:
            assert output_path.exists()


@patch("duventchezmoi.download_gfs.datetime")
@patch("duventchezmoi.download_gfs.download_from_url")
def test_download_gfs(mock_download_from_url, mock_datetime):

    # mock the run date to generate download url and output filename
    mock_datetime.now.return_value.strftime.return_value = "20220330"
    mock_datetime.strptime.return_value = datetime.datetime(2022, 3, 30)

    with tempfile.TemporaryDirectory() as temp_dir:
        data_path = Path(temp_dir)
        extent = [-0.75, 45.0, -0.50, 44.75]  # mock data

        # assert that download_from_url is called 121 times, without actually calling it
        download_gfs(extent, data_path)
        assert mock_download_from_url.call_count == 121
