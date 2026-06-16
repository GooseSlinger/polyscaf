# polyscaf

`polyscaf` - CLI для генерации стартового каркаса FastAPI-проекта.

## Что умеет

- создавать базовую структуру проекта;
- генерировать модели, схемы, роуты, сервисы, скрипты, тесты и заготовки;
- поднимать async-шаблон с автосозданием базы данных при старте.

## Установка

### Через `pipx`

```bash
brew install pipx
pipx ensurepath
pipx install .
```

Если `pipx` уже установлен, достаточно:

```bash
pipx install .
```

## Проверка

```bash
polyscaf --help
```

## Сборка

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

## Пример использования

Создание стартового проекта:

```bash
polyscaf make-project MyApp --mysql
```

Генерация отдельных частей:

```bash
polyscaf make-model User
polyscaf make-schema User
polyscaf make-route User
polyscaf make-service User
polyscaf make-service User --with mr
```

`make-service --with` понимает буквы:

- `m` -> model
- `s` -> schema
- `r` -> route

Порядок букв не важен, например `--with rm` и `--with mr` работают одинаково.

## Примечания

- Команда `make project` создаёт каркас, а не полностью готовое приложение.
- Роуты в `main.py` подключаются вручную по мере добавления модулей.
- Для работы проекта в зависимости от выбранной БД нужны доступы на создание базы.
