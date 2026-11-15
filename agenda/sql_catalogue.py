from collections import defaultdict

from db.database import connect, query_library

QUERIES = query_library()


def interests():
    with connect() as connection:
        return list(connection.execute(QUERIES["events_per_interest"]))


def events(scenario, *params):
    with connect() as connection:
        rows = [dict(row) for row in connection.execute(QUERIES[scenario], params)]
        tags = defaultdict(list)
        for row in connection.execute(QUERIES["event_tags"]):
            tags[row["event_id"]].append(dict(row))
    for event in rows:
        event["tag_list"] = tags[event["id"]]
    return rows
