# Определитель средних зарплат по языкам программирования (ЯП) на основании данных вакансий от HeadHunter и SuperJob.

## Установка

- Скачайте код.
- Установите актуальную версию poetry в `UNIX`-подобных дистрибутивах с помощью команды:
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
```
или в `Windows Powershell`:
```
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```
- Добавьте к переменной окружения `$PATH` команду poetry:
```
source $HOME/.poetry/bin
```
- Установите виртуальное окружение в директории с проектом командой:
```
poetry config virtualenvs.in-project true
```
- Установите все зависимости (для установки без dev зависимостей можно добавить аргумент `--no-dev`):
```
poetry install
```
- Активируйте виртуальное окружение командой: 
```
source .venv/bin/activate
```

## Настройка переменных окружения

- Cоздайте файл `.env` в директории проекта, на основе файла `.env.example` командой 
(при необходимости скорректируйте значения переменных окружения):
```
cp .env.example .env
```
<details>
  <summary>Переменные окружения</summary>
  <pre>
    SUPERJOB_API_KEY=
    PROGRAMING_LANGUAGES=Python,Golang,NodeJS,Java,Rust,C,C++,C#,PHP,Ruby,Scala
    TIMEOUT=10
    RETRY_COUNT=5
    STATUS_FORCE_LIST=429,500,502,503,504
    ALLOWED_METHODS=HEAD,GET,OPTIONS
  </pre>
</details>

*** Для работы c агрегатором `SuperJob` необходимо сначала зарегистрировать приложение и заполнить переменную окружения `SUPERJOB_API_KEY` активным api ключом. Подробности на официальном сайте [SuperJob](https://api.superjob.ru/).***

## Запуск линтеров

```
isort . && flake8 . && mypy .
```
## Запуск 
- Для запуска определителя средних зарплат по языкам программирования вводим команду:
```
 python main.py
```
- Пример вывода:
```
┌HeadHunter Москва──────┬──────────────────┬─────────────────────┬──────────────────┐
│ Язык программирования │ Вакансий найдено │ Вакансий обработано │ Средняя зарплата │
├───────────────────────┼──────────────────┼─────────────────────┼──────────────────┤
│ Golang                │             2000 │                 813 │           159001 │
│ Python                │             2000 │                 507 │           177372 │
│ Java                  │             2000 │                 426 │           192844 │
│ Scala                 │             1585 │                 436 │           200866 │
│ C#                    │             2000 │                 509 │           169302 │
│ PHP                   │             2000 │                 902 │           153636 │
│ C++                   │             2000 │                 538 │           165807 │
│ C                     │             2000 │                1128 │           110945 │
│ Ruby                  │              409 │                 124 │           196268 |
│ Rust                  |             2000 |                 155 |           232050 |
| NodeJS                |             1700 |                 140 |           178120 |
└───────────────────────┴──────────────────┴─────────────────────┴──────────────────┘
┌SuperJob Москва────────┬──────────────────┬─────────────────────┬──────────────────┐
│ Язык программирования │ Вакансий найдено │ Вакансий обработано │ Средняя зарплата │
├───────────────────────┼──────────────────┼─────────────────────┼──────────────────┤
│ Golang                │              137 │                  84 │           128245 │
│ Python                │              128 │                  69 │           126298 │
│ Java                  │               98 │                  47 │           159608 │
│ Scala                 │               26 │                  17 │           173941 │
│ C#                    │               49 │                  25 │           148661 │
│ PHP                   │               87 │                  57 │           138761 │
│ C++                   │               70 │                  49 │           135600 │
│ C                     │              500 │                 470 │            74012 │
│ Ruby                  │                5 │                   4 │           166500 |
│ Rust                  |               98 |                  25 |           189050 |
| NodeJS                |               55 |                  23 |           155120 |
└───────────────────────┴──────────────────┴─────────────────────┴──────────────────┘
```
## Цели проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](https://dvmn.org).
