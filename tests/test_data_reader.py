# tests/test_data_reader.py
import unittest
from unittest.mock import patch
import pandas as pd
from src.data_reader import (
    read_csv_transactions,
    read_xlsx_transactions,
    filter_by_status,
    AVAILABLE_STATUSES
)


class TestReadCSVTransactions(unittest.TestCase):

    @patch("src.data_reader.pd.read_csv")
    def test_read_csv_success(self, mock_read_csv):
        mock_df = pd.DataFrame({
            "id": [1, 2],
            "status": ["paid", "pending"],          # важно: status, а не state
            "date": ["2024-01-01", "2024-01-02"],
            "amount": [100.0, 200.0],
            "currency_name": ["RUB", "USD"],
            "currency_code": ["RUB", "USD"],
            "from_account": ["A", "B"],
            "to_account": ["C", "D"],
            "description": ["pay1", "pay2"],
        })
        mock_read_csv.return_value = mock_df

        result = read_csv_transactions("path/to/file.csv", sep=";", encoding="utf-8")

        # Проверка вызова read_csv
        mock_read_csv.assert_called_once_with(
            "path/to/file.csv",
            sep=";",
            encoding="utf-8"
        )

        # Проверка типа результата
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        # Проверка структуры первой записи
        first = result[0]
        self.assertIn("id", first)
        self.assertEqual(first["id"], 1)
        self.assertIn("date", first)

        # Проверка, что дата стала datetime с UTC
        self.assertIsNotNone(first["date"])
        self.assertTrue(first["date"].tzinfo is not None)
        # tzname() может быть None в некоторых версиях/конфигурациях, лучше проверить tzinfo
        self.assertEqual(first["date"].tzname(), "UTC")

    @patch("src.data_reader.pd.read_csv")
    def test_read_csv_no_date_column(self, mock_read_csv):
        mock_df = pd.DataFrame({
            "id": [1, 2],
            "status": ["pending", "completed"],
            "amount": [100.0, 200.0],
        })
        mock_read_csv.return_value = mock_df

        result = read_csv_transactions("path/to/file.csv")

        mock_read_csv.assert_called_once()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertNotIn("date", result[0])  # даты нет, потому что колонки не было


class TestFilterByStatus(unittest.TestCase):

    def test_filter_by_status_valid(self):
        transactions = [
            {"id": 1, "status": "pending"},
            {"id": 2, "status": "completed"},
            {"id": 3, "status": "failed"},
        ]
        filtered = filter_by_status(transactions, "pending")
        self.assertEqual([t["id"] for t in filtered], [1])

    def test_filter_by_status_invalid(self):
        transactions = [
            {"id": 1, "status": "pending"},
            {"id": 2, "status": "completed"},
        ]
        filtered = filter_by_status(transactions, "unknown_status")
        self.assertEqual(filtered, [])

    def test_available_statuses_definition(self):
        # Можно дополнительно проверить, что статусы определены и имеют ожидаемый вид
        self.assertIsInstance(AVAILABLE_STATUSES, list)
        self.assertIn("pending", AVAILABLE_STATUSES)

    @patch("src.data_reader.pd.read_csv")
    def test_load_transactions_from_csv_invalid_dates(self, mock_read_csv):
        """
        Тестирование загрузки транзакций из CSV-файла с невалидными датами.
        В этом тесте проверяется, что функция корректно обрабатывает даты,
        которые не могут быть конвертированы в формат datetime.
        """
        mock_df = pd.DataFrame({
            "id": [1, 2, 3],
            "date": ["2024-01-01", "not-a-date", None],
        })
        mock_read_csv.return_value = mock_df

        result = read_csv_transactions("path/to/file.csv")

        self.assertEqual(len(result), 3)
        valid_date = result[0]["date"]
        invalid_date_1 = result[1]["date"]
        invalid_date_2 = result[2]["date"]

        # Валидная дата должна быть datetime с UTC
        self.assertIsNotNone(valid_date)
        self.assertTrue(valid_date.tzinfo is not None)

        # Невалидные даты должны стать NaT (в pandas это pd.NaT, в словаре это будет NaT,
        # но при to_dict(orient="records") NaT превращается в pd.NaT, который в JSON-подобном
        # представлении часто выглядит как None или NaT. Важно понимать поведение.)
        self.assertTrue(pd.isna(invalid_date_1))
        self.assertTrue(pd.isna(invalid_date_2))


class TestLoadTransactionsFromExcel(unittest.TestCase):

    @patch("src.data_reader.pd.read_excel")
    def test_load_transactions_from_excel_success(self, mock_read_excel):
        """
        Тестирование успешной загрузки транзакций из Excel-файла.
        В этом тесте проверяется, что функция загружает данные корректно,
        возвращает список словарей и обрабатывает даты.
        """
        mock_df = pd.DataFrame({
            "id": [10, 20],
            "date": ["2024-03-01", "2024-03-02"],
            "amount": [500.0, 600.0],
        })
        mock_read_excel.return_value = mock_df

        result = read_xlsx_transactions("path/to/file.xlsx", sheet_name="Sheet1")

        mock_read_excel.assert_called_once_with(
            "path/to/file.xlsx",
            sheet_name="Sheet1",
            engine="openpyxl"
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("date", result[0])
        self.assertTrue(result[0]["date"].tzinfo is not None)

    @patch("src.data_reader.pd.read_excel")
    def test_load_transactions_from_excel_no_date_column(self, mock_read_excel):
        """
        Тестирование загрузки транзакций из Excel-файла без колонки 'date'.
        В этом тесте проверяется, что функция не падает и возвращает данные,
        если в Excel-файле отсутствует колонка с датами.
        """
        # DataFrame без колонки date
        mock_df = pd.DataFrame({
            "id": [1],
            "state": ["paid"],
            "amount": [100.0],
        })
        mock_read_excel.return_value = mock_df

        result = read_xlsx_transactions("path/to/file.xlsx")

        mock_read_excel.assert_called_once()
        # Проверяем, что ключа "date" нет в первой записи
        self.assertNotIn("date", result[0])

        # Дополнительно можно проверить количество записей
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["state"], "paid")
        self.assertEqual(result[0]["amount"], 100.0)