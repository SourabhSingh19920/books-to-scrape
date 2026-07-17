import math
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_soup(url: str):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_categories():
    soup = get_soup(BASE_URL)

    categories = []

    category_list = soup.select("div.side_categories ul li ul li a")

    for category in category_list:
        categories.append({
            "name": category.text.strip(),
            "url": urljoin(BASE_URL, category["href"])
        })

    return categories


def page_url(page: int):
    if page == 1:
        return BASE_URL

    return f"{BASE_URL}catalogue/page-{page}.html"


def parse_rating(classes):
    ratings = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    for cls in classes:
        if cls in ratings:
            return ratings[cls]

    return None


def get_books(page: int):

    soup = get_soup(page_url(page))

    books = []

    for item in soup.select("article.product_pod"):

        title = item.h3.a["title"]

        price = item.select_one(".price_color").text.strip()

        availability = item.select_one(".instock.availability").text.strip()

        image = urljoin(BASE_URL, item.img["src"])

        rating = parse_rating(item.select_one(".star-rating")["class"])

        detail = urljoin(
            BASE_URL + "catalogue/",
            item.h3.a["href"]
        )

        books.append({
            "title": title,
            "price": price,
            "availability": availability,
            "rating": rating,
            "image": image,
            "detail_url": detail
        })

    return books


def get_category_page_count(category_name: str):

    categories = get_categories()

    category = next(
        (
            c for c in categories
            if c["name"].lower() == category_name.lower()
        ),
        None,
    )

    if category is None:
        return None

    soup = get_soup(category["url"])

    current = soup.select_one("li.current")

    if current:
        # Example:
        # "Page 1 of 4"

        text = current.text.strip().split()

        return int(text[-1])

    # Only one page exists
    return 1

def get_books_by_category(category_name: str, page: int = 1):
    """
    Returns all books for a given category and page.
    """

    categories = get_categories()

    category = next(
        (
            c
            for c in categories
            if c["name"].lower() == category_name.lower()
        ),
        None,
    )

    if category is None:
        return None

    category_url = category["url"]

    # First page
    if page == 1:
        url = category_url
    else:
        url = category_url.replace(
            "index.html",
            f"page-{page}.html"
        )

    soup = get_soup(url)

    books = []

    for item in soup.select("article.product_pod"):

        title = item.h3.a["title"]

        price = item.select_one(".price_color").text.strip()

        availability = item.select_one(".instock.availability").text.strip()

        rating = parse_rating(
            item.select_one(".star-rating")["class"]
        )

        image = urljoin(BASE_URL, item.img["src"])

        detail_url = urljoin(
            BASE_URL + "catalogue/",
            item.h3.a["href"]
        )

        books.append(
            {
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating,
                "image": image,
                "detail_url": detail_url,
            }
        )

    return books