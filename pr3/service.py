"""Операции над коллекциями объектов."""
from datetime import date
from typing import Union
from models import Event, Interest, Recommendation, User


def find_by_id(items: list, item_id: int) -> Union[
        Event, Interest, Recommendation, User]:
    for item in items:
        if item.id == item_id:
            return item
    raise ValueError('Объект с таким номером не найден')


def next_id(items: list) -> int:
    return max((item.id for item in items), default=0) + 1


def add_user(data: dict, name: str, age: int, budget: float,
             interest_ids: list) -> User:
    interests = [find_by_id(data['interests'], i)
                 for i in sorted(set(interest_ids))]
    user = User(next_id(data['users']), name, age, budget, interests)
    data['users'].append(user)
    return user


def search_events(events: list, query: str = '') -> list:
    found = [event for event in events
             if query.casefold() in event.name.casefold()]
    return sorted(found, key=lambda event: (event.date, event.id))


def recommend(data: dict, user_id: int, today: date) -> list:
    user = find_by_id(data['users'], user_id)
    candidates = [e for e in data['events'] if e.is_suitable(user, today)]
    candidates.sort(key=lambda e: (-e.score_for(user), e.price))
    start_id = next_id(data['recommendations'])
    data['recommendations'] = [r for r in data['recommendations']
                               if r.user.id != user_id]
    result = []
    for event in candidates:
        record = Recommendation(start_id, user, event, event.score_for(user))
        result.append(record)
        data['recommendations'].append(record)
        start_id += 1
    return result


def dismiss(data: dict, recommendation_id: int) -> None:
    find_by_id(data['recommendations'], recommendation_id).dismiss()


def statistics(data: dict) -> dict:
    return {'Пользователей': len(data['users']),
            'Мероприятий': len(data['events']),
            'Новых рекомендаций': sum(r.status == 'new'
                                      for r in data['recommendations'])}
