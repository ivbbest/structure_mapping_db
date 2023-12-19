from config import all_table_name, code_package_bodies, main_schema
import re
from collections import defaultdict
from pprint import pprint
import csv
import traceback


def get_current_table(line: str) -> str:
    """Проверка наличия алиаса рядом с таблицей и возврат только самой таблицы"""
    line = line if line.find(' ') == -1 else line.split()[0]

    if line in all_table_name or (line.find('.') != -1 and line.find('_') != -1):
        return line.strip('()')


def get_tables_from_key_from(line: str) -> str:
    """Получить все таблицы из раздела from"""
    line = line.lower().split('from')[1].strip(' \n')

    if line.find(' where ') != -1:
        line = line.split(' where ')[0]

    return get_current_table(line)


def get_tables_from_key_join(line: str) -> str:
    """Получить все таблицы из раздела join"""
    try:
        line = line.split('join')[1].split(' on ')[0]
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))

    return get_current_table(line)


def get_name_tables(line: str) -> str:
    """Получить название таблицы из раздела insert или merge"""
    line = line.split(' into ')[1] if line.find('(') == -1 else line.split(' into ')[1].split('(')[0]

    return get_current_table(line)


# TODO: считывание данных не из одного файла, а из папки, где много сразу файлов
def get_hashmap_dependent_tables(code_package_bodies) -> dict:
    """Получение хэш-таблицы с зависимостями таблиц из всех пакетов"""
    hash_tables = defaultdict(set)

    with open(code_package_bodies, 'r', encoding='UTF-8') as f:
        for line in f:
            line = line.lower().strip(' \n ')
            if line.startswith('--'):
                continue
            elif re.search(r"merge into|insert into", line):
                table = get_name_tables(line)
            elif re.search(r'from', line) and not re.search(r'extract|coalesce|vw_', line):
                hash_tables[table].add(get_tables_from_key_from(line))
            elif re.search(r'join', line):
                hash_tables[table].add(get_tables_from_key_join(line))

    # pprint(hash_tables)

    return hash_tables


def get_list_depedent(hash_tables: dict) -> list:
    """Получение  словарей с данными для дальнейшей загрузки в csv"""
    list_depedent_for_csv = list()

    for main_table, value in hash_tables.items():
        for val in value:
            if val is None:
                continue

            try:
                dependent_schema, dependent_table = str(val).split('.')
            except Exception as e:
                dependent_table = val
                dependent_schema = main_schema

            list_depedent_for_csv.append(
                {
                    'схема АПЛ': main_schema,
                    'наименование таблицы': main_table,
                    'тип таблицы': 'продуктовая витрина',
                    'критичность переноса на КАПe': 'высокая',
                    'зависимая таблица': dependent_table,
                    'схема зависимой таблицы': dependent_schema
                }
            )

    # pprint(list_depedent_for_csv)
    return list_depedent_for_csv


def create_csv_file(name_file: str, list_depedents_for_csv: list) -> None:
    """Создание csv файла"""
    with open(f"{name_file}.csv", mode="w", encoding='utf-8-sig') as w_file:
        file_writer = csv.DictWriter(w_file, lineterminator="\r",
                                     fieldnames=list_depedents_for_csv[0].keys(), delimiter=';')
        file_writer.writeheader()
        file_writer.writerows(list_depedents_for_csv)


def main():
    hash_tables = get_hashmap_dependent_tables(code_package_bodies)
    list_depedent_for_csv = get_list_depedent(hash_tables)
    create_csv_file('results2', list_depedent_for_csv)


if __name__ == "__main__":
    main()
