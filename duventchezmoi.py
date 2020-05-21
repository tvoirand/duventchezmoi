"""
Duventchezmoi main script.
"""

import os

def duventchezmoi(config_path):
    """
    Duventchezmoi main function.
    Input:
        -config_path    str
    """

    # download gfs data

    # performe daily average of gfs data

    # compare results to threshold

    # if alert triggered

    # write report

    # send email

if __name__ == "__main__":

    duventchezmoi_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(duventchezmoi_path, "config", "config.ini")

    duventchezmoi(config_path)
