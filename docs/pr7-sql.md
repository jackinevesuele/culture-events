# ПР7. SQLite и SQL

`python -m db.import_json` создаёт `data/culture.sqlite` из `pr3/seed.json`.
Для другого источника передайте `--source путь.json --database путь.sqlite`.

В `sql/schema.sql` описаны четыре сущности и две таблицы связей многие ко многим.
В `sql/queries.sql` приведены 11 именованных запросов. SQLite подключается через `db/database.py`; там же включена проверка внешних ключей и зарегистрирована функция CASEFOLD для поиска по кириллице.

Коммит ПР7 показывает работу веб-страниц с этими запросами. Для просмотра этой версии можно открыть её в отдельном Git worktree и запустить `python -m db.import_json`, затем `python manage.py runserver`. Текущая версия веб-приложения использует ORM.
