import logging
import requests
from typing import List, Optional
from attrs import define
from pathlib import Path
import jinja2

OPENLIBRARY_URL = "https://openlibrary.org"
BOOK_TEMPLATE = Path("./book.rst.j2")

@define
class Author:
    name: str

    @classmethod
    def from_key(cls, key):
        response = requests.get(f"{OPENLIBRARY_URL}{key}.json")
        if response.status_code != 200:
            raise Exception("Book not found")
        openlib_author = response.json()
        logging.debug("GET author answer: %s", openlib_author)
        return cls(openlib_author.get("name"))


@define
class Book:
    publishers: List[str]
    title: str
    subtitle: Optional[str]
    isbn_10: Optional[List[str]]
    isbn_13: Optional[List[str]]
    publish_date: str
    covers: Optional[List[int]]
    authors: List[Author]

    @classmethod
    def from_isbn(cls, isbn: int):
        response = requests.get(f"{OPENLIBRARY_URL}/isbn/{isbn}.json")
        if response.status_code != 200:
            raise Exception("Book not found")
        openlib_book = response.json()
        logging.debug("GET isbn answer: %s", openlib_book)

        authors = []
        authors_ref = openlib_book.get("authors", [])
        for author in authors_ref:
            authors.append(Author.from_key(author["key"]))

        isbn_10 = openlib_book.get("isbn_10")
        isbn_13 = openlib_book.get("isbn_13")
        title = openlib_book.get("title")
        subtitle = openlib_book.get("subtitle")
        covers = openlib_book.get("covers")
        publishers = openlib_book.get("publishers")
        publish_date = openlib_book.get("publish_date")

        if openlib_book["works"] and not authors:
            authors, covers = get_work(openlib_book["works"][0]["key"])

        return cls(
                publishers,
                title,
                subtitle,
                isbn_10,
                isbn_13,
                publish_date,
                covers,
                authors,
                )

    def render(self):

        template = jinja2.Template(BOOK_TEMPLATE.read_text())
        return template.render(book=self)

def get_work(key: str):
    response = requests.get(f"{OPENLIBRARY_URL}/{key}.json")
    if response.status_code != 200:
        raise Exception("Work not found")
    openlib_work = response.json()
    logging.debug("GET work answer: %s", openlib_work)

    covers = openlib_work.get("covers")

    authors = []
    authors_ref = openlib_work.get("authors", [])

    for author in authors_ref:
        if key_type(author) == '/type/author_role':
            authors.append(Author.from_key(author["author"]["key"]))

    return authors, covers

def key_type(ref):
    if not ref["type"]:
        return None
    elif type(ref["type"]) is str:
        return ref["type"]
    elif type(ref["type"]) is dict:
        return ref["type"]["key"]
    return None
