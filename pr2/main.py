"""Консольный интерфейс сервиса."""
from datetime import date
from pathlib import Path
import json

from service import (add_user, dismiss, recommend,
                     search_events, statistics)
from storage import load_data, save_data


def main() -> None:
    folder = Path(__file__).resolve().parent
    path = folder / 'data.json'
    try:
        data = load_data(path if path.exists() else folder / 'seed.json')
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('Не удалось загрузить данные:', error)
        return
    while True:
        print('\n1 Каталог | 2 Поиск | 3 Добавить пользователя')
        print('4 Подобрать | 5 Отклонить рекомендацию | 6 Статистика')
        print('7 Интересы и пользователи | 0 Выход')
        try:
            choice = input('Команда: ').strip()
            if choice == '0':
                return
            if choice in ('1', '2'):
                query = input('Название: ') if choice == '2' else ''
                for event in search_events(data['events'], query):
                    print(event)
            elif choice == '3':
                print('Интересы:', data['interests'])
                name = input('Имя: ')
                age = int(input('Возраст: '))
                budget = float(input('Бюджет: '))
                interests = [int(s) for s in input(
                    'Номера интересов через пробел: ').split()]
                print(add_user(data, name, age, budget, interests))
                save_data(path, data)
            elif choice == '4':
                user_id = int(input('Номер пользователя: '))
                records = recommend(data, user_id, date.today())
                if not records:
                    print('Подходящих мероприятий нет')
                for record in records:
                    print(record)
                save_data(path, data)
            elif choice == '5':
                item_id = int(input('Номер рекомендации: '))
                dismiss(data, item_id)
                save_data(path, data)
                print('Рекомендация отклонена')
            elif choice == '6':
                print(statistics(data))
            elif choice == '7':
                print('Интересы:', data['interests'])
                for user in data['users']:
                    print(user)
            else:
                print('Введите номер команды из меню')
        except (ValueError, KeyError, TypeError, OSError,
                json.JSONDecodeError) as error:
            print('Ошибка:', error)
        except (EOFError, KeyboardInterrupt):
            print('\nРабота завершена')
            return


if __name__ == '__main__':
    main()
