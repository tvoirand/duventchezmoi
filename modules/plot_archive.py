"""
Script to plot duventchezmoi data archive.
"""

# standard imports
import os
import argparse
import configparser
import datetime

# local imports
from duventchezmoi import write_report
from duventchezmoi import compute_mean_wind_speed


def plot_archive(report_filename=None):
    """
    Plot duventchezmoi data archive.
    Input:
        -report_filename    str or None
            if None, the plot will be displayed and not saved to a file
    """

    # get project path
    duventchezmoi_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    # read config
    config = configparser.ConfigParser()
    config.read(os.path.join(duventchezmoi_path, "config", "config.ini"))
    threshold = float(config["main"]["threshold"])
    data_path = config["main"]["data_path"]
    units = config["main"]["units"]

    # initiate data array
    data = []

    # loop through dates
    for date_path in [
        os.path.join(data_path, d)
        for d in os.listdir(data_path)
        if os.path.isdir(os.path.join(data_path, d))
    ]:

        # loop through hourly grib files
        for grib_file_path in [
            os.path.join(date_path, f)
            for f in os.listdir(date_path)
            if f.endswith(".grib2")
        ]:

            # compute wind speed
            wind_speed = compute_mean_wind_speed(grib_file_path, units)

            # compare value to threshold
            is_threshold_surpassed = wind_speed > threshold
            if is_threshold_surpassed:  # trigger alert
                is_alert_triggered = True

            # add item in data array
            data.append(
                {
                    "date_str": os.path.splitext(os.path.basename(grib_file_path))[0],
                    "date_obj": datetime.datetime.strptime(
                        os.path.splitext(os.path.basename(grib_file_path))[0],
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
