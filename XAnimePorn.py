"""
This module allows anyone to interact with the XAnimePorn.com website inside their own code.
NO AFFILIATION WITH X Anime Porn!

Author: Stefan Cucoranu <elpideus@gmail.com>
"""
import json
import re
import math
import unicodedata
from pathlib import Path
from urllib.request import urlopen
import certifi
import urllib3
from bs4 import BeautifulSoup, SoupStrainer
from typing import List
from tqdm import tqdm
from colorama import Fore

website_domain = "www.xanimeporn.com"


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


class Video:
    """
    This is used as a type. The methods inside this class automatically get data from the website and transforms them
    into a Video type value.

    Args:
        id (str): The id of the video on the website. It can also be a link.
    """

    def __init__(self, id: str):
        """
        Args:
            id (str):
                The id of the video on the website. It can also be a link
        """
        self.id = id
        if any(protocol in self.id for protocol in [
            "http://{domain}/".format(domain=website_domain), "http://{domain}/".format(domain=website_domain)]):
            self.url = id
        else:
            self.url = "http://{website_domain}/{id}/".format(website_domain=website_domain, id=id)
        self.page = urlopen(self.url).read()

    @property
    def title(self) -> str:
        """
        Returns:
            str: Full title of the video on the website.
        """
        return [tag for tag in BeautifulSoup(self.page, parse_only=SoupStrainer('span'), features="lxml")][1]

    @property
    def thumbnail(self):
        """
        Returns:
            str: Link to the thumbnail file on the website.
        """
        thumb = [tag for tag in BeautifulSoup(
            self.page, parse_only=SoupStrainer("img", {"class": "fp-splash"}), features="lxml")]
        return thumb[1].get("src")

    @property
    def file(self) -> str:
        """
        Returns:
            str: Link to the video file (download link).
        """
        flowplayer = [tag for tag in BeautifulSoup(
            self.page, parse_only=SoupStrainer("div", {"class": re.compile(r"\bflowplayer\b")}), features="lxml")]
        return json.loads(flowplayer[1].get("data-item"))["sources"][0]["src"]

    def download(self, location="downloads", debug_link=None) -> bool:
        """
        Downloads the video

        Args:
            location (str): Where to download the video.

        Returns:
            bool: True if download has finished successfully or False if an error occurred.
        """
        url = json.loads([tag for tag in BeautifulSoup(self.page, parse_only=SoupStrainer(
               'div', {"class": re.compile(r"\bflowplayer\b")}), features="lxml")][1]
                         .get("data-item"))["sources"][0]["src"]
        if debug_link is not None:
            url = debug_link
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where()
        )
        r = http.request('GET', url, preload_content=False)
        file_size = int(r.headers["Content-Length"])
        file_size_dl = 0
        block_sz = 8192
        if not Path(location).exists():
            Path(location).mkdir()
            print("There wasn't a directory named \"{location}\" available. One has been created successfully!"
                  .format(location=location))
        f = open("{location}/{name}.mp4".format(location=location, name=slugify(self.title)), "wb")
        progress_bar = tqdm(iterable=None, desc="Downloading", mininterval=1, total=file_size / 1000000, leave=False,
                            bar_format=
                            Fore.GREEN + "{desc} -> " +
                            Fore.RED + "{percentage:.0f}% " +
                            Fore.GREEN + "|" +
                            Fore.WHITE + "{bar}" +
                            Fore.GREEN + "| [{n:.02f}/{total:.02f}MB] -> ({remaining} remaining) File: " +
                            slugify(self.title) + ".mp4")
        status = 0
        while True:
            buffer = r.read(block_sz)
            if not buffer:
                break
            f.write(buffer)
            progress_bar.update(len(buffer) / 1000000)
            file_size_dl += len(buffer)
            status = int(file_size_dl * 100. // file_size)
            if status == 100:
                f.close()
                print(Fore.GREEN + "Done!")
                return True


def search(query=None, elements=None, pages=None, tag=None, order_by=None) -> List[str]:
    """
    This function searches the website using the options passed in the arguments and returns links to the found videos.

    Args:
        query (str | optional): Contains the words that get searched on the website. If this is used tag must be None.
        elements (int | str | optional): How many elements should be returned. It can be omitted but it's highly
        recommended to keep this value as low as possible since the maximum number of results per page is 24 and this
        means that every 24 results the script will send a request to the next page. This will require more time and
        there is the risk that the website detects this action as a DDOS attack attempt. Be careful!
        pages (int | str | optional): This can be used instead of elements. There is a little difference though. It's
        recommended to keep it low since loading a lot of pages requires more time and the website can datect this
        action as a DDOS attack attempt. Be careful!
        elements gets a precise number of results but pages gets a variable number of results depending on the page.
        tag (str | optional): It is possible to search the website by using tags. If this is used query must be None.
        order_by (str | optional): The order of the results. It can be views, duration (or duree), rate, random.

    Raises:
        ValueError: if query is not string or None, elements is not string, None or integer, pages is not integer, None
                    or string, tag is not string or None or order_by is not string or None.

    Returns:
        list[str]: A list containing the links to the various hentai videos outputted by the function.
    """
    if not isinstance(query, str) and query is not None:
        raise ValueError("The query must be a string.")
    elif not isinstance(elements, int) and not isinstance(elements, str) and elements is not None:
        raise ValueError("The elements number must be passed as integer or string.")
    elif not isinstance(pages, int) and not isinstance(pages, str) and pages is not None:
        raise ValueError("Pages can only be passed as integer or string.")
    elif not isinstance(tag, str) and tag is not None:
        raise ValueError("The tag can only be a string.")
    elif not isinstance(order_by, str) and order_by is not None:
        raise ValueError("Order can only be a string.")
    elements = (int(elements) if elements is not None else elements)
    pages = (int(pages) if pages is not None else pages)
    if order_by == "duration":
        order_by = "duree"
    results = []
    order = ""
    search = query.replace(" ", "+").lower()
    if order_by is not None:
        order = "{sign}filtre={order_by}".format(sign=("&" if query is not None and tag is None else "?"),
                                                 order_by=order_by)
    if query is not None and tag is None:
        query_document = urlopen("http://{domain}/?s={query}{order_by}"
                                 .format(domain=website_domain, query=search, order_by=order_by)).read()
    else:
        query_document = urlopen("http://{domain}/{tag}/{order_by}"
                                 .format(domain=website_domain, tag=search, order_by=order_by)).read()
    parsed_query_document = [tag for tag in BeautifulSoup(
        query_document, parse_only=SoupStrainer("li", {"class": re.compile(r"\bborder-radius-5\b")}), features="lxml")]
    del parsed_query_document[0]
    pagination = [tag for tag in BeautifulSoup(query_document, parse_only=SoupStrainer("div", {"class": "pagination"}),
                                               features="lxml")][1]
    scraped_pagination = (int(pagination.find_all("a", attrs={'class': None})[1].get("href").split("/")
                              [(4 if query is not None and tag is not None else 5)])
                          if len(pagination.find_all("a", attrs={'class': None})) > 0 else 1)
    if pages is None:
        pages = scraped_pagination
    elif pages > scraped_pagination:
        pages = scraped_pagination
    else:
        pages = math.ceil(elements / scraped_pagination)
    results_counter = 0
    loop_must_break = False
    for page in range(pages):
        page += 1
        if query is not None and tag is None:
            scraped_search_page = urlopen("http://{domain}/page/{page}/?s={query}{order_by}"
                                          .format(domain=website_domain, page=page, query=search,
                                                  order_by=order_by)).read()
        else:
            scraped_search_page = urlopen("http://{domain}/{tag}/page/{page}/{order_by}"
                                          .format(domain=website_domain, tag=search, page=page, order_by=order_by)
                                          ).read()
        parsed_search_page = [tag for tag in BeautifulSoup(
            scraped_search_page, parse_only=SoupStrainer("a", attrs={"title": re.compile(r".*")}), features="lxml")]
        del parsed_search_page[0]
        for link in parsed_search_page:
            if "episode" in link.get("href"):
                if results_counter < elements:
                    results.append(link.get("href"))
                    results_counter += 1
                else:
                    loop_must_break = True
        if loop_must_break:
            break
    return results


def most_viewed(elements=None, pages=None) -> List[str]:
    """
    Returns the most viewed videos of the website.

    Args:
        elements (int, str, optional): How many elements should be returned. It can be omitted but it's highly
        recommended to keep this value as low as possible since the maximum number of results per page is 24 and this
        means that every 24 results the script will send a request to the next page. This will require more time and
        there is the risk that the website detects this action as a DDOS attack attempt. Be careful!
        pages (int, str, optional): This can be used instead of elements. There is a little difference though. It's
        recommended to keep it low since loading a lot of pages requires more time and the website can datect this
        action as a DDOS attack attempt. Be careful!

    Returns:
        list[str]: List containing links to the most viewed hentai videos.

    Raises:
        ValueError: if elements or pages are not integer, None or string.
    """
    if not isinstance(elements, int) and not isinstance(elements, str) and elements is not None:
        raise ValueError("\"elements\" must be integer or string.")
    if not isinstance(pages, int) and not isinstance(pages, str) and pages is not None:
        raise ValueError("The number of pages must be passed as integer or string.")
    elements = (int(elements) if elements is not None else elements)
    pages = (int(pages) if pages is not None else pages)
    results = []
    mw_document = urlopen("http://{domain}/?filtre=views".format(domain=website_domain)).read()
    parsed_mw_document = [tag for tag in BeautifulSoup(
        mw_document, parse_only=SoupStrainer("li", {"class": re.compile(r"\bborder-radius-5\b")}),
        features="lxml")]
    del parsed_mw_document[0]
    pagination = [tag for tag in BeautifulSoup(
        mw_document, parse_only=SoupStrainer("div", {"class": "pagination"}),
        features="lxml")][1]
    scraped_pagination = (int(pagination.find_all("a", attrs={'class': None})[1].get("href").split("/")[4])
                          if len(pagination.find_all("a", attrs={'class': None})) > 0 else 1)
    if pages is None:
        pages = scraped_pagination
    if pages > scraped_pagination:
        pages = scraped_pagination
    else:
        pages = math.ceil(elements / scraped_pagination)
    results_counter = 0
    loop_must_break = False
    for page in range(pages):
        page += 1
        scraped_search_page = urlopen("http://www.xanimeporn.com/page/{page}/?filtre=views".format(page=page)).read()
        parsed_search_page = [tag for tag in BeautifulSoup(
            scraped_search_page, parse_only=SoupStrainer("a", attrs={"title": re.compile(r".*")}),
            features="lxml")]
        del parsed_search_page[0]
        for link in parsed_search_page:
            if "episode" in link.get("href"):
                if results_counter < elements:
                    results.append(link.get("href"))
                    results_counter += 1
                else:
                    loop_must_break = True
        if loop_must_break:
            break
    return results


def top_rated(elements=None, pages=None):
    """
    Returns the most liked videos of the website.

    Args:
        elements (int, str, optional): How many elements should be returned. It can be omitted but it's highly
        recommended to keep this value as low as possible since the maximum number of results per page is 24 and this
        means that every 24 results the script will send a request to the next page. This will require more time and
        there is the risk that the website detects this action as a DDOS attack attempt. Be careful!
        pages (int, str, optional): This can be used instead of elements. There is a little difference though. It's
        recommended to keep it low since loading a lot of pages requires more time and the website can datect this
        action as a DDOS attack attempt. Be careful!

    Returns:
        list[str]: List containing links to the most liked hentai videos.

    Raises:
        ValueError: if elements or pages are not integer, None or string.
    """
    if not isinstance(elements, int) and not isinstance(elements, str) and elements is not None:
        raise ValueError("\"elements\" must be integer or string.")
    if not isinstance(pages, int) and not isinstance(pages, str) and pages is not None:
        raise ValueError("The number of pages must be passed as integer or string.")
    elements = (int(elements) if elements is not None else elements)
    pages = (int(pages) if pages is not None else pages)
    results = []
    tr_document = urlopen("http://{domain}/?filtre=rate".format(domain=website_domain)).read()
    parsed_tr_document = [tag for tag in BeautifulSoup(
        tr_document, parse_only=SoupStrainer("li", {"class": re.compile(r"\bborder-radius-5\b")}),
        features="lxml")]
    del parsed_tr_document[0]
    pagination = [tag for tag in BeautifulSoup(
        tr_document, parse_only=SoupStrainer("div", {"class": "pagination"}),
        features="lxml")][1]
    scraped_pagination = (int(pagination.find_all("a", attrs={'class': None})[1].get("href").split("/")[4])
                          if len(pagination.find_all("a", attrs={'class': None})) > 0 else 1)
    if pages is None:
        pages = scraped_pagination
    if pages > scraped_pagination:
        pages = scraped_pagination
    else:
        pages = math.ceil(elements / scraped_pagination)
    results_counter = 0
    loop_must_break = False
    for page in range(pages):
        page += 1
        scraped_search_page = urlopen("http://www.xanimeporn.com/page/{page}/?filtre=rate".format(page=page)).read()
        parsed_search_page = [tag for tag in BeautifulSoup(
            scraped_search_page, parse_only=SoupStrainer("a", attrs={"title": re.compile(r".*")}),
            features="lxml")]
        del parsed_search_page[0]
        for link in parsed_search_page:
            if "episode" in link.get("href"):
                if results_counter < elements:
                    results.append(link.get("href"))
                    results_counter += 1
                else:
                    loop_must_break = True
        if loop_must_break:
            break
    return results


def random(elements=None, pages=None):
    """
    Returns random videos from the website.

    Args:
        elements (int, str, optional): How many elements should be returned. It can be omitted but it's highly
        recommended to keep this value as low as possible since the maximum number of results per page is 24 and this
        means that every 24 results the script will send a request to the next page. This will require more time and
        there is the risk that the website detects this action as a DDOS attack attempt. Be careful!
        pages (int, str, optional): This can be used instead of elements. There is a little difference though. It's
        recommended to keep it low since loading a lot of pages requires more time and the website can datect this
        action as a DDOS attack attempt. Be careful!

    Returns:
        list[str]: List containing links to random videos.

    Raises:
        ValueError: if elements or pages are not integer, None or string.
    """
    if not isinstance(elements, int) and not isinstance(elements, str) and elements is not None:
        raise ValueError("\"elements\" must be integer or string.")
    if not isinstance(pages, int) and not isinstance(pages, str) and pages is not None:
        raise ValueError("The number of pages must be passed as integer or string.")
    elements = (int(elements) if elements is not None else elements)
    pages = (int(pages) if pages is not None else pages)
    results = []
    random_document = urlopen("http://{domain}/?filtre=random".format(domain=website_domain)).read()
    parsed_random_document = [tag for tag in BeautifulSoup(
        random_document, parse_only=SoupStrainer("li", {"class": re.compile(r"\bborder-radius-5\b")}),
        features="lxml")]
    del parsed_random_document[0]
    pagination = [tag for tag in BeautifulSoup(
        random_document, parse_only=SoupStrainer("div", {"class": "pagination"}),
        features="lxml")][1]
    scraped_pagination = (int(pagination.find_all("a", attrs={'class': None})[1].get("href").split("/")[4])
                          if len(pagination.find_all("a", attrs={'class': None})) > 0 else 1)
    if pages is None:
        pages = scraped_pagination
    if pages > scraped_pagination:
        pages = scraped_pagination
    else:
        pages = math.ceil(elements / scraped_pagination)
    results_counter = 0
    loop_must_break = False
    for page in range(pages):
        page += 1
        scraped_search_page = urlopen("http://www.xanimeporn.com/page/{page}/?filtre=random".format(page=page)).read()
        parsed_search_page = [tag for tag in BeautifulSoup(
            scraped_search_page, parse_only=SoupStrainer("a", attrs={"title": re.compile(r".*")}),
            features="lxml")]
        del parsed_search_page[0]
        for link in parsed_search_page:
            if "episode" in link.get("href"):
                if results_counter < elements:
                    results.append(link.get("href"))
                    results_counter += 1
                else:
                    loop_must_break = True
        if loop_must_break:
            break
    return results
