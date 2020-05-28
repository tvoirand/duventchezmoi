"""
Duventchezmoi main script.
"""

# standard packages
import os
import sys
import shutil
import configparser
import math
import datetime

# third party packages
import pygrib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.dates as mdates

# local modules
from modules.download_gfs import download_gfs
from modules.send_mail import send_mail


def send_report(
    recipient,
    sender,
    password,
    report_file,
    smtp_server,
    smtp_port,
    lat,
    lon,
    threshold,
    units
):
    """
    Send report via email.
    Input:
        -recipient          str
        -sender             str
        -password           str
        -report_file        str
        -smtp_server        str
        -smtp_port          str
        -lat                float
        -lon                float
        -threshold          float
        -units              str
    """

    subject = "Wind speed alert from Duventchezmoi"

    contents = ""
    contents += "Hi,\n\n"
    contents += "An alert was triggered for the following monitoring configuration:\n"
    contents += "Latitude, longitude (decimal degrees): {:5.2f}, {:5.2f}\n".format(
        lat, lon
    )
    contents += "Threshold ({}): {:5.2f}\n\n".format(units, threshold)
    contents += "Wind speed forecast from the GFS model in the next 16 days "
    contents += "showed values higher than the given threshold over the monitoring coordinates.\n"
    contents += "See the report in attachment for more details.\n\n"
    contents += "This is an automatic email sent by the Duventchezmoi application."

    send_mail(
        sender,
        password,
        recipient,
        [],  # cc
        [],  # bcc
        subject,
        contents,
        [report_file],
        smtp_server,
        smtp_port,
    )


def write_report(data, file_name, threshold, units):
    """
    Write alert report displaying wind speed values.
    Input:
        -data       [dict, ...]
            contains for each row:
            {"date_str": str, "date_obj": datetime object, "wind_speed": float, "alert": bool}
        -file_name  str
        -threshold  float
        -units      str
    """

    # preparing data
    dates = [row["date_obj"] for row in data]
    values = [row["wind_speed"] for row in data]
    points_color = []
    for row in data:
        if row["alert"]:
            points_color.append("red")
        else:
            points_color.append("black")

    # creating figure
    fig = plt.figure(figsize=[8.8, 4.8])
    plt.scatter(dates, values, c=points_color, marker="+")  # plotting values
    plt.plot(
        dates, [threshold for i in data], c="black", linewidth=0.5,
    )  # plotting threshold

    # format dates axis
    plt.gca().xaxis.set_ticks([d for d in dates if d.hour == 0])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    # adding labels
    plt.xlabel("Dates")
    plt.ylabel("Wind speed ({})".format(units))
    plt.title("Mean surface wind speed forecast from GFS")

    # add legend
    black_legend = mlines.Line2D(
        [],
        [],
        color="black",
        marker="+",
        linestyle="None",
        label="GFS forecast below threshold",
    )
    red_legend = mlines.Line2D(
        [],
        [],
        color="red",
        marker="+",
        linestyle="None",
        label="GFS forecast above threshold",
    )
    threshold_legend = mlines.Line2D(
        [], [], color="black", linewidth=0.5, label="Threshold"
    )
    plt.legend(
        handles=[black_legend, red_legend, threshold_legend],
        loc="upper left",
        bbox_to_anchor=(1.0, 1.0),
    )

    # handle layout
    plt.tight_layout()

    # saving file
    plt.savefig(file_name, format="pdf")


def compute_mean_wind_speed(grib2_file, units):
    """
    Compute mean wind speed from GFS products.
    Input:
        -grib2_file     str
        -units          str
            either m/s or km/h
    Output:
        -               float
    """

    # open grib2 file
    grbs = pygrib.open(grib2_file)

    # fetch datasets
    u_grb = grbs.select(name="U component of wind")[0]
    v_grb = grbs.select(name="V component of wind")[0]

    # compute wind speed from U and V velocities
    wind_speed = np.sqrt(u_grb.values ** 2 + v_grb.values ** 2)

    # compute areal mean
    mean_wind_speed = np.mean(wind_speed)

    # units conversion
    if units.lower() == "km/h":
        mean_wind_speed *= 3.6

    return mean_wind_speed


def duventchezmoi(config_path):
    """
    Duventchezmoi main function.
    Input:
        -config_path    str
    """

    # read config
    config = configparser.ConfigParser()
    config.read(config_path)
    lat = float(config["main"]["lat"])
    lon = float(config["main"]["lon"])
    threshold = float(config["main"]["threshold"])
    data_path = config["main"]["data_path"]
    cleaning = config["main"]["cleaning"].lower() in ["true"]
    units = config["main"]["units"]
    recipient = config["mail"]["recipient"]
    sender = config["mail"]["sender"]
    password = config["mail"]["password"]
    smtp_server = config["mail"]["smtp_server"]
    smtp_port = int(config["mail"]["smtp_port"])

    # create extent on 0.25 deg grid around given coordinates
    extent = [
        math.floor(lon * 4) / 4,  # smallest lon (W bound)
        math.ceil(lat * 4) / 4,  # greatest lat (N bound)
        math.ceil(lon * 4) / 4,  # greatest lon (E bound)
        math.floor(lat * 4) / 4,  # smallest lat (S bound)
    ]

    # creating download directory
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    todays_data_path = os.path.join(data_path, today_str)
    if not os.path.exists(todays_data_path):
        os.makedirs(todays_data_path)

    # download gfs data
    try:
        download_gfs(extent, todays_data_path)
    except:
        sys.exit("Error in GFS data download")

    # loop through all hourly forecast gfs files
    data = []  # initiate list to store results for each forecast
    is_alert_triggered = False  # initiate boolean to trigger alerts
    for file in os.listdir(todays_data_path):

        # compute mean wind speed
        wind_speed = compute_mean_wind_speed(os.path.join(todays_data_path, file), units)

        # compare value to threshold
        is_threshold_surpassed = wind_speed > threshold
        if is_threshold_surpassed:  # trigger alert
            is_alert_triggered = True

        # store results in list
        data.append(
            {
                "date_str": os.path.splitext(file)[0],
                "date_obj": datetime.datetime.strptime(
                    os.path.splitext(file)[0], "%Y%m%d_%H%M"
                ),
                "wind_speed": wind_speed,
                "alert": is_threshold_surpassed,
            }
        )

    # if alert triggered
    if is_alert_triggered:

        # write report
        report_filename = os.path.join(data_path, "{}.pdf".format(today_str))
        write_report(data, report_filename, threshold, units)

        # send report via email
        send_report(
            recipient,
            sender,
            password,
            report_filename,
            smtp_server,
            smtp_port,
            lat,
            lon,
            threshold,
            units
        )

    # clear data path
    if cleaning:
        for d in [
            di
            for di in os.listdir(data_path)
            if os.path.isdir(os.path.join(data_path, di))
        ]:
            shutil.rmtree(os.path.join(data_path, di))


if __name__ == "__main__":

    duventchezmoi_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(duventchezmoi_path, "config", "config.ini")

    duventchezmoi(config_path)
