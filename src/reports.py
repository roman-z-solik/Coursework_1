import datetime
import logging
from functools import wraps
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.config import logs_path, root_path

logging.basicConfig(
    filename=logs_path / "logs.log",
    encoding="utf-8",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
)

reports_logger = logging.getLogger("app.reports")


def writing_report_to_file(func):
    "Декоратор, который записывает данные отчета в файл data/report.xlsx"

    reports_logger.info('Запуск декоратора "writing_report_to_file"')

    @wraps(func)
    def wrapper(*args, **kwargs):

        try:
            result = func(*args, **kwargs)
            result.to_excel(root_path / "report.xlsx")
            reports_logger.info('Отчет успешно записан в "report.xlsx"')

        except Exception as e:
            print(f"{func.__name__} error: {e}. Inputs: {args}, {kwargs}")
            reports_logger.error(
                f"Ошибка функции{func.__name__}: {e}. Inputs: {args}, {kwargs} в функции writing_report_to_file"
            )
            result = None

        return result

    return wrapper


def writing_report_to_file_by_user(filename="report.xlsx"):
    "Декоратор, который записывает данные отчета в файл указанный в параметре"

    reports_logger.info(f'Запуск декоратора "writing_report_to_file_by_user" с параметром {filename}')

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            try:
                result = func(*args, **kwargs)
                result.to_excel(root_path / filename)
                reports_logger.info(f"Отчет успешно записан в {filename}")

            except Exception as e:
                print(f"{func.__name__} error: {e}. Inputs: {args}, {kwargs}")
                reports_logger.error(
                    f"Ошибка функции{func.__name__}: {e}. Inputs: {args}, {kwargs} в writing_report_to_file_by_user"
                )
                result = None

            return result

        return wrapper

    return decorator


@writing_report_to_file_by_user("111.xlsx")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    "Функция, которая возвращает траты по заданной категории за последние три месяца"
    reports_logger.info('Запуск функции "spending_by_category"')
    if date is None:
        date_obj = datetime.datetime.now()
    else:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    beginning_date = date_obj - relativedelta(months=3)

    df_transactions_in_category = transactions[
        (transactions["Статус"] == "OK")
        & (transactions["Сумма платежа"] <= 0)
        & (transactions["Категория"] == category)
    ]
    df_in_date = df_transactions_in_category[
        (df_transactions_in_category["Дата операции"] >= beginning_date)
        & (df_transactions_in_category["Дата операции"] <= date_obj)
    ]
    df_sum_in_category = df_in_date.groupby("Категория")
    sum_transactions_in_category = df_sum_in_category["Сумма платежа"].sum()
    return sum_transactions_in_category
