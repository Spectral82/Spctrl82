import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from src.data_reader import (
    AVAILABLE_STATUSES,
    filter_by_status,
    read_csv_transactions,
    read_xlsx_transactions,
)


class TestReadCSVTransactions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        pass  # Можно добавить удаление файлов, если потребуется

    def test_read_csv_success(self):
        csv_content = """id;date;amount;status\n1;2024-06-01 10:00:00;1500.50;EXECUTED\n2;2024-06-02 11:30:00;2000.00;CANCELED\n3;invalid-date;3000.75;PENDING\n"""
        file_path = os.path.join(self.temp_dir, "transactions.csv")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
        result = read_csv_transactions(file_path)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["status"], "EXECUTED")
        self.assertTrue(result[0]["date"].tzinfo is not None)
        self.assertEqual(result[0]["date"].tzname(), "UTC")
        self.assertTrue(pd.isna(result[2]["date"]))

    def test_read_csv_no_date_column(self):
        csv_content = "id;amount;status\n1;100;EXECUTED"
        file_path = os.path.join(self.temp_dir, "no_date.csv")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
        result = read_csv_transactions(file_path)
        self.assertEqual(len(result), 1)
        self.assertNotIn("date", result[0])

    @patch("src.data_reader.pd.read_csv")
    def test_read_csv_uses_pandas(self, mock_read_csv):
        mock_df = pd.DataFrame([{"id": 1, "date": "2024-01-01", "status": "EXECUTED"}])
        mock_read_csv.return_value = mock_df
        read_csv_transactions("dummy.csv", sep=";", encoding="utf-8")
        mock_read_csv.assert_called_once_with("dummy.csv", sep=";", encoding="utf-8")


class TestReadXLSXTransactions(unittest.TestCase):
    @patch("src.data_reader.pd.read_excel")
    def test_read_xlsx_success(self, mock_read_excel):
        mock_df = pd.DataFrame(
            [
                {"id": 1, "date": "2023-01-01", "status": "EXECUTED"},
                {"id": 2, "date": "bad-date", "status": "PENDING"},
            ]
        )
        mock_read_excel.return_value = mock_df
        result = read_xlsx_transactions("dummy.xlsx")
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]["date"].tzinfo is not None)
        self.assertTrue(pd.isna(result[1]["date"]))


class TestFilterByStatus(unittest.TestCase):
    def setUp(self):
        self.transactions = [
            {"id": 1, "status": "EXECUTED"},
            {"id": 2, "status": " CANCELED ", "amount": 100},
            {"id": 3, "status": "pending"},
            {"id": 4, "amount": 200},  # нет статуса
        ]

    def test_filter_by_status_executed(self):
        filtered = filter_by_status(self.transactions, "executed")
        self.assertEqual([t["id"] for t in filtered], [1])

    def test_filter_by_status_canceled_with_spaces(self):
        filtered = filter_by_status(self.transactions, "  canceled  ")
        self.assertEqual([t["id"] for t in filtered], [2])

    def test_filter_by_status_pending_lowercase(self):
        filtered = filter_by_status(self.transactions, "pending")
        self.assertEqual([t["id"] for t in filtered], [3])

    def test_filter_by_status_invalid(self):
        filtered = filter_by_status(self.transactions, "UNKNOWN")
        self.assertEqual(filtered, [])

    def test_filter_handles_missing_status(self):
        filtered = filter_by_status(self.transactions, "PENDING")
        ids = [t["id"] for t in filtered]
        self.assertNotIn(4, ids)

    def test_available_statuses(self):
        expected = {"EXECUTED", "CANCELED", "PENDING"}
        self.assertEqual(set(AVAILABLE_STATUSES), expected)


if __name__ == "__main__":
    unittest.main()
