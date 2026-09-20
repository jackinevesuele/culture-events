from datetime import date
from pathlib import Path
import pytest

from service import (add_user, dismiss, recommend,
                     search_events)
from storage import load_data, save_data


@pytest.fixture
def data():
    return load_data(Path(__file__).parents[1] / 'seed.json')


def test_search_case_insensitive(data):
    assert len(search_events(data['events'], 'ДЖАЗ')) == 1


def test_budget_boundary(data):
    user = data['users'][0]
    event = data['events'][0]
    user.budget = 1200
    assert event.is_suitable(user, date(2026, 9, 21))
    user.budget = 1199
    assert not event.is_suitable(user, date(2026, 9, 21))


def test_age_date_and_active(data):
    event, user = data['events'][0], data['users'][0]
    user.age = 15
    assert not event.is_suitable(user, date(2026, 9, 21))
    user.age = 20
    assert not event.is_suitable(user, date(2027, 1, 1))
    event.active = False
    assert not event.is_suitable(user, date(2026, 9, 21))


def test_empty_interests(data):
    data['users'][0].interests = []
    assert recommend(data, 1, date(2026, 9, 21)) == []


def test_invalid_user(data):
    with pytest.raises(ValueError):
        add_user(data, 'Иван', -1, 100, [1])
    with pytest.raises(ValueError):
        add_user(data, 'Иван', 20, float('nan'), [1])
    with pytest.raises(ValueError):
        add_user(data, 'Иван', 20, 100, [999])


def test_recommendation_order_and_regeneration(data):
    result = recommend(data, 1, date(2026, 9, 21))
    assert [r.event.id for r in result] == [4, 2, 1]
    recommend(data, 1, date(2026, 9, 21))
    assert len(data['recommendations']) == 3


def test_user_recommendation_save_load(data, tmp_path):
    user = add_user(data, 'Анна', 20, 500, [2])
    result = recommend(data, user.id, date(2026, 9, 21))
    assert len(result) == 1
    path = tmp_path / 'data.json'
    save_data(path, data)
    loaded = load_data(path)
    assert loaded['recommendations'][0].event.name == result[0].event.name
    assert loaded['recommendations'][0].user is loaded['users'][-1]


def test_dismiss_persists(data, tmp_path):
    result = recommend(data, 1, date(2026, 9, 21))
    dismiss(data, result[0].id)
    path = tmp_path / 'data.json'
    save_data(path, data)
    assert load_data(path)['recommendations'][0].status == 'dismissed'


def test_corrupt_file(tmp_path):
    path = tmp_path / 'bad.json'
    path.write_text('{bad', encoding='utf-8')
    with pytest.raises(ValueError):
        load_data(path)
