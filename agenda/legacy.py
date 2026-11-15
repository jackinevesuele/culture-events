import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parent.parent / "pr3" / "seed.json"


def catalogue():
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def enrich(data):
    tags = {item["id"]: item for item in data["interests"]}
    for event in data["events"]:
        event["interests"] = [tags[key] for key in event["interest_ids"]]
    return data
