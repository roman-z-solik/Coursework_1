import calendar
import json
import logging

import pandas as pd

from src.config import logs_path, root_path, data_file
from src.utils import sorted_by_date, read_info

logging.basicConfig(
    filename=f'{logs_path}/logs.log',
    encoding='utf-8',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(filename)s - %(levelname)s: %(message)s',
)

logger_util = logging.getLogger('app.services')


def cashback(df: pd.DataFrame, year: str, month: str) -> str:
    """Функция, подсчитывающая, сколько на каждой категории можно заработать кешбэка."""
    logger_util.info('Запуск функции подсчета кэшбэка успешен')
    df = df.where(pd.notnull(df), None)
    _, last_day = calendar.monthrange(int(year), int(month))
    end_date = f'{year}-{month}-{last_day} 23:59:59'
    df = sorted_by_date(df, end_date)
    df = df[df['Статус'] == 'OK']
    df = df[df['Кэшбэк'] > 0]
    df = df.loc[:, ['Кэшбэк', 'Категория']].groupby('Категория').sum().reset_index()
    df_list = df.to_dict(orient='records')
    answer_string = json.dumps(df_list, ensure_ascii=False, indent=4)
    with open(f'{root_path}/data/cashback.json', 'w', encoding='utf-8') as f:
        json.dump(answer_string, f, ensure_ascii=False, indent=4)
    logger_util.info('Файл cashback.json и подсчет кэшбэка сформирован успешно')
    return answer_string


def search_word(df: pd.DataFrame, search_word_str: str) -> str | None:
    """Функция поиска слова в описании или категории"""
    logger_util.info('Запуск функции поиска')
    df = df.where(pd.notnull(df), None)
    df = df[
        (df['Описание'].str.contains(search_word_str, case=False, na=False))
        | (df['Категория'].str.contains(search_word_str, case=False, na=False))
    ]
    df_list = df.to_dict(orient='records')
    answer_string = json.dumps(df_list, ensure_ascii=False, indent=4)
    with open(f'{root_path}/data/search_word.json', 'w', encoding='utf-8') as f:
        json.dump(answer_string, f, ensure_ascii=False, indent=4)
    logger_util.info('Файл search_world.json и поиск сформирован успешно')
    return answer_string


def search_number(df: pd.DataFrame, search_word_str: str) -> str | None:
    """Функция поиска транзакций, в описании содержащий мобильные номера"""
    logger_util.info('Запуск функции поиска транзакций с мобильными номерами в описании')
    number_mask = r"(8 | \+7).\d+"
    if search_word_str == 'cellphone':
        df = df.where(pd.notnull(df), None)
        df = df[(df['Описание'].str.contains(number_mask, na=False))]
        df_list = df.to_dict(orient='records')
        answer_string = json.dumps(df_list, ensure_ascii=False, indent=4)
        with open(f'{root_path}/data/search_number.json', 'w', encoding='utf-8') as f:
            json.dump(answer_string, f, ensure_ascii=False, indent=4)
        logger_util.info('Файл search_number.json и поиск транзакций с мобильными номерами в описании сформирован успешно')
        return answer_string
    else:
        return None


def search_name(df: pd.DataFrame, search_word_str: str) -> str | None:
    """Функция поиска транзакций, в описании содержащий имена для перевода"""
    logger_util.info('Запуск функции поиска транзакций с именами в описании')
    letter_mask = r"[А-Я]\."
    if search_word_str == 'transfer':
        df = df.where(pd.notnull(df), None)
        df = df[(df['Описание'].str.contains(letter_mask, na=False))]
        df_list = df.to_dict(orient='records')
        answer_string = json.dumps(df_list, ensure_ascii=False, indent=4)
        with open(f'{root_path}/data/search_number.json', 'w', encoding='utf-8') as f:
            json.dump(answer_string, f, ensure_ascii=False, indent=4)
        logger_util.info('Файл search_number.json и поиск транзакций с именами в описании сформирован успешно')
        return answer_string
    else:
        return None
