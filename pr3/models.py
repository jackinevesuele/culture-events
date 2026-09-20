"""Сущности сервиса культурных мероприятий."""
from datetime import date
import math


class Interest:
    def __init__(self, item_id: int, name: str):
        self.id = item_id
        self.name = name

    def __str__(self) -> str:
        return f'{self.id}: {self.name}'

    def to_dict(self) -> dict:
        return {'id': self.id, 'name': self.name}


class User:
    def __init__(self, item_id: int, name: str, age: int,
                 budget: float, interests: list):
        if not name.strip() or not 0 <= age <= 120:
            raise ValueError('Проверьте имя и возраст (0–120)')
        if not math.isfinite(budget) or budget < 0:
            raise ValueError('Бюджет должен быть неотрицательным числом')
        self.id = item_id
        self.name = name.strip()
        self.age = age
        self.budget = budget
        self.interests = interests

    def __str__(self) -> str:
        names = ', '.join(interest.name for interest in self.interests)
        return f'{self.id}: {self.name}, бюджет {self.budget}, {names}'

    def to_dict(self) -> dict:
        return {'id': self.id, 'name': self.name, 'age': self.age,
                'budget': self.budget,
                'interest_ids': [i.id for i in self.interests]}


class Event:
    def __init__(self, item_id: int, name: str, event_date: date,
                 price: float, min_age: int, interests: list,
                 active: bool = True):
        if not name.strip() or not math.isfinite(price) or price < 0:
            raise ValueError('Проверьте название и цену мероприятия')
        if not 0 <= min_age <= 120:
            raise ValueError('Некорректное возрастное ограничение')
        self.id = item_id
        self.name = name
        self.date = event_date
        self.price = price
        self.min_age = min_age
        self.interests = interests
        self.active = active

    def __str__(self) -> str:
        return (f'{self.id}: {self.name}, {self.date}, '
                f'{self.price} руб., {self.min_age}+')

    def score_for(self, user: User) -> int:
        return len({i.id for i in self.interests}
                   & {i.id for i in user.interests})

    def is_suitable(self, user: User, today: date) -> bool:
        return (self.active and self.date >= today
                and self.min_age <= user.age
                and self.price <= user.budget and self.score_for(user) > 0)

    def to_dict(self) -> dict:
        return {'id': self.id, 'name': self.name,
                'date': self.date.isoformat(), 'price': self.price,
                'min_age': self.min_age, 'active': self.active,
                'interest_ids': [i.id for i in self.interests]}


class Recommendation:
    def __init__(self, item_id: int, user: User, event: Event,
                 score: int, status: str = 'new'):
        if status not in ('new', 'dismissed'):
            raise ValueError('Неизвестный статус рекомендации')
        self.id = item_id
        self.user = user
        self.event = event
        self.score = score
        self._status = status

    @property
    def status(self) -> str:
        return self._status

    def dismiss(self) -> None:
        self._status = 'dismissed'

    def __str__(self) -> str:
        return (f'{self.id}: {self.user.name} — {self.event.name}; '
                f'совпадений {self.score}; {self.status}')

    def to_dict(self) -> dict:
        return {'id': self.id, 'user_id': self.user.id,
                'event_id': self.event.id, 'score': self.score,
                'status': self.status}
