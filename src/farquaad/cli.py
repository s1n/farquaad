import argparse
import json
import logging
import sys

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display

from .distributors.heb import HEB
from .base import Restrictions

from farquaad import __version__

__author__ = "Jason Switzer"
__copyright__ = "Jason Switzer"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from farquaad.cli import heb`,
# when using this Python module as a library.

def heb(driver=None, logger=None):
    return HEB(driver, logger)

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.

def parse_args(args):
    parser = argparse.ArgumentParser(description="Automated Vaccine scheduler")
    parser.add_argument(
        "--version",
        action="version",
        version="farquaad {ver}".format(ver=__version__),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    parser.add_argument(
        "--sanity",
        dest="sanity",
        help="Perform a sanity test to verify the environment and assumptions",
        action="store_true"
    )
    parser.add_argument(
        "-c",
        "--cities",
        dest="cities",
        help="Cities to restrict appointment availability",
        nargs="+",
    )
    parser.add_argument(
        "-d",
        "--distance",
        dest="distance",
        help="Maximum distance (miles) from home (requires --home)",
        type=float,
    )
    parser.add_argument(
        "-H",
        "--home",
        dest="home",
        help="Home location, typically includes zipcode, address, lat/lon, city, etc - uses OpenStreetMap (requires --distance)",
    )
    parser.add_argument(
        "-z",
        "--zip-codes",
        dest="zipcodes",
        help="Zipcodes to restrict appointment availability",
        nargs="+"
    )
    parser.add_argument(
        "-t",
        "--time-delay",
        dest="timedelay",
        help="Time delay between availability checks in seconds",
        type=float,
        default=10.0,
    )
    parser.add_argument(
        "-P",
        "--patient-data",
        dest="patientdata",
        help="Patient automation data file - see form.json for a sample",
        type=argparse.FileType('r'), 
    )
    return parser.parse_args(args)

def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )

def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Initializing the default web driver")
    
    # let's create the driver here so we can reuse it
    display = Display(visible=0, size=(800, 600))
    display.start()
    options = Options()
    options.headless = False
    driver = webdriver.Firefox(options=options)

    # find a store, grab a slot, cleanup
    henryebutts = heb(driver=driver, logger=_logger)

    if args.sanity:
        goodToGo = henryebutts.sanity(args.timedelay)
        if goodToGo:
            _logger.info("Sanity test complete; environment is good")
        else:
            _logger.info("Sanity test complete; environment is not good - check requirements and distributor's website")
        driver.quit()
        display.stop()
        sys.exit(goodToGo ? 1 : 0)
        
    patientData = json.load(args.patientdata)
    restricted = Restrictions(cities=args.cities, zipcodes=args.zipcodes, distance=args.distance)
    appt = None

    while not appt:
        possibleSites = henryebutts.monitor(args.home, restricted, args.timedelay)
        print(possibleSites)
        appt = henryebutts.schedule(possibleSites, patientData)
        if appt:
            _logger.info(f"Appointment scheduled at {appt['name']}")
            break
        #if we didn't break out, all of the slots found booked too quick, start over
    henryebutts.finalize()
    display.stop()
    _logger.info("Auto-registration complete, heck the provided email for the appointment")

def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])

if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m farquaad.cli -H TX,78701 -d 50 -P data/patient.json
    #
    run()
