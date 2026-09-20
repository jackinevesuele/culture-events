"""Начальный сценарий подбора мероприятия."""
from datetime import date


def matches_interest(user_interest: str, event_interest: str) -> bool:
    return user_interest.strip().casefold() == event_interest.casefold()


def is_available(age: int, min_age: int, event_date: date,
                 today: date) -> bool:
    return age >= min_age and event_date >= today


def fits_budget(price: float, budget: float) -> bool:
    return 0 <= price <= budget


if __name__ == '__main__':
    name = 'Выставка городской фотографии'
    interest = 'Фотография'
    age = 20
    price = 400.0
    budget = float('600')
    event_date = date.today()
    suitable = (matches_interest('фотография', interest)
                and is_available(age, 12, event_date, date.today())
                and fits_budget(price, budget))
    print('Мероприятие:', name)
    print('Дата:', event_date)
    print('Цена:', price, 'руб.')
    print('Остаток бюджета:', budget - price, 'руб.')
    if suitable:
        print('Рекомендация: мероприятие подходит')
    else:
        print('Рекомендация: выберите другое мероприятие')
