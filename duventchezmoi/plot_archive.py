"""
Script to plot duventchezmoi data archive.
"""

# standard library
import argparse
import configparser
import datetime
from pathlib import Path

# current project
from duventchezmoi import compute_mean_wind_speed
from duventchezmoi import write_report


def plot_archive(report_filename=None):
    """Plot duventchezmoi data archive.

    Parameters
    ----------
    report_filename : Path or None
        if None, the plot will be displayed and not saved to a file
    """

    # get project path
    project_path = Path(__file__).resolve().parents[1]

    # read config
    config = configparser.ConfigParser()
    config.read(project_path / "config" / "config.ini")
    threshold = float(config["main"]["threshold"])
    data_path = config["main"]["data_path"]
    units = config["main"]["units"]

    # initiate data array
    data = []

    # loop through dates
    for date_path in [d for d in data_path.iterdir() if d.is_dir()]:

        # loop through hourly grib files
        for grib_file_path in [f for f in date_path.iterdir() if f.name.endswith(".grib2")]:

            # compute wind speed
            wind_speed = compute_mean_wind_speed(grib_file_path, units)

            # compare value to threshold
            is_threshold_surpassed = wind_speed > threshold

            # add item in data array
            data.append(
                {
                    "date_str": grib_file_path.stem,
                    "date_obj": datetime.datetime.strptime(
                        grib_file_path.stem,
                        "%Y%m%d_%H%M",
                    ),
                    "wind_speed": wind_speed,
                    "alert": is_threshold_surpassed,
                }
            )

    # write report
    write_report(data, threshold, units, report_filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--report_filename")
    args = parser.parse_args()

    plot_archive(args.report_filename)
