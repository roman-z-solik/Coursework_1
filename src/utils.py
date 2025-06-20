import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Hashable

import pandas as pd
import requests
from dotenv import load_dotenv

from src.config import logs_path, root_path, data_file, user_settings_file

load_dotenv()
api_key = os.getenv("Alpha_Vantage_API_KEY")

logging.basicConfig(
    filename=f"{logs_path}/logs.log",
    encoding="utf-8",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s: %(message)s",
)

logger_util = logging.getLogger("app.utils")


def read_info(path_xls: str) -> pd.DataFrame | None:
    """
    Функция для считывания финансовых операций из Excel,
    принимает путь к файлу Excel в качестве аргумента.
    """
    try:
        with open(path_xls, 'rb') as f:
            logger_util.info(f'Файл {root_path}/{path_xls} корректно открыт')
            df = pd.read_excel(f)
            df = df[df['Статус'] == 'OK']
            return df
    except (FileNotFoundError, PermissionError) as e:
        logger_util.info(f'Ошибка при чтении файла {root_path}/{path_xls}: {str(e)}')
        print(f'Ошибка при чтении файла {root_path}/{path_xls}: {str(e)}')
        return None

def read_user_settings(settings: str) -> Any | None:
    """
    Функция, которая принимает JSON-файл с настройками пользователя
    и возвращает список с нужными для вывода данными
    """
    try:
        with open(f"{user_settings_file}", "r", encoding="utf-8") as json_file:
            json_file_content = json.load(json_file)
            read_data = json_file_content[settings]
            return read_data
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        print(f"Ошибка чтения файла {user_settings_file}: {str(e)}")
        logger_util.error(f"Ошибка чтения файла {user_settings_file}: {str(e)}")
        return None


def output_date(date_str: str, diapason: str = "M") -> datetime | str:
    """
    Функция, которая принимает начальную дату и диапазон и выдает конечную дату
    в этом диапазоне (W - неделя, M - месяц, Y = год, All = все даты)
    """
    end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    if diapason == "W":
        weekly_day = end_date - timedelta(days=end_date.weekday())
        start_date = datetime(end_date.year, end_date.month, weekly_day.day, 0, 0, 0)
        return start_date
    elif diapason == "Y":
        start_date = datetime(end_date.year, 1, 1, 0, 0, 0)
        return start_date
    elif diapason == "All":
        start_date = datetime(1900, 1, 1, 0, 0, 0)
        return start_date
    elif diapason == "M":
        start_date = datetime(end_date.year, end_date.month, 1, 0, 0, 0)
        return start_date
    else:
        return "Ошибка даты"


def sorted_date(df: pd.DataFrame, date_str: str, diapason: str = "M") -> pd.DataFrame:
    """
    Функция, которая принимает данные, конечную дату и диапазон и выдает все операции
    в этом диапазоне (W - неделя, M - месяц, Y = год, All = все опрерации)
    """
    df = df.assign(daytime=pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S"))
    end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_date = output_date(date_str, diapason)
    df = df[df["daytime"].between(start_date, end_date)]
    df = df.sort_values(by="daytime", ascending=False)
    df = df.drop("daytime", axis=1)
    return df







# print(read_info(data_file))
# print(read_user_settings('user_stocks'))
print(sorted_date(read_info(data_file),'2021-12-07 14:55:21', 'All'))
