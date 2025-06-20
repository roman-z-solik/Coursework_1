import json
import logging
from datetime import datetime

from src.config import data_file, logs_path, root_path
from src.services import cashback, search_word, search_number, search_name
from src.utils import (
    cards_info,
    currency_rates,
    expenses_by_category,
    income_by_category,
    read_info,
    sorted_by_date,
    stocks_prices,
    top_transactions,
    total_expenses,
    total_income,
)

logging.basicConfig(
    filename=f'{logs_path}/logs.log',
    encoding='utf-8',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(filename)s - %(levelname)s: %(message)s',
)

logger_util = logging.getLogger('app.services')


def greeting() -> str | None:
    """Функция, формирующая приветствие в зависимости от текущего времени."""
    logger_util.info('Запуск функции формирующей приветствие в зависимости от текущего времени.')
    greeting_dict = ['Доброе утро', 'Добрый день', 'Добрый вечер', 'Доброй ночи']
    current_hour = datetime.now().hour
    if 6 <= current_hour <= 11:
        logger_util.info('Приветствие сформировано корректно.')
        return greeting_dict[0]
    elif 12 <= current_hour <= 17:
        logger_util.info('Приветствие сформировано корректно.')
        return greeting_dict[1]
    elif 18 <= current_hour <= 23:
        logger_util.info('Приветствие сформировано корректно.')
        return greeting_dict[2]
    elif 0 <= current_hour <= 5:
        logger_util.info('Приветствие сформировано корректно.')
        return greeting_dict[3]
    else:
        logger_util.info('Приветствие не сформировано.')
        print('Ошибка определения времени суток')
        return None


def json_answer_main(start_date_str: str, diapason: str = "M") -> str:
    """
    Функция, формирующая JSON ответ для страницы "Главная":
        Приветствие в формате "???", где ??? — «Доброе утро» / «Добрый день» /
        «Добрый вечер» / «Доброй ночи» в зависимости от текущего времени.

        По каждой карте:
            последние 4 цифры карты;
            общая сумма расходов;
            кешбэк (1 рубль на каждые 100 рублей).
        Топ-5 транзакций по сумме платежа.
        Курс валют.
        Стоимость акций из S&P500.
        Возвращает строку в формате JSON.
    """
    answer_dict: dict = {
        "greeting": greeting(),
        "cards": cards_info(sorted_by_date(read_info(data_file), start_date_str, diapason)),
        "top_transactions": top_transactions(sorted_by_date(read_info(data_file), start_date_str, diapason)),
        "currency_rates": currency_rates(),
        "stock_prices": stocks_prices(),
    }
    answer_string = json.dumps(answer_dict, ensure_ascii=False, indent=4)
    with open(f"{root_path}/data/answer_main.json", "w", encoding="utf-8") as f:
        json.dump(answer_string, f, ensure_ascii=False, indent=4)
    return answer_string


def json_answer_events(start_date_str: str, diapason: str = "M") -> str:
    """
    Функция, формирующая JSON ответ для страницы "События":
        «Расходы»:
            Общая сумма расходов.
            Раздел «Основные», в котором траты по категориям отсортированы по убыванию. Данные
            предоставляются по 7 категориям с наибольшими тратами, траты по остальным категориям
            суммируются и попадают в категорию «Остальное».
        «Поступления»:
            Общая сумма поступлений.
            Раздел «Основные», в котором поступления по категориям отсортированы по убыванию.
        Курс валют.
        Стоимость акций из S&P500.
        Возвращает строку в формате JSON.
    """
    answer_dict: dict = {
        "expenses": {
            "total_amount": round(
                float(total_expenses(sorted_by_date(read_info(data_file), start_date_str, diapason))), 2
            ),
            "main": expenses_by_category(sorted_by_date(read_info(data_file), start_date_str, diapason)),
        },
        "income": {
            "total_amount": round(float(total_income(sorted_by_date(read_info(data_file), start_date_str, diapason))), 2),
            "main": income_by_category(sorted_by_date(read_info(data_file), start_date_str, diapason)),
        },
        "currency_rates": currency_rates(),
        "stock_prices": stocks_prices(),
    }
    answer_string = json.dumps(answer_dict, ensure_ascii=False, indent=4)
    with open(f"{root_path}/data/answer_events.json", "w", encoding="utf-8") as f:
        json.dump(answer_string, f, ensure_ascii=False, indent=4)
    return answer_string


def json_answer_cashback(year_str: str, month_str: str) -> str:
    """
    Функция, формирующая JSON ответ для страницы "Сервисы":
        JSON с анализом, сколько на каждой категории можно заработать кешбэка.
            Формат выходных данных:
                {
                    "Категория 1": 1000,
                    "Категория 2": 2000,
                    "Категория 3": 500
                }
    """
    answer_dict: dict = {"cashback": cashback(read_info(data_file), year_str, month_str)}
    answer_string = json.dumps(answer_dict, ensure_ascii=False, indent=4)
    with open(f"{root_path}/data/answer_events.json", "w", encoding="utf-8") as f:
        json.dump(answer_string, f, ensure_ascii=False, indent=4)
    return answer_string


def json_answer_search(search_data: str) -> str | None:
    if search_data == 'cellphone':
        result = search_number(read_info(data_file), 'cellphone')
        return result
    elif search_data == 'transfer':
        result = search_name(read_info(data_file), 'transfer')
        return result
    else:
        result = search_word(read_info(data_file), search_data)
        return result
