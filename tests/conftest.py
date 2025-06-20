from unittest.mock import patch

import pytest
import datetime
import pandas as pd


@pytest.fixture
def mock_transactions():
    return pd.DataFrame(
        {
            "Дата операции": [datetime.datetime(2023, 1, 1), datetime.datetime(2023, 2, 1), datetime.datetime(2023, 3, 1), datetime.datetime(2023, 4, 1)],
            "Статус": ["OK", "OK", "FAILED", "OK"],
            "Сумма платежа": [-1000, -2000, 500, -1500],
            "Категория": ["Книги", "Книги", "Еда", "Книги"],
        }
    )


@pytest.fixture(scope='module')
def sample_df():
    data = {
        'Дата операции': ['01.01.2023 12:00:00', '07.01.2023 15:30:00',
                         '15.01.2023 10:15:00', '25.01.2023 18:45:00'],
        'Описание': ['Операция 1', 'Операция 2', 'Операция 3', 'Операция 4']
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_df():
    data = [
        {'Дата операции': '31.12.2021 16:44:00', 'Номер карты': '*1234', 'Сумма платежа': -100.0},
        {'Дата операции': '31.12.2021 16:44:00', 'Номер карты': '*1234', 'Сумма платежа': -200.0},
        {'Дата операции': '31.12.2021 16:44:00', 'Номер карты': '*5678', 'Сумма платежа': -300.0},
        {'Дата операции': '31.12.2021 16:44:00', 'Номер карты': '*5678', 'Сумма платежа': -400.0},
        {'Дата операции': '31.12.2021 16:44:00', 'Номер карты': '*3333', 'Сумма платежа': 50.0},
    ]
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def mock_df1():
    # Создание фиктивных данных для теста
    data = [
        {"Дата операции": "2023-01-01 12:00:00", "Сумма платежа": -100, "Категория": "Еда", "Описание": "Покупка продуктов"},
        {"Дата операции": "2023-01-02 13:00:00", "Сумма платежа": -200, "Категория": "Развлечения", "Описание": "Кино"},
        {"Дата операции": "2023-01-03 14:00:00", "Сумма платежа": -300, "Категория": "Транспорт", "Описание": "Такси"},
        {"Дата операции": "2023-01-04 15:00:00", "Сумма платежа": -400, "Категория": "Одежда", "Описание": "Новая куртка"},
        {"Дата операции": "2023-01-05 16:00:00", "Сумма платежа": -500, "Категория": "Путешествия", "Описание": "Поездка"},
        {"Дата операции": "2023-01-06 17:00:00", "Сумма платежа": 600, "Категория": "Доход", "Описание": "Зарплата"}
    ]
    return pd.DataFrame(data)


@pytest.fixture
def mock_logger():
    with patch('src.utils.logger_util') as mock_logger_util:
        yield mock_logger_util


@pytest.fixture
def mock_read_user_settings():
    with patch('src.utils.read_user_settings') as mock_read:
        yield mock_read


@pytest.fixture
def mock_requests_get():
    with patch('src.utils.requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def api_key():
    return "test_api_key"
