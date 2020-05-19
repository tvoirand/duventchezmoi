"""
GFS data downloading module.
"""

import os
import urllib.request
import datetime
import math


def create_gfs_url(
    run_date, extent, forecast_hours
):
    """
    Generates GFS data request.
    Input:
        -run_date           str (format YYYYmmdd)
        -extent             [float, float, float, float] (W, N, E, S)
        -forecast_hours     int
    """

    # preparing parameters
    step = "00"
    grid = "0.25".replace(".", "p")
    forecast_hours = "{}".format(forecast_hours).zfill(3)
    levels = ["planetary_boundary_layer"]
    variables = ["UGRD", "VGRD"]
    left_lon = extent[0]
    right_lon = extent[2]
    top_lat = extent[1]
    bottom_lat = extent[3]

    # creating url
    url = "https://nomads.ncep.noaa.gov"
    url += "/cgi-bin/filter_gfs_{0}.pl?file=gfs.t{1}z.pgrb2.{2}.f{3}".format(
        grid,
        step,
        grid,
        forecast_hours
    )
    for level in levels:
        url += "&lev_{}=on".format(level)
    for variable in variables:
        url += "&var_{}=on".format(variable)
    url += "&subregion="
    url += "&leftlon={}".format(left_lon)
    url += "&rightlon={}".format(right_lon)
    url += "&toplat={}".format(top_lat)
    url += "&bottomlat={}".format(bottom_lat)
    url += "&dir=%2Fgfs.{0}%2F{1}".format(run_date, step)

    return url


def download_from_url(input_url, output_file, verbose=False):
    """
    Download from given url, and store responde in given output file.
    Input:
        -input_url      str
        -output_file    str (full path)
        -verbose        boolean
    """

    if verbose:
        print("Downloading: {}".format(input_url))

    response = urllib.request.urlopen(input_url)

    try:
        html = response.read()
    except:
        exit("Error while downloading file")

    if len(html) > 0:
        f = open(output_file, "wb")
        f.write(html)
        return True
    else:
        return False



def download_gfs(coordinates, data_path):
    """
    Download today's GFS forecast for given coordinates.
    Input:
        -coordinates    [float, float]
            lat, lon
        -data_path      str
    """

    # get run date
    run_date_str = datetime.datetime.now().strftime("%Y%m%d")
    run_date_obj = datetime.datetime.strptime(run_date_str, "%Y%m%d")

    # create extent on 0.25 deg grid around given coordinates
    extent = [
        math.floor(coordinates[1] * 4) / 4,    # smallest lon (W bound)
        math.ceil(coordinates[0] * 4) / 4,     # greatest lat (N bound)
        math.ceil(coordinates[1] * 4) / 4,     # greatest lon (E bound)
        math.floor(coordinates[0] * 4) / 4,    # smallest lat (S bound)
    ]

    # GFS performs 16 days forecast
    GFS_max_forecast_hours = 72#384

    for forecast_hours in range(GFS_max_forecast_hours + 1):

        # create output filename
        forecast_date = run_date_obj + datetime.timedelta(hours = forecast_hours)
        output_file = "{}.grib2".format(forecast_date.strftime("%Y%m%d_%H%S"))

        # create URL
        url = create_gfs_url("20200517", extent, forecast_hours)

        # download file
        download_from_url(url, os.path.join(data_path, output_file), verbose=True)

    return 0


if __name__ == "__main__":

    coordinates = [44.834546, -0.566572]
    data_path = "/Users/thibautvoirand/creation/programmation/duventchezmoi/data"

    print(download_gfs(coordinates, data_path))
