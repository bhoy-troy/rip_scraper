import argparse
import datetime as dt
import itertools
import logging
import math
import time
from functools import partial
from multiprocessing import Pool, cpu_count

import bs4
import pandas as pd
from dateutil import parser as date_parser
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

HOST = "https://funeral-notices.co.uk"
PAGINATION_SIZE = 15
from_date = None
to_date = None


def get_count(soup: bs4.BeautifulSoup) -> int:

    listings = soup.find("div", {"class": "listings_result_container_right"})
    search_results_filter_container = listings.find(
        "div", {"class": "search_results_filter_container"}
    )
    search_results_filter = search_results_filter_container.find(
        "div", {"class": "search_results_filter"}
    )
    search_filter_item = search_results_filter.find(
        "a", {"class": "search_filter_item"}
    )
    count = search_filter_item.find("div", {"class": "result_count"})
    return int(count.string.replace(",", ""))


def get_name(element):
    name = element.find("div", {"class": "search_item_inner_fullname"})
    try:
        first_name = element.find("span", {"class": "firstname"}).string
    except AttributeError as e:
        first_name = ""
    try:
        last_name = element.find("span", {"class": "surname"}).string
    except AttributeError as e:
        last_name = ""

    return first_name, last_name


def get_location(soup):
    notice_name_details = soup.find("div", {"class": "notice_name_details"})
    h2 = notice_name_details.find("h2")
    return h2.text.split(",")[0]


def _get_death_deatails(element, session):

    try:
        resource = element["onclick"].split("'")[1]
        url = f"{HOST}{resource}"
        response = session.get(url)
        soup = bs4.BeautifulSoup(response.content, "html.parser")
        notice = soup.find("div", {"class": "notice_item_info_container block_item"})
        notice.find_all("span")[-1]
        tod = notice.find_all("span")[-1].string
        tod = date_parser.parse(tod)
        details = {
            "tine_of_death": tod.strftime("%d-%m-%Y"),
            "location": get_location(soup),
        }

    except Exception as e:
        details = {}
    return details


def get_death_deatails(element, session):
    details = _get_death_deatails(element, session)
    first_name, last_name = get_name(element)
    details["first_name"] = first_name
    details["last_name"] = last_name
    return details


def headers():
    return {
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "Accept": "text/html, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Language": "en-GB,en;q=0.9,en-IE;q=0.8,en-US;q=0.7",
    }


def get_data(page_number=None, from_date=None, to_date=None):
    # global from_date
    # global to_date
    ## keyword_search=&search_from_date=01/01/2021&search_to_date=10/01/2021
    params = {
        "keyword_search": "",
        "search_from_date": from_date.strftime("%d/%m/%Y"),
        "search_to_date": to_date.strftime("%d/%m/%Y"),
    }
    if page_number is not None:
        params["page"] = page_number
        params["pagination"] = "true"

    session = Session()
    response = session.get(
        f"{HOST}/national/death-notices",
        headers=headers(),
        params=params,
    )
    return response.content


def get_paginated_data(page, from_date, to_date):
    session = Session()
    # print(page, from_date, to_date)
    html = get_data(page, from_date, to_date)

    soup = bs4.BeautifulSoup(html, "html.parser")
    listings = soup.find("div", {"class": "listings_result_container_left"})
    search_results_container = listings.find(
        "div", {"class": "search_results_container"}
    )
    search_result_items = search_results_container.find_all(
        "div", {"class": "search_result_item"}
    )
    return [get_death_deatails(el, session) for el in search_result_items]


def get_initial_data(from_date=None, to_date=None):
    session = Session()
    html = get_data(page_number=None, from_date=from_date, to_date=to_date)
    soup = bs4.BeautifulSoup(html, "html.parser")
    listings = soup.find("div", {"class": "listings_result_container_left"})
    search_results_container = listings.find(
        "div", {"class": "search_results_container"}
    )
    search_result_items = search_results_container.find_all(
        "div", {"class": "search_result_item"}
    )
    return [get_death_deatails(el, session) for el in search_result_items], get_count(
        soup
    )


def pool_runner(_from_date, _to_date, page):
    global from_date
    global to_date
    from_date, to_date = _from_date, _to_date
    return get_paginated_data(page)


def get_deaths(_from_date, _to_date=dt.datetime.now().strftime("%Y-%m-%d")):
    global from_date
    global to_date
    from_date, to_date = _from_date, _to_date
    listings, death_count = get_initial_data(from_date=from_date, to_date=to_date)

    page_count = math.ceil(death_count / PAGINATION_SIZE)
    pages = [x for x in range(2, page_count + 1)]

    # import pdb
    #
    # pdb.set_trace()
    # get_paginated_data(3)

    with Pool(cpu_count()) as pool:
        # data = p.map(get_paginated_data, pages)
        import pdb

        pdb.set_trace()
        import sys

        sys.setrecursionlimit(25000)
        data = pool.map(
            partial(get_paginated_data, from_date=from_date, to_date=to_date), pages
        )

    import pdb

    pdb.set_trace()
    data.append(listings)
    if data:
        df = pd.DataFrame(list(itertools.chain(*data)))
        # df.drop_duplicates(subset='id', keep="last", inplace=True)
        df.to_csv("/data/uk_deaths.csv", index=False, header=True)


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

    get_deaths(args.from_date, args.to_date)
