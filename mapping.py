from config import all_table_name, file_code_package_bodies, main_schema
import re
from collections import defaultdict
import csv


def get_current_table(line: str) -> str:
    """Проверка наличия алиаса рядом с таблицей и возврат только самой таблицы"""
    line = line if line.find(' ') == -1 else line.split()[0]

    if line in all_table_name or (line.find('.') != -1 and line.find('_') != -1):
        return line.strip('()')


def get_table_from_section_from_or_join(line: str) -> str:
    """Получить таблицу из раздела from или join"""
    line = re.split(r'from|join', line)[1]
    line = re.split(r'\swhere\s|\son\s', line)[0].strip()

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
            elif (re.search(r'from', line) and not re.search(r'extract|coalesce|vw_', line)) or re.search(r'join',
                                                                                                          line):
                hash_tables[table].add(get_table_from_section_from_or_join(line))

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

    return list_depedent_for_csv


def create_csv_file(name_file: str, list_depedents_for_csv: list) -> None:
    """Создание csv файла"""
    with open(f"{name_file}.csv", mode="w", encoding='utf-8-sig') as w_file:
        file_writer = csv.DictWriter(w_file, lineterminator="\r",
                                     fieldnames=list_depedents_for_csv[0].keys(), delimiter=';')
        file_writer.writeheader()
        file_writer.writerows(list_depedents_for_csv)


def main():
    """Точка входа"""
    hash_tables = get_hashmap_dependent_tables(file_code_package_bodies)
    list_depedent_for_csv = get_list_depedent(hash_tables)
    create_csv_file('results', list_depedent_for_csv)


if __name__ == "__main__":
    main()
