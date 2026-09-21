from datetime import date
import math


def find_by_id(items: list, item_id: int) -> dict:
    for item in items:
        if item['id'] == item_id:
            return item
    raise ValueError('Объект с таким номером не найден')


def next_id(items: list) -> int:
    return max((item['id'] for item in items), default=0) + 1


def add_user(data: dict, name: str, age: int, budget: float,
             interest_ids: list) -> dict:
    if not name.strip() or not 0 <= age <= 120:
        raise ValueError('Проверьте имя и возраст (0–120)')
    if not math.isfinite(budget) or budget < 0:
        raise ValueError('Бюджет должен быть неотрицательным числом')
    for interest_id in interest_ids:
        find_by_id(data['interests'], interest_id)
    user = {'id': next_id(data['users']), 'name': name.strip(),
            'age': age, 'budget': budget,
            'interest_ids': sorted(set(interest_ids))}
    data['users'].append(user)
    return user


def search_events(events: list, query: str = '') -> list:
    found = [event for event in events
             if query.casefold() in event['name'].casefold()]
    return sorted(found, key=lambda event: (event['date'], event['id']))


def is_suitable(event: dict, user: dict, today: date) -> bool:
    return (event['active'] and date.fromisoformat(event['date']) >= today
            and event['min_age'] <= user['age']
            and event['price'] <= user['budget']
            and bool(set(event['interest_ids']) & set(user['interest_ids'])))


def recommend(data: dict, user_id: int, today: date) -> list:
    user = find_by_id(data['users'], user_id)
    candidates = []
    for event in data['events']:
        if is_suitable(event, user, today):
            score = len(set(event['interest_ids']) & set(user['interest_ids']))
            candidates.append((event, score))
    candidates.sort(key=lambda pair: (-pair[1], pair[0]['price']))
    existing = [r for r in data['recommendations'] if r['user_id'] == user_id]
    start_id = next_id(data['recommendations'])
    for record in existing:
        data['recommendations'].remove(record)
    result = []
    for event, score in candidates:
        record = {'id': start_id, 'user_id': user_id,
                  'event_id': event['id'], 'score': score, 'status': 'new'}
        data['recommendations'].append(record)
        result.append(record)
        start_id += 1
    return result


def dismiss(data: dict, recommendation_id: int) -> None:
    record = find_by_id(data['recommendations'], recommendation_id)
    record['status'] = 'dismissed'


def statistics(data: dict) -> dict:
    return {'Пользователей': len(data['users']),
            'Мероприятий': len(data['events']),
            'Новых рекомендаций': sum(r['status'] == 'new'
                                      for r in data['recommendations'])}
