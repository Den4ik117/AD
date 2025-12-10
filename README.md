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
4. [Ссылка на четвёртую лабораторную работу](https://docs.google.com/document/d/15FRfiUYdONo2iLJPyB7hiq7Hmc_yTFR37AYn9WzB61Y/edit?usp=sharing)
5. [Ссылка на пятую лабораторную работу](https://docs.google.com/document/d/1pLNgx7PPAwTO5Ul7wJ3QHNGokp7VCOk1nXbL3cIabX4/edit?usp=sharing)
6. [Ссылка на шестую лабораторную работу](https://docs.google.com/document/d/1N7mADRd65VUpP0xNYjcJcleseNyprJZixjqY6qKzl24/edit?usp=sharing)
7. [Ссылка на седьмую лабораторную работу](https://docs.google.com/document/d/1o55TEAYlXIn4Z6zaCQFFrFNxoSs2UsWKqUZxBCl2SeY/edit?usp=sharing)
7. [Ссылка на восьмую лабораторную работу](https://docs.google.com/document/d/1oiNIAF_8Lu_zlf777gAiBebAYTCgzhaZtdegmEASJiw/edit?usp=sharing)

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

## Запуск проекта для задания с RabbitMQ

1. Установить зависимости: `pip install -r requirements.txt`
2. Запустить контейнеры: `docker compose up -d`
3. Запустить реализацию `python -m app.rabbit_app`
4. Опубликовать несколько сообщений: `python producer.py`

## Проверка отчётов и планировщика

1. Поднять инфраструктуру: `docker compose up -d` 
2. Установить зависимости и применить миграции: `pip install -r requirements.txt` и `alembic upgrade head`
3. Запустить обработчик очередей (создаёт товары и заказы из очереди): `python -m app.rabbit_app`
4. Опубликовать тестовые данные: `python producer.py` (создаст товары/заказы с сегодняшней датой)
5. Запустить TaskIQ worker для брокера: `taskiq worker app.scheduler:broker`
6. В отдельном терминале запустить планировщик: `taskiq scheduler app.scheduler:scheduler --skip-first-run`
7. Получить отчёт за нужный день: `curl "http://127.0.0.1:8000/report?report_at=2025-12-10"` или выполнить запрос из блока `/report` в `api.http`.
