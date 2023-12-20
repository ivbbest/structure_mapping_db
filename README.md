# Структура соответствий и зависимостей таблиц в базе данных

1) На вход файл с пакетами скриптов, процедур таблиц и функций. 
2) На выходе csv, в котором структура:

~~~ json
{
    'схема': main_schema,
    'наименование таблицы': main_table,
    'тип таблицы': 'например: продуктовая витрина',
    'критичность переноса': 'например: высокая',
    'зависимая таблица': dependent_table,
    'схема зависимой таблицы': dependent_schema
}
~~~

## Запуск скрипта

1) Склонируйте репозиторий `git clone https://github.com/ivbbest/structure_mapping_db` в текущую папку.


2) Переходим в папку с проектом.

    `cd structure_mapping_db`


3) Заполнить config.py, а именно:

- file_code_package_bodies;
- main_schema;
- all_table_name.

4) Добавить файл с пакетами данных = file_code_package_bodies.

5) Если хотим запустить основной скрипт:

- Linux:

    `python3 mapping.py`


- Windows:

    `python mapping.py`

6) Получаем csv файл results.csv.