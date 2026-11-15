import sqlite3
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "culture.sqlite"
SQL = ROOT / "sql"


@contextmanager
def connect(path=DATABASE, *, create=False):
    if not create and not path.is_file():
        raise FileNotFoundError("Создайте базу ПР7: python -m db.import_json")
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.create_function("CASEFOLD", 1, str.casefold, deterministic=True)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def query_library():
    statements = (SQL / "queries.sql").read_text(encoding="utf-8")
    return dict(part.strip().split(maxsplit=1)
                for part in statements.split("-- name: ")[1:])
