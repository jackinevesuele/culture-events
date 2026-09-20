"""Чтение и запись данных приложения."""
import json
from pathlib import Path


def load_data(path: Path) -> dict:
    with path.open(encoding='utf-8') as source:
        data = json.load(source)
    required = ('users', 'interests', 'events', 'recommendations')
    if not isinstance(data, dict) or any(
            not isinstance(data.get(key), list) for key in required):
        raise ValueError('Неверная структура файла данных')
    return data


def save_data(path: Path, data: dict) -> None:
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', encoding='utf-8') as target:
        json.dump(data, target, ensure_ascii=False, indent=2)
    temporary.replace(path)
