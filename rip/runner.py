import argparse
import datetime as dt
import itertools
import logging
import math
import time
from multiprocessing import Pool, cpu_count

import bs4
import pandas as pd
from dateutil import parser
from requests import Session

from rip.get_data import get_irl_data
from rip.uk_deaths import get_deaths

IRELAND = "irl"
UK = "uk"
fns = {IRELAND: get_irl_data, UK: get_deaths}
"""
Scrape deaths from rip.ie between given time frames
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("../data.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--region",
        choices=[IRELAND, UK],
        default=IRELAND,
        help="Region used to aquire deaths",
    )
    parser.add_argument(
        "-f",
        "--from_date",
        type=dt.date.fromisoformat,
        help="The date used to start data retrieval",
    )
    parser.add_argument(
        "-t",
        "--to_date",
        type=dt.date.fromisoformat,
        default=dt.datetime.now().strftime("%Y-%m-%d"),
        help="The date used to start data retrieval",
        required=False,
    )

    args = parser.parse_args()
    fn = fns[args.region]
    fn(args.from_date, args.to_date)
