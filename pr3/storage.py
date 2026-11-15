from datetime import date
import json
from pathlib import Path
if __package__:
    from .models import Event, Interest, Recommendation, User
    from .service import find_by_id
else:
    from models import Event, Interest, Recommendation, User
    from service import find_by_id


def load_data(path: Path) -> dict:
    with path.open(encoding='utf-8') as source:
        raw = json.load(source)
    required = ('users', 'interests', 'events', 'recommendations')
    if not isinstance(raw, dict) or any(
            not isinstance(raw.get(key), list) for key in required):
        raise ValueError('Неверная структура файла данных')
    for key in required:
        ids = [record['id'] for record in raw[key]]
        if len(ids) != len(set(ids)):
            raise ValueError('Повторяющиеся идентификаторы: ' + key)
    interests = [Interest(r['id'], r['name']) for r in raw['interests']]
    users = [User(r['id'], r['name'], r['age'], r['budget'],
                  [find_by_id(interests, i) for i in r['interest_ids']])
             for r in raw['users']]
    events = [Event(r['id'], r['name'], date.fromisoformat(r['date']),
                    r['price'], r['min_age'],
                    [find_by_id(interests, i) for i in r['interest_ids']],
                    r['active']) for r in raw['events']]
    recommendations = [Recommendation(
        r['id'], find_by_id(users, r['user_id']),
        find_by_id(events, r['event_id']), r['score'], r['status'])
        for r in raw['recommendations']]
    return dict(interests=interests, users=users, events=events,
                recommendations=recommendations)


def save_data(path: Path, data: dict) -> None:
    raw = {key: [item.to_dict() for item in items]
           for key, items in data.items()}
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', encoding='utf-8') as target:
        json.dump(raw, target, ensure_ascii=False, indent=2)
    temporary.replace(path)
