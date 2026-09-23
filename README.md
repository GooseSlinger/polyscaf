# polyscaf

`polyscaf` - CLI для генерации стартового каркаса FastAPI-проекта.

## Что умеет

- создавать базовую структуру проекта;
- генерировать модели, схемы, роуты, сервисы, скрипты, тесты и заготовки;
- создавать компактный MySQL-каркас с async-сессиями.

## Установка

### Через `pipx`

Если `pipx` ещё не установлен:

```bash
brew install pipx
pipx ensurepath
```

Первичная установка из корня этого репозитория:

```bash
pipx install .
```

Если `pipx` уже установлен, можно сразу:

```bash
pipx install .
```

Если ты уже ставил `polyscaf` и хочешь подтянуть изменения из этой папки, используй:

```bash
pipx install --force .
```

После установки проверь:

```bash
polyscaf --help
polyscaf --version
```

## Проверка

```bash
python -m build
```

Если `build` не установлен:

```bash
python -m pip install build
```

## Переустановка

```bash
pipx uninstall polyscaf
pipx install --force .
```

Если нужно просто обновить локальную установленную версию после правок в этом репозитории, обычно достаточно второй команды.

## Пример использования

Создание стартового проекта:

```bash
polyscaf make-project MyApp
```

Генерация отдельных частей:

```bash
polyscaf make-model User
polyscaf make-schema User
polyscaf make-route User
polyscaf make-service User
polyscaf make-service User --with mr
polyscaf make-service User --with msr
```

`make-service --with` понимает буквы:

- `m` -> model
- `s` -> schema
- `r` -> route

Порядок букв не важен, например `--with rm` и `--with mr` работают одинаково.

## Примечания

- Команда `make-project` создаёт каркас в текущей директории. Флаг `--mysql` оставлен для совместимости.
- Имена для команд генерации должны быть допустимыми идентификаторами Python; пути и символы вроде дефиса не принимаются.
- Роуты в `main.py` подключаются вручную по мере добавления модулей.
- В `.env` задайте `SQL_BASE` как URL сервера MySQL без имени базы и `SQL_DATABASE` как имя целевой базы.
- Для явного создания базы запустите `python scripts/create_database_script.py` с учётными данными, имеющими право `CREATE DATABASE`. Импорт приложения базу не создаёт.
- `alembic` включён в зависимости. Если нужны миграции, самостоятельно выполните `alembic init alembic` и настройте подключение и модели; каркас не содержит конфигурации или начальной миграции.
