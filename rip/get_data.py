import argparse
import datetime as dt
import logging
import time

import bs4
import pandas as pd
from requests import Session


"""
Scrape deaths from rip.ie between given time frames
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("../scraping.log"), logging.StreamHandler()],
)


logger = logging.getLogger(__name__)
URL = "https://rip.ie"

path = "/Deathnotices/All"
start = ""
end = ""

page_size = 40
page = 1
i_display_length = ["40", "40"]
i_display_start = 0
echo = 0

headers = {
    "authority": "rip.ie",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://rip.ie/Deathnotices/All",
    "accept-language": "en-GB,en;q=0.9,en-IE;q=0.8,en-US;q=0.7",
}


def get_data(display_start, display_length, date_from, date_to, echo=1):

    params = {
        "do": "get_deathnotices_pages",
        "iDisplayStart": display_start,
        "iDisplayLength": display_length,
        "DateFrom": f"{date_from} 00:00:00",
        "DateTo": f"{date_to} 00:00:00",
        "NoWhere": "y",
        "include_fn": "false",
        "sEcho": echo,
        "iColumns": "5",
        "sColumns": "",
        "mDataProp_0": "0",
        "mDataProp_1": "1",
        "mDataProp_2": "2",
        "mDataProp_3": "3",
        "mDataProp_4": "4",
        "iSortingCols": "2",
        "iSortCol_0": "0",
        "sSortDir_0": "desc",
        "iSortCol_1": "0",
        "sSortDir_1": "asc",
        "bSortable_0": "true",
        "bSortable_1": "true",
        "bSortable_2": "true",
        "bSortable_3": "true",
        "bSortable_4": "true",
    }
    logger.info("getting request %s- %s", display_start + 1, display_start + page_size)
    try:
        response = session.get("https://rip.ie/deathnotices.php", params=params)
        data = response.json()

    except Exception as e:
        logger.exception("failed to get data %s", e)
        return []

    deaths = data["aaData"]
    logger.info("retrieved page number %s", data["isarchive"])

    return [
        {
            "surname": x[0],
            "town": x[1],
            "county": x[2],
            "published": x[3],
            "death_data": x[4],
            "id": x[5],
            "link": f"https://rip.ie/showdn.php?dn=x{x[5]}",
            "unknown_1": x[6],
            "first_name": x[7],
            "maiden_name": x[8],
            "address": x[9],
            "image": x[10],
            "unknown_4": x[11],
            "unknown_5": x[12],
            "unknown_6": x[13],
            "unknown_7": x[14],
            "unknown_8": x[15],
        }
        for x in deaths
    ], int(data["iTotalRecords"])


# def scrape(
#     display_start,
#     display_length,
#     date_from="2016-01-01 00:00:00",
#     date_to="2021-08-17 23:59:59",
# ):
#     pages_remaining = True
#
#     while pages_remaining:
#
#         deaths, total_records = get_data(
#             display_start, display_length, date_from, date_to
#         )
#
#         display_start += page_size
#         pages_remaining = display_start < total_records
#         df = pd.DataFrame(deaths)
#         # df.drop_duplicates(subset=["id"], inplace=True)
#         with open("data/data.csv", "a") as f:
#             df.to_csv(f, mode="a", index=False, header=not f.tell())


def save_data(df):
    with open("data/data.csv", "a") as f:
        df.to_csv(f, mode="a", index=False, header=not f.tell())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

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
    from_date = args.from_date
    to_date = args.to_date
    total_deaths = 0

    start = from_date
    end = start + dt.timedelta(days=7)
    session = Session()
    session.headers = headers

    while end < to_date:
        logger.info("getting data from %s to %s", start, end)
        recoords_retrieved = 0
        display_start = 0
        display_length = 40
        echo = 1
        pages_remaining = True
        deaths = []
        while pages_remaining:
            _deaths, total_records = get_data(
                display_start, display_length, start, end, echo=echo
            )
            echo += 1
            deaths.extend(_deaths)
            display_start = display_start + display_length
            pages_remaining = total_records > display_start

        total_deaths += len(deaths)
        start = end
        end = end + dt.timedelta(days=7)
        # save on the fly in case it fails or crashes
        save_data(pd.DataFrame(deaths))
    logger.info("Complete with %s deaths %s to %s", total_deaths, from_date, to_date)
