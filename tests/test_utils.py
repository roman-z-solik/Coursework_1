from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.utils import (
    cards_info,
    currency_rates,
    expenses_by_category,
    income_by_category,
    read_info,
    read_user_settings,
    sorted_by_date,
    top_transactions,
    total_expenses,
    total_income,
)


@patch("pandas.read_excel")
@patch("src.utils.logger_util")
def test_read_info_success(mock_logger, mock_read_excel):
    test_data = {"Статус": ["OK", "OK", "ERROR"], "Сумма": [100, 200, 300]}
    mock_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = mock_df
    result = read_info("test_file.xlsx")
    expected_data = {"Статус": ["OK", "OK"], "Сумма": [100, 200]}
    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(result, expected_df)
    mock_logger.info.assert_any_call("Запуск функции чтения данных из файла")
    mock_logger.info.assert_any_call("Файл test_file.xlsx корректно прочитан")


@patch("src.utils.logger_util")
def test_read_info_file_not_found(mock_logger):
    with patch("pandas.read_excel", side_effect=FileNotFoundError):
        result = read_info("non_existent_file.xlsx")
        assert result is None
        mock_logger.error.assert_called_once_with("Файл non_existent_file.xlsx не найден")


def test_read_user_settings_success():
    assert read_user_settings("user_stocks") == ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]


def test_read_user_settings_invalid_key(tmpdir):
    settings_file = tmpdir.join("test_settings.json")
    settings_file.write('{"theme": "dark", "language": "ru"}')
    with pytest.raises(KeyError):
        read_user_settings(str(settings_file))


def test_read_user_settings_file_not_found() -> None:
    with pytest.raises(KeyError):
        read_user_settings("/path/to/nonexistent/file")


def test_read_user_settings_json_decode_error(tmpdir):
    settings_file = tmpdir.join("invalid_test_settings.json")
    settings_file.write("{ invalid json }")
    with pytest.raises(KeyError):
        read_user_settings(str(settings_file))


def test_read_user_settings_permission_error(monkeypatch):
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: _raise(PermissionError))
    result = read_user_settings("/some/path")
    assert result is None


def _raise(exception_class):
    raise exception_class()


def test_sorted_by_date_month(sample_df):
    """Тест успешной фильтрации за месяц"""
    expected_columns = ["Дата операции", "Описание"]
    result = sorted_by_date(sample_df, "2023-01-31 23:59:59", "M")
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == expected_columns
    assert len(result) > 0


def test_sorted_by_date_year(sample_df):
    """Тест успешной фильтрации за год"""
    result = sorted_by_date(sample_df, "2023-12-31 23:59:59", "Y")
    assert isinstance(result, pd.DataFrame)
    assert len(result) >= len(sample_df)


def test_sorted_by_date_all(sample_df):
    """Тест успешной фильтрации всех операций"""
    result = sorted_by_date(sample_df, "2023-12-31 23:59:59", "All")
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_df)


def test_sorted_by_date_empty_df() -> None:
    """Тест пустой таблицы"""
    empty_df = pd.DataFrame(columns=["Дата операции"])
    result = sorted_by_date(empty_df, "2023-01-31 23:59:59", "M")
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_sorted_by_date_incorrect_date_format(sample_df):
    """Тест неправильного формата даты"""
    with pytest.raises(ValueError):
        sorted_by_date(sample_df, "incorrect-date-format", "M")


def test_sorted_by_date_wrong_diapason_value(sample_df):
    """Тест с неизвестным значением временного диапазона"""
    with pytest.raises(Exception):
        sorted_by_date(sample_df, "2023-01-31 23:59:59", "InvalidDiapason")


def test_cards_info(mock_df):
    expected_result = [
        {"last_digits": "1234", "total_spent": 300.0, "cashback": 3.0},
        {"last_digits": "5678", "total_spent": 700.0, "cashback": 7.0},
    ]
    result = cards_info(mock_df)
    assert result == expected_result


def test_cards_info_with_no_negative_payments():
    df = pd.DataFrame([{"Номер карты": "12345678****1234", "Сумма платежа": 100}])
    result = cards_info(df)
    assert result == []


def test_cards_info_single_card() -> None:
    df = pd.DataFrame(
        [{"Номер карты": "*1234", "Сумма платежа": -100.0}, {"Номер карты": "*1234", "Сумма платежа": -200.0}]
    )
    expected_result = [{"last_digits": "1234", "total_spent": 300.0, "cashback": 3.0}]
    result = cards_info(df)
    assert result == expected_result


def test_cards_info_large_sums() -> None:
    df = pd.DataFrame(
        [{"Номер карты": "*1234", "Сумма платежа": -10000.0}, {"Номер карты": "*5678", "Сумма платежа": -20000.0}]
    )
    expected_result = [
        {"last_digits": "1234", "total_spent": 10000.0, "cashback": 100.0},
        {"last_digits": "5678", "total_spent": 20000.0, "cashback": 200.0},
    ]
    result = cards_info(df)
    assert result == expected_result


def test_top_transactions(mock_df1):
    result = top_transactions(mock_df1)
    expected_result = [
        {"date": "2023-01-05", "amount": 500, "category": "Путешествия", "description": "Поездка"},
        {"date": "2023-01-04", "amount": 400, "category": "Одежда", "description": "Новая куртка"},
        {"date": "2023-01-03", "amount": 300, "category": "Транспорт", "description": "Такси"},
        {"date": "2023-01-02", "amount": 200, "category": "Развлечения", "description": "Кино"},
        {"date": "2023-01-01", "amount": 100, "category": "Еда", "description": "Покупка продуктов"},
    ]
    assert result == expected_result


def test_top_transactions_less_than_5_items():
    small_df = pd.DataFrame(
        {
            "Дата операции": ["2023-01-01 12:00:00"],
            "Сумма платежа": [-100],
            "Категория": ["Еда"],
            "Описание": ["Покупка продуктов"],
        }
    )
    result = top_transactions(small_df)
    expected_result = [{"date": "2023-01-01", "amount": 100, "category": "Еда", "description": "Покупка продуктов"}]
    assert result == expected_result


def test_top_transactions_no_expenditures() -> None:
    no_expenses_df = pd.DataFrame(
        {
            "Дата операции": ["2023-01-01 12:00:00"],
            "Сумма платежа": [100],  # Доход
            "Категория": ["Доход"],
            "Описание": ["Зарплата"],
        }
    )
    result = top_transactions(no_expenses_df)
    assert result == []


def test_currency_rates_request_exception(mock_logger, mock_read_user_settings, mock_requests_get):
    from requests.exceptions import RequestException

    mock_read_user_settings.return_value = ["USD"]
    mock_requests_get.side_effect = RequestException("Network error")
    result = currency_rates()
    assert "Ошибка получения курса валют" in result
    mock_logger.error.assert_called_with(
        f"Ошибка получения курса валют. Код ошибки: {RequestException('Network error')}"
    )


def test_currency_rates_keyerror_or_typeerror(mock_logger, mock_read_user_settings, mock_requests_get):
    invalid_data = {"InvalidKey": {}}
    mock_read_user_settings.return_value = ["USD"]
    response_mock = MagicMock()
    response_mock.json.return_value = invalid_data
    mock_requests_get.return_value = response_mock
    result = currency_rates()
    assert "Ошибка получения курса валют. Код ошибки 'Valute'" in result


def test_total_expenses_positive_and_negative_values(mock_logger):
    data = {"Сумма платежа": [100, -50, -20, 30]}
    df = pd.DataFrame(data)
    result = total_expenses(df)
    assert result == 70


def test_total_expenses_all_positive(mock_logger):
    data = {"Сумма платежа": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = total_expenses(df)
    assert result == 0


def test_total_expenses_all_negative(mock_logger):
    data = {"Сумма платежа": [-10, -20, -30]}
    df = pd.DataFrame(data)
    result = total_expenses(df)
    assert result == 60


def test_total_expenses_with_nan_values(mock_logger):
    data = {"Сумма платежа": [100, None, -50, float("nan")]}
    df = pd.DataFrame(data)
    result = total_expenses(df)
    assert result == 50


def test_logging_calls_expenses(mock_logger):
    data = {"Сумма платежа": [100, -50]}
    df = pd.DataFrame(data)
    total_expenses(df)
    mock_logger.info.assert_any_call("Запуск функции подсчета суммы всех расходов за период")
    mock_logger.info.assert_any_call("Подсчет суммы всех расходов за период успешен")


def test_total_income_positive_and_negative_values(mock_logger):
    data = {"Сумма платежа": [100, -50, 20, 30]}
    df = pd.DataFrame(data)
    result = total_income(df)
    assert result == 150


def test_total_income_all_negative(mock_logger):
    data = {"Сумма платежа": [-10, -20, -30]}
    df = pd.DataFrame(data)
    result = total_income(df)
    assert result == 0


def test_total_income_all_positive(mock_logger):
    data = {"Сумма платежа": [10, 20, 30]}
    df = pd.DataFrame(data)
    result = total_income(df)
    assert result == 60


def test_total_income_with_nan_values(mock_logger):
    data = {"Сумма платежа": [100, None, -50, float("nan")]}
    df = pd.DataFrame(data)
    result = total_income(df)
    assert result == 100


def test_logging_calls_income(mock_logger):
    data = {"Сумма платежа": [100, -50]}
    df = pd.DataFrame(data)
    total_income(df)
    mock_logger.info.assert_any_call("Запуск функции подсчета суммы всех поступлений за период")
    mock_logger.info.assert_any_call("Подсчет суммы всех поступлений за период успешен")


def test_expenses_with_no_negative_values(mock_logger):
    data = {"Сумма платежа": [100, 200], "Категория": ["A", "B"]}
    df = pd.DataFrame(data)
    result = expenses_by_category(df)
    assert len(result) == 1
    assert result[0]["category"] == "Остальное"
    assert result[0]["amount"] == 0.00


def test_logging_calls_expenses_by_category(mock_logger):
    data = {"Сумма платежа": [-100], "Категория": ["Test"]}
    df = pd.DataFrame(data)
    expenses_by_category(df)


def test_income_by_category_basic(mock_logger):
    data = {
        "Сумма платежа": [100, 50, -200, 300],
        "Категория": ["Категория1", "Категория2", "Категория1", "Категория3"],
    }
    df = pd.DataFrame(data)
    result = income_by_category(df)
    expected = [
        {"category": "Категория3", "amount": 300.00},
        {"category": "Категория1", "amount": 100.00},
        {"category": "Категория2", "amount": 50.00},
    ]
    assert result[:3] == expected


def test_income_with_no_positive_values(mock_logger):
    data = {"Сумма платежа": [-100, -200], "Категория": ["A", "B"]}
    df = pd.DataFrame(data)
    result = income_by_category(df)
    assert len(result) == 1
    assert result[0]["category"] == "Остальное"
    assert result[0]["amount"] == 0.00


def test_income_with_nan_and_zero(mock_logger):
    data = {"Сумма платежа": [float("nan"), 50, 0], "Категория": ["X", "Y", "Z"]}
    df = pd.DataFrame(data)
    result = income_by_category(df)
    assert any(item["category"] == "Y" and item["amount"] == 50.00 for item in result)


def test_logging_calls(mock_logger):
    data = {"Сумма платежа": [100], "Категория": ["Test"]}
    df = pd.DataFrame(data)
    income_by_category(df)
