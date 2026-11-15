import argparse
import json
import sqlite3
from pathlib import Path

from .database import DATABASE, ROOT, SQL, connect

SOURCE = ROOT / "pr3" / "seed.json"


def import_json(source, destination):
    data = json.loads(source.read_text(encoding="utf-8"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb"):
        pass
    try:
        with connect(destination, create=True) as connection:
            connection.executescript((SQL / "schema.sql").read_text(encoding="utf-8"))
            connection.executemany("INSERT INTO interests VALUES (:id, :name)",
                                   data["interests"])
            connection.executemany(
                "INSERT INTO visitors VALUES (:id, :name, :age, :budget)", data["users"],
            )
            connection.executemany(
                "INSERT INTO events VALUES (:id, :name, :date, :price, :min_age, :active)",
                data["events"],
            )
            connection.executemany(
                "INSERT INTO visitor_interests VALUES (?, ?)",
                [(item["id"], interest) for item in data["users"]
                 for interest in item["interest_ids"]],
            )
            connection.executemany(
                "INSERT INTO event_interests VALUES (?, ?)",
                [(item["id"], interest) for item in data["events"]
                 for interest in item["interest_ids"]],
            )
            connection.executemany(
                """INSERT INTO recommendations
                VALUES (:id, :user_id, :event_id, :score, :status)""",
                data["recommendations"],
            )
    except (KeyError, TypeError, sqlite3.Error, OSError):
        destination.unlink(missing_ok=True)
        raise
    return {name: len(data[name]) for name in ("interests", "users", "events", "recommendations")}


def main():
    parser = argparse.ArgumentParser(description="Перенос JSON ПР3 в SQLite ПР7")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--database", type=Path, default=DATABASE)
    args = parser.parse_args()
    try:
        counts = import_json(args.source, args.database)
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
        parser.exit(1, f"Импорт не выполнен: {exc}\n")
    print(f"{args.database}: {counts}")


if __name__ == "__main__":
    main()
