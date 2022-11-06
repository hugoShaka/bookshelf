"""Bookshelf register.

Usage:
  register.py <isbn> [--dry-run]
  register.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --dry-run      Moored (anchored) mine.
"""


import requests
from typing import List
from attrs import define
from pathlib import Path
import jinja2
from docopt import docopt

OPENLIBRARY_URL = "https://openlibrary.org"
BOOK_TEMPLATE = Path("./book.rst.j2")

@define
class Author:
    name: str

    def __init__(self, key):
        response = requests.get(f"{OPENLIBRARY_URL}{key}.json")
        if response.status_code != 200:
            raise Exception("Book not found")
        openlib_author = response.json()
        self.name = openlib_author.get("name")


@define
class Book:
    publishers: List[str]
    title: str
    subtitle: str
    isbn_10: List[str]
    isbn_13: List[str]
    publish_date: str
    covers: List[int]
    authors: List[Author]

    def __init__(self, isbn: int):
        response = requests.get(f"{OPENLIBRARY_URL}/isbn/{isbn}.json")
        if response.status_code != 200:
            raise Exception("Book not found")
        openlib_book = response.json()

        self.authors = []
        authors = openlib_book.get("authors")
        for author in authors:
            self.authors.append(Author(author["key"]))

        self.isbn_10 = openlib_book.get("isbn_10")
        self.isbn_13 = openlib_book.get("isbn_13")
        self.title = openlib_book.get("title")
        self.subtitle = openlib_book.get("subtitle")
        self.covers = openlib_book.get("covers")
        self.publishers = openlib_book.get("publishers")
        self.publish_date = openlib_book.get("publish_date")

    def render(self):

        template = jinja2.Template(BOOK_TEMPLATE.read_text())
        return template.render(book=self)
        



if __name__ == '__main__':
    arguments = docopt(__doc__, version='register 0.1.0')
    book = Book(arguments["<isbn>"])
    print(book)
    if arguments["--dry-run"]:
        print(book.render())
    else:
        book_rst = Path("./source/books/", f'{arguments["<isbn>"]}.rst')
        book_rst.write_text(book.render())
    print("Book added")


