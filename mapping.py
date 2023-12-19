from enum import Enum
from config import all_table_name, code_package_bodies
import re
from collections import defaultdict
from pprint import pprint


class SearchElement(str, Enum):
    """Поиск ключевых слов для выборки таблиц"""
    INSERT = 'insert into'
    FROM = 'from'
    JOIN = 'join'
    MERGE = 'merge into'
    EXTRACT = 'extract'

    # Эти разделители должны быть в join
    POINT = '.'
    UNDER = '_'


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
    line = line.split('join ')[1].split(' on ')[0]

    return get_current_table(line)


def get_name_tables(line: str) -> str:
    """Получить название таблицы из раздела insert или merge"""
    line = line.split(' into ')[1] if line.find('(') == -1 else line.split(' into ')[1].split('(')[0]

    return get_current_table(line)

hash_tables = defaultdict(set)

with open(code_package_bodies, 'r', encoding='UTF-8') as f:
    for line in f:
        line = line.lower().strip(' \n')
        if line.startswith('--'):
            continue
        elif re.search(r"merge into|insert into", line):
            table = get_name_tables(line)
        elif re.search(r'from', line) and not re.search(r'extract|coalesce', line):
            hash_tables[table].add(get_tables_from_key_from(line))
        elif re.search(r'join', line):
            hash_tables[table].add(get_tables_from_key_join(line))

pprint(hash_tables)