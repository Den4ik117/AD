# Разработка приложений

Репозиторий для курса «Разработка приложений».

## Данные

- **AD** — Application Development
- **ФИО:** Загвоздин Денис Сергеевич
- **Группа:** РИМ-150950

## Ссылки

1. [Ссылка на первую лабораторную работу](https://docs.google.com/document/d/1bVu7TfxUbWR_RSGt7TuVU-NhrscZtI-oZAgqkfGqTPI/edit?usp=sharing)
2. [Ссылка на вторую лабораторную работу](https://docs.google.com/document/d/1cU1Zea1AAHJnes7yII1ShEcCLRvkWjDBZoo704TQ8Ic/edit?usp=sharing)
3. [Ссылка на третью лабораторную работу](https://docs.google.com/document/d/1M0DBQrG4NEUtzN714a1_N_Rh_KVSZIhnR8QxQiCZdgg/edit?usp=sharing)

## Запуск и установка

1. Установить зависимости: `pip install -r requirements.txt`
2. Запустить PostgreSQL в контейнере: `docker compose up -d`
3. Применить миграции: `alembic upgrade head`
4. Запустить приложение командой `python -m app.main`

## Запуск тестов

- Запуск всех тестов: `pytest`
- Запуск только unit-тестов: `pytest tests/test_models/ tests/test_repositories/ tests/test_services/`
- Запуск только API-тестов: `pytest tests/test_routes/`
- Запуск тестов с покрытием кода: `pytest --cov=app --cov-report=html`
- Параллельный запуск тестов: `pytest -n auto`

## Форматирование и линтинг

1. Установите зависимости из `requirements.txt`, чтобы были доступны `black`, `isort`, `pylint` и `pre-commit`.
2. Выполните `pre-commit install`, чтобы включить проверки перед коммитами.
3. Локально прогоните всё сразу командой `pre-commit run --all-files`. Скрипт последовательно вызовет `black` и `isort` для каталогов `app` и `tests`, а затем `pylint` для боевого кода.

Все параметры форматеров и линтера заданы в `pyproject.toml` и `.pylintrc`. При необходимости обновите игнорируемые каталоги или список отключённых правил в соответствии с задачами.

## Сборка и запуск в Docker

1. Соберите образ приложения: `docker compose build web`.
2. Поднимите сервисы вместе с PostgreSQL: `docker compose up --build`.

