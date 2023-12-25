from config import all_table_name, file_code_package_bodies, main_schema
import re
from collections import defaultdict, namedtuple
import csv
from typing import NamedTuple
from exceptions import catch_all_exceptions


@catch_all_exceptions('алиасов у таблицы')
def get_current_table(line: str) -> str:
    """Проверка наличия алиаса рядом с таблицей и возврат только самой таблицы"""
    line = line if line.find(' ') == -1 else line.split()[0]

    if line in all_table_name or (line.find('.') != -1 and line.find('_') != -1):
        return line.strip('()')


@catch_all_exceptions('from или join')
def get_table_from_section_from_or_join(line: str) -> str:
    """Получить таблицу из раздела from или join"""
    line = re.split(r'from|join', line)[1]
    line = re.split(r'\swhere\s|\son\s', line)[0].strip()

    return get_current_table(line)


@catch_all_exceptions('insert или merge')
def get_name_tables(line: str) -> str:
    """Получить название таблицы из раздела insert или merge"""
    line = line.split(' into ')[1] if line.find('(') == -1 else line.split(' into ')[1].split('(')[0]

    return get_current_table(line)


# TODO: считывание данных не из одного файла, а из папки, где много сразу файлов
def get_hashmap_dependent_tables(code_package_bodies) -> NamedTuple:
    """Получение хэш-таблицы с зависимостями таблиц из всех пакетов"""
    tables = defaultdict(set)
    packages_and_procedures = defaultdict(dict)
    hash_data = namedtuple('hash_data', 'tables packages_and_procedures')

    with open(code_package_bodies, 'r', encoding='UTF-8') as f:
        for number_line, line in enumerate(f):
            line = line.lower().strip(' \n ')
            if line.startswith('--'):
                continue
            elif re.search(r"package body", line):
                package_name = line.split(' body ')[1].split(' is')[0]
            elif re.search(r"merge into|insert into", line):
                table_name = get_name_tables(line)
            elif (re.search(r'from', line) and not re.search(r'extract|coalesce|vw_', line)) or re.search(r'join',
                                                                                                          line):
                tables[table_name].add(get_table_from_section_from_or_join(line))
            elif re.search(r"procedure", line):
                procedure_name = line.split('procedure')[1].strip().split(' is')[0]
                start_line = number_line
            elif re.search(r"end;", line):
                end_line = number_line
                packages_and_procedures[package_name].update({procedure_name: end_line - start_line + 2})

    return hash_data(tables=tables, packages_and_procedures=packages_and_procedures)


def get_list_tables_depedent(hash_tables: dict) -> list:
    """Получение словарей с зависимостями таблиц для дальнейшей загрузки в csv"""
    list_tables_depedent = list()

    for main_table, value in hash_tables.items():
        for val in value:
            if val is None:
                continue

            try:
                dependent_schema, dependent_table = str(val).split('.')
            except Exception as e:
                dependent_table = val
                dependent_schema = main_schema

            list_tables_depedent.append(
                {
                    'схема АПЛ': main_schema,
                    'наименование таблицы': main_table,
                    'тип таблицы': 'продуктовая витрина',
                    'критичность переноса на КАПe': 'высокая',
                    'зависимая таблица': dependent_table,
                    'схема зависимой таблицы': dependent_schema
                }
            )

    return list_tables_depedent


def get_packages_and_procedures_count_row(hash_packages_and_procedures: dict) -> list:
    """Получение словарей с пакетами и количеством строк в каждой процедуре для дальнейшей загрузки в csv"""
    list_packages_and_procedure = list()

    for package, procedures in hash_packages_and_procedures.items():
        for procedure, row_procedure in procedures.items():
            list_packages_and_procedure.append(
                {
                    'схема АПЛ': main_schema,
                    'наименование пакета': package,
                    'наименование процедуры': procedure,
                    'объем кода': row_procedure,
                    'критичность переноса на КАП': '',
                    'цель': ''
                }
            )

    return list_packages_and_procedure


def create_csv_file(name_file: str, list_input_data: list) -> None:
    """Создание csv файла на основе списка данных"""
    with open(f"{name_file}.csv", mode="w", encoding='utf-8-sig') as w_file:
        file_writer = csv.DictWriter(w_file, lineterminator="\r",
                                     fieldnames=list_input_data[0].keys(), delimiter=';')
        file_writer.writeheader()
        file_writer.writerows(list_input_data)


def main() -> None:
    """Точка входа"""
    hash_tables, hash_packages = get_hashmap_dependent_tables(file_code_package_bodies)
    list_tables_depedent = get_list_tables_depedent(hash_tables)
    list_packages_and_procedures = get_packages_and_procedures_count_row(hash_packages)
    create_csv_file('tables_depedent', list_tables_depedent)
    create_csv_file('packages_procedure', list_packages_and_procedures)


if __name__ == "__main__":
    main()
