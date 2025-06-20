from unittest.mock import patch

from src.config import root_path
from src.reports import spending_by_category, writing_report_to_file, writing_report_to_file_by_user


def test_spending_by_category_with_date(mock_transactions):
    result = spending_by_category(mock_transactions, "Книги", "2023-04-01 00:00:00")
    assert result["Книги"] == -4500


def test_spending_by_category_no_results(mock_transactions):
    result = spending_by_category(mock_transactions, "Техника", "2023-04-01 00:00:00")
    assert result.empty


@patch("pandas.DataFrame.to_excel")
def test_writing_report_to_file_decorator(mock_to_excel, mock_transactions):
    @writing_report_to_file
    def test_func():
        return mock_transactions

    result = test_func()
    mock_to_excel.assert_called_once_with(root_path / "report.xlsx")
    assert result.equals(mock_transactions)


@patch("pandas.DataFrame.to_excel", side_effect=Exception("Test error"))
def test_writing_report_to_file_error(mock_to_excel, mock_transactions, caplog):
    @writing_report_to_file
    def test_func():
        return mock_transactions

    result = test_func()
    assert "Test error" in caplog.text
    assert result is None


# Тесты декоратора writing_report_to_file_by_user
@patch("pandas.DataFrame.to_excel")
def test_writing_report_to_file_by_user_decorator(mock_to_excel, mock_transactions):
    @writing_report_to_file_by_user("custom_report.xlsx")
    def test_func():
        return mock_transactions

    result = test_func()
    mock_to_excel.assert_called_once_with(root_path / "custom_report.xlsx")
    assert result.equals(mock_transactions)


@patch("pandas.DataFrame.to_excel", side_effect=Exception("Test error"))
def test_writing_report_to_file_by_user_error(mock_to_excel, mock_transactions, caplog):
    @writing_report_to_file_by_user("custom_report.xlsx")
    def test_func():
        return mock_transactions

    result = test_func()
    assert "Test error" in caplog.text
    assert result is None


def test_spending_by_category_invalid_date_format(mock_transactions, caplog):
    result = spending_by_category(mock_transactions, "Книги", "invalid-date")
    assert "Ошибка функции" in caplog.text
    assert result is None
