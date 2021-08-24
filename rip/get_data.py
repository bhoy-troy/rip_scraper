import argparse
import datetime as dt
import itertools
import logging
from multiprocessing import Pool, cpu_count

import pandas as pd
from requests import Session

"""
Scrape deaths from rip.ie between given time frames
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("../data.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)
RIP_HOST = "https://rip.ie"

page_size = 40
page = 1
i_display_length = ["40", "40"]
i_display_start = 0

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
    "referer": f"{RIP_HOST}/Deathnotices/All",
    "accept-language": "en-GB,en;q=0.9,en-IE;q=0.8,en-US;q=0.7",
}


def get_data(
    display_start, display_length, date_from, date_to, session, echo=1
):
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
    logger.info(
        "getting request %s- %s", display_start + 1, display_start + page_size
    )
    try:
        response = session.get(f"{RIP_HOST}/deathnotices.php", params=params)
        data = response.json()

    except Exception as e:
        logger.exception("failed to get data %s", e)
        return []

    deaths = data["aaData"]
    # logger.info("retrieved page number %s", data["isarchive"])

    return [
        {
            "surname": x[0],
            "town": x[1],
            "county": x[2],
            "published": x[3],
            "death_data": x[4],
            "id": x[5],
            "link": f"{RIP_HOST}/showdn.php?dn=x{x[5]}",
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


def process_data(date_range):
    from_date, to_date = date_range
    session = Session()
    session.headers = headers

    logger.info("getting data from %s to %s", from_date, to_date)
    display_start = 0
    display_length = 40
    echo = 1
    pages_remaining = True
    deaths = []
    while pages_remaining:
        _deaths, total_records = get_data(
            display_start,
            display_length,
            from_date,
            to_date,
            session,
            echo=echo,
        )
        echo += 1
        deaths.extend(_deaths)
        display_start = display_start + display_length
        pages_remaining = total_records > display_start
    logger.info(
        "Complete with %s deaths %s to %s", len(deaths), from_date, to_date
    )
    return deaths


def get_irl_data(
    _from_date: dt.datetime,
    _to_date: dt.datetime = dt.datetime.now().strftime("%Y-%m-%d"),
):
    delta = _to_date - _from_date

    date_ranges = [
        (_to_date - dt.timedelta(days=x + 1), _to_date - dt.timedelta(days=x))
        for x in reversed(range(delta.days))
    ]
    # It is quicker to get daily deaths using multiprocessing
    # multiprocessing, is bound by the number of cpu cores.
    with Pool(cpu_count()) as p:
        data = p.map(process_data, date_ranges)

    if data:
        df = pd.DataFrame(list(itertools.chain(*data)))
        # df.drop_duplicates(subset='id', keep="last", inplace=True)
        df.to_csv("../data/deaths.csv", index=False, header=True)


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
    get_irl_data(args.from_date, args.to_date)
