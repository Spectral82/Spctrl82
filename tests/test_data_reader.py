import unittest
from unittest.mock import patch,  Mock
import pandas as pd
from datetime import  datetime, timezone

from src.data_reader import load_transactions_from_csv, load_transactions_from_excel


class TestLoadTransactionsFromCSV(unittest.TestCase):

    @patch("src.data_reader.pd.read_csv")
    def test_load_transactions_from_csv_success(self, mock_read_csv):
        mock_df = pd.DataFrame({
            "id": [1, 2],
            "state": ["paid", "pending"],
            "date": ["2024-01-01", "2024-01-02"],
            "amount": [100.0, 200.0],
            "currency_name": ["RUB", "USD"],
            "currency_code": ["RUB", "USD"],
            "from_account": ["A", "B"],
            "to_account": ["C", "D"],
            "description": ["pay1", "pay2"],
        })
        mock_read_csv.return_value = mock_df

        result = load_transactions_from_csv("path/to/file.csv", sep=";", encoding="utf-8")

        mock_read_csv.assert_called_once_with("path/to/file.csv", sep=";", encoding="utf-8")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)

        # Проверяем, что колонка date стала datetime с UTC
        self.assertTrue(pd.api.types.is_datetime64tz_dtype(result["date"]))

        # Явная проверка tzinfo у первого валидного значения
        first_date = result["date"].dropna().iloc[0]
        self.assertIs(first_date.tzinfo, timezone.utc)

    @patch("src.data_reader.pd.read_csv")
    def test_load_transactions_from_csv_no_date_column(self, mock_read_csv):
        mock_df = pd.DataFrame({
            "id": [1],
            "state": ["paid"],
            "amount": [100.0],
        })
        mock_read_csv.return_value = mock_df

        result = load_transactions_from_csv("path/to/file.csv")

        mock_read_csv.assert_called_once()
        self.assertNotIn("date", result.columns)

    @patch("src.data_reader.pd.read_csv")
    def test_load_transactions_from_csv_invalid_date_coerced(self, mock_read_csv):
        mock_df = pd.DataFrame({
            "id": [1, 2],
            "date": ["2024-01-01", "invalid-date"],
        })
        mock_read_csv.return_value = mock_df

        result = load_transactions_from_csv("path/to/file.csv")

        mock_read_csv.assert_called_once()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("date", result.columns)
        self.assertTrue(pd.api.types.is_datetime64tz_dtype(result["date"]))

        self.assertFalse(result["date"].isna().all())
        self.assertTrue(result["date"].isna().any())


class TestLoadTransactionsFromExcel(unittest.TestCase):
    @patch("src.data_reader.pd.read_excel")
    def test_load_transactions_from_excel_success(self, mock_read_excel):
        mock_df = pd.DataFrame({
            "id": [1, 2],
            "state": ["paid", "pending"],
            "date": ["2024-01-01", "2024-01-02"],
            "amount": [100.0, 200.0],
        })
        mock_read_excel.return_value = mock_df

        result = load_transactions_from_excel("path/to/file.xlsx")

        mock_read_excel.assert_called_once_with("path/to/file.xlsx", sheet_name=0, engine="openpyxl")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)

        # Проверяем, что колонка date стала datetime с таймзоной
        self.assertTrue(pd.api.types.is_datetime64tz_dtype(result["date"]))

        # Проверяем, что timezone — UTC
        self.assertEqual(result["date"].dt.tz, timezone.utc)

    @patch("src.data_reader.pd.read_excel")
    def test_load_transactions_from_excel_no_date_column(self, mock_read_excel):
        # DataFrame без колонки date
        mock_df = pd.DataFrame({
            "id": [1],
            "state": ["paid"],
            "amount": [100.0],
        })
        mock_read_excel.return_value = mock_df

        result = load_transactions_from_excel("path/to/file.xlsx")

        mock_read_excel.assert_called_once()
        self.assertNotIn("date", result.columns)
        # Проверяем, что дата не добавилась и не является временным рядом
        self.assertFalse(pd.api.types.is_datetime64tz_dtype(result.get("date", pd.Series())))  # Проверяем, что дата не добавилась



