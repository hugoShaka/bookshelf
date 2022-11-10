"""Bookshelf manager.

Usage:
  bookshelf.py [--fetch] [--render] [--debug]
  bookshelf.py --version

Options:
  -h --help     Show this screen.
  --fetch       Fetch metadata on openlibrary.
  --render      Render the RST files.
  --debug       Enable debug logs.
  --version     Show version.
  --dry-run      Moored (anchored) mine.
"""

import logging
import json
import docopt
import gspread
import cattrs
from pathlib import Path
from openlibrary import Book, Author

def fetch_metadata():
    gc = gspread.service_account()
    sh = gc.open("Bookshelf")
    ws = sh.get_worksheet(0)
    entries = ws.get_all_records()
    
    changes = []
    for row, entry in enumerate(entries):
        if entry["isbn"] and entry["synced"] not in ["TRUE", "ERROR"]:
            try:
                logging.info(f"Fetching data for ISBN {entry['isbn']}")
                book = Book.from_isbn(entry["isbn"])
                data = cattrs.unstructure(book)
                change = {"range": f"B{row+2}:C{row+2}", "values": [["TRUE", json.dumps(data)]]}
            except Exception as err:
                logging.warning(err)
                change = {"range": f"B{row+2}:C{row+2}", "values": [["ERROR", ""]]}
            changes.append(change)
    
    logging.info("Applying sheet changes")
    ws.batch_update(changes)

def render():
    gc = gspread.service_account()
    sh = gc.open("Bookshelf")
    ws = sh.get_worksheet(0)
    entries = ws.get_all_records()

    for entry in entries:
        if entry["data"]:
            logging.info(f"Rendering ISBN {entry['isbn']}")
            book = cattrs.structure(json.loads(entry["data"]), Book)
            book_path = Path("./source/books/", f'{entry["isbn"]}.rst')
            book_path.write_text(book.render())

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='bookshelf 0.1.0')
    logger = logging.getLogger()
    if arguments["--debug"]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if arguments["--fetch"]:
        fetch_metadata()
    if arguments["--render"]:
        render()
