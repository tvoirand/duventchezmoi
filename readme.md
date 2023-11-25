# Du vent chez moi

A tool to automatically alert me in case of strong winds in my town.

Download GFS surface wind speed forecast around a given set of coordinates.
Sends a report by email in case the forecast surpasses a given threshold.

<img src="docs/example.png" width="50%"/>

## Dependencies

*   Requires Python 3 with the following packages (listed in `environment.yml`):

    *   pygrib
    *   numpy
    *   matplotlib
    *   google-api-python-client
    *   google-auth
    *   google-auth-oauthlib

*   Email server which can be accessed automatically

## Installation

*   Create the necessary environment using for example `conda env create -f environment.yml`

*   Create a custom config file named `config/config.ini` based on the example given in `config/example_config.ini`

*   Write a crontab to run `python duventchezmoi.py` periodically using the corresponding environment

## Contribute

Please feel free to contribute by opening issues or pull-requests!
