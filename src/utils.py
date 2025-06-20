import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Hashable

import pandas as pd
import requests
from dotenv import load_dotenv

from src.config import logs_path, root_path, user_settings_file

load_dotenv()
api_key = os.getenv("Alpha_Vantage_API_KEY")

logging.basicConfig(
    filename=f"{logs_path}/logs.log",
    encoding="utf-8",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s: %(message)s",
)

logger_util = logging.getLogger("app.services")


def read_info(path_xls: str) -> pd.DataFrame | None:
    """
    Функция для считывания финансовых операций из Excel,
    принимает путь к файлу Excel в качестве аргумента.
    """
    logger_util.info("Запуск функции чтения данных из файла")
    try:
        df = pd.read_excel(path_xls)
        logger_util.info(f"Файл {path_xls} корректно прочитан")

        df = df[df["Статус"] == "OK"]

        return df
    except FileNotFoundError:
        logger_util.error(f"Файл {path_xls} не найден")
        return None
    except pd.errors.EmptyDataError:
        logger_util.error(f"Файл {path_xls} пуст")
        return None
    except Exception as e:
        logger_util.error(f"Произошла ошибка при чтении файла {path_xls}: {e}")
        return None


def read_user_settings(settings: str) -> Any | None:
    """
    Функция, которая принимает JSON-файл с настройками пользователя
    и возвращает список с нужными для вывода данными
    """
    logger_util.info("Запуск функции чтения настроек")
    try:
        with open(f"{user_settings_file}", "r", encoding="utf-8") as json_file:
            json_file_content = json.load(json_file)
            logger_util.info(f"Файл {root_path}/{user_settings_file} корректно прочитан")
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
    logger_util.info("Запуск функции расчета даты начала и конца диапазона")
    end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    if diapason == "W":
        weekly_day = end_date - timedelta(days=end_date.weekday())
        start_date = datetime(end_date.year, end_date.month, weekly_day.day, 0, 0, 0)
        logger_util.info("Функция расчета даты начала и конца диапазона выполнена корректно")
        return start_date
    elif diapason == "Y":
        start_date = datetime(end_date.year, 1, 1, 0, 0, 0)
        logger_util.info("Функция расчета даты начала и конца диапазона выполнена корректно")
        return start_date
    elif diapason == "All":
        start_date = datetime(1900, 1, 1, 0, 0, 0)
        logger_util.info("Функция расчета даты начала и конца диапазона выполнена корректно")
        return start_date
    elif diapason == "M":
        start_date = datetime(end_date.year, end_date.month, 1, 0, 0, 0)
        logger_util.info("Функция расчета даты начала и конца диапазона выполнена корректно")
        return start_date
    else:
        logger_util.info("Ошибка даты")
        print("Ошибка даты")
        return "Ошибка даты"


def sorted_by_date(df: pd.DataFrame, date_str: str, diapason: str = "M") -> pd.DataFrame:
    """
    Функция, которая принимает данные, конечную дату и диапазон и выдает все операции
    в этом диапазоне (W - неделя, M - месяц, Y = год, All = все опрерации)
    """
    logger_util.info("Запуск функции сортировки данных по диапазону дат")
    df = df.assign(daytime=pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S"))
    end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_date = output_date(date_str, diapason)
    df = df[df["daytime"].between(start_date, end_date)]
    df = df.sort_values(by="daytime", ascending=False)
    df = df.drop("daytime", axis=1)
    logger_util.info("Сортировка данных по диапазону дат успешна")
    return df


def cards_info(df: pd.DataFrame) -> list:
    """
    Функция, которая принимает отсортированные данные и выдает информацию по картам:
        последние 4 цифры карты;
        общая сумма расходов;
        кешбэк (1 рубль на каждые 100 рублей).
        Возвращает список.
    """
    logger_util.info("Запуск функции сбора информации по кредитным картам для страницы Main")
    df = df[df["Сумма платежа"] < 0]
    df = df.loc[:, ["Номер карты", "Сумма платежа"]].groupby("Номер карты").sum().reset_index()
    df["Номер карты"] = df["Номер карты"].str.slice(1)
    df["Сумма платежа"] = df["Сумма платежа"] * -1
    df["Сумма платежа"] = df["Сумма платежа"].round(2)
    df = df.assign(cashback=(df["Сумма платежа"] / 100))
    df["cashback"] = df["cashback"].round(2)
    df.rename(columns={"Номер карты": "last_digits"}, inplace=True)
    df.rename(columns={"Сумма платежа": "total_spent"}, inplace=True)
    df_list = df.to_dict(orient="records")
    logger_util.info("Информация по кредитным картам для страницы Main собрана корректно")
    return df_list


def top_transactions(df: pd.DataFrame) -> list:
    """Функция, которая принимает данные и выдает информацию - топ-5 транзакций по сумме платежа."""
    logger_util.info("Запуск функции сбора топ-5 транзакций по сумме платежа для страницы Main")
    df = df[df["Сумма платежа"] < 0]
    df = df.sort_values(by="Сумма платежа", ascending=True)
    df = df.loc[:, ["Дата операции", "Сумма платежа", "Категория", "Описание"]]
    df = df[:5]
    df["Сумма платежа"] = df["Сумма платежа"] * -1
    df["Дата операции"] = df["Дата операции"].str.slice(0, 10)
    df.rename(columns={"Дата операции": "date"}, inplace=True)
    df.rename(columns={"Сумма платежа": "amount"}, inplace=True)
    df.rename(columns={"Категория": "category"}, inplace=True)
    df.rename(columns={"Описание": "description"}, inplace=True)
    df_list = df.to_dict(orient="records")
    logger_util.info("Топ-5 транзакций по сумме платежа для страницы Main собрана корректно")
    return df_list


def currency_rates() -> list | str:
    """Функция получения курса валют"""
    try:
        logger_util.info("Запуск функции получения курса валют")
        valute_list = read_user_settings("user_currencies")
        data = requests.get("https://www.cbr-xml-daily.ru/daily_json.js").json()
        data = data["Valute"]
        sample_valute = {}
        sorted_valute = []
        for valute in valute_list:
            for key, value in data.items():
                if key == valute:
                    sample_valute["currency"] = valute
                    sample_valute["rate"] = round(value["Value"], 2)
                    sorted_valute.append(sample_valute)
                    sample_valute = {}
                else:
                    continue
        logger_util.info("Курсы валют собраны успешно")
        return sorted_valute
    except requests.exceptions.RequestException as e:
        logger_util.error(f"Ошибка получения курса валют. Код ошибки: {e}")
        return f"Ошибка получения курса валют. Код ошибки: {e}"
    except (KeyError, TypeError) as e:
        logger_util.error(f"Ошибка получения курса валют. Код ошибки: {e}")
        return f"Ошибка получения курса валют. Код ошибки {e}"


def stocks_prices() -> list | str:
    """Функция получения стоимости акций"""
    try:
        logger_util.info("Запуск функции получения стоимости акций")
        stock_list = read_user_settings("user_stocks")
        sample_stock = {}
        sorted_stock = []
        for stock in stock_list:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
            response = requests.get(url, timeout=10)
            stock_price = round(float(response.json()["Global Quote"]["05. price"]), 2)
            sample_stock["stock"] = stock
            sample_stock["price"] = stock_price
            sorted_stock.append(sample_stock)
            sample_stock = {}
            logger_util.info("Стоимости акций собраны успешно")
        return sorted_stock
    except requests.exceptions.RequestException as e:
        logger_util.error(f"Ошибка получения стоимости акций. Код ошибки: {e}")
        return f"Ошибка получения стоимости акций. Код ошибки: {e}"
    except (KeyError, TypeError) as e:
        logger_util.error(f"Ошибка получения стоимости акций. Код ошибки: {e}")
        return f"Ошибка получения стоимости акций. Код ошибки: {e}"


def total_expenses(df: pd.DataFrame) -> int:
    """Функция, подсчитывающая общую сумму расходов"""
    logger_util.info("Запуск функции подсчета суммы всех расходов за период")
    df = df[df["Сумма платежа"] < 0]
    total = df["Сумма платежа"].sum().sum()
    logger_util.info("Подсчет суммы всех расходов за период успешен")
    return round(int(total * -1), 2)


def expenses_by_category(df: pd.DataFrame) -> list[dict[Hashable, Any]]:
    """
    Функция, формирующая раздел «Основные», в котором траты по категориям
    отсортированы по убыванию. Данные предоставляются по 7 категориям с
    наибольшими тратами, траты по остальным категориям суммируются и попадают
    в категорию «Остальное».
    """
    logger_util.info("Запуск функции подсчета расходов за период по категориям")
    df = df[df["Сумма платежа"] < 0]
    df["Сумма платежа"] = df["Сумма платежа"] * -1
    df = df.loc[:, ["Сумма платежа", "Категория"]].groupby("Категория").sum().reset_index()
    df = df.sort_values(by="Сумма платежа", ascending=False)
    df_top = df[:7]
    df_other = df[8:]
    df_other_sum = float(df_other["Сумма платежа"].sum())
    new_row = pd.DataFrame([{"Категория": "Остальное", "Сумма платежа": df_other_sum}])
    df = pd.concat([df_top, new_row], ignore_index=True)
    df.rename(columns={"Категория": "category"}, inplace=True)
    df.rename(columns={"Сумма платежа": "amount"}, inplace=True)
    df_list = df.to_dict(orient="records")
    for amount in df_list:
        amount["amount"] = round(amount["amount"], 2)
    logger_util.info("Подсчет всех расходов за период по категориям успешен")
    return df_list


def total_income(df: pd.DataFrame) -> Any:
    """Функция, подсчитывающая общую сумму поступлений"""
    logger_util.info("Запуск функции подсчета суммы всех поступлений за период")
    df = df[df["Сумма платежа"] > 0]
    total = df["Сумма платежа"].sum().sum()
    logger_util.info("Подсчет суммы всех поступлений за период успешен")
    return round(total, 2)


def income_by_category(df: pd.DataFrame) -> list:
    """
    Функция, формирующая раздел «Основные», в котором поступления по
    категориям отсортированы по убыванию.
    """
    logger_util.info("Запуск функции подсчета поступлений за период по категориям")
    df = df[df["Сумма платежа"] > 0]
    df = df.loc[:, ["Сумма платежа", "Категория"]].groupby("Категория").sum().reset_index()
    df = df.sort_values(by="Сумма платежа", ascending=False)
    df_top = df[:7]
    df_other = df[8:]
    df_other_sum = float(round(df_other["Сумма платежа"].sum(), 2))
    new_row = pd.DataFrame([{"Категория": "Остальное", "Сумма платежа": df_other_sum}])
    df = pd.concat([df_top, new_row], ignore_index=True)
    df.rename(columns={"Категория": "category"}, inplace=True)
    df.rename(columns={"Сумма платежа": "amount"}, inplace=True)
    df_list = df.to_dict(orient="records")
    for x in df_list:
        x["amount"] = round(x["amount"], 2)
    logger_util.info("Подсчет всех поступлений за период по категориям успешен")
    return df_list
