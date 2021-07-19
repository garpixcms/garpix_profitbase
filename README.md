# Garpix ProfitBase

Пакет интеграции с profitbase.ru

## Быстрый старт

Установка:

```bash
pip install garpix_profitbase
```

Добавьте `garpix_profitbase` в `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'garpix_profitbase',
]
```

Также, добавьте переменные окружения (файл `.env`) значениями, полученными от profitbase.ru:

```bash
PROFITBASE_API_KEY=app-?????????
PROFITBASE_CLIENT_NAME=???????
PROFITBASE_COMPANY_ID=????
ENABLE_GARPIX_AUTH=????
```

## Использование

Для получения данных от profitbase.ru используйте следующую manage.py команду:

```
python3 backend/manage.py profitbase_update
```

# Changelog

Смотри [CHANGELOG.md](CHANGELOG.md).

# Contributing

Смотри [CONTRIBUTING.md](CONTRIBUTING.md).

# License

[MIT](LICENSE)

---

Developed by Garpix / [https://garpix.com](https://garpix.com)