from unittest.mock import patch

import pytest

from src import main


@patch("src.main.read_json_transactions")
@patch("src.main.sort_transactions")
def test_main_choice_1_prints_report(mock_sort, mock_read_json, capsys):
    # Arrange: данные, которые вернёт mocked-функция
    mock_read_json.return_value = [
        {
            "date": "2019-12-08T10:00:00",
            "description": "Открытие вклада",
            "account": "1111222233334321",
            "amount": 40542,
            "currency": "руб.",
        },
        {
            "date": "2019-11-12T11:00:00",
            "description": "Перевод с карты на карту",
            "account": "7771270000003727",
            "amount": 130,
            "currency": "USD",
        },
    ]
    mock_sort.return_value = mock_read_json.return_value

    with patch("builtins.input", return_value="1"):
        main.main()

    captured = capsys.readouterr()
    output = captured.out

    assert "Привет! Добро пожаловать в программу работы с банковскими транзакциями." in output
    assert "Выберите необходимый пункт меню:" in output
    assert "Всего банковских операций в выборке: 2" in output
    assert "Открытие вклада" in output
    assert "Перевод с карты на карту" in output


@patch("src.main.read_csv_transactions")
@patch("src.main.sort_transactions")
def test_main_choice_2_calls_csv_reader(mock_sort, mock_read_csv, capsys):
    mock_read_csv.return_value = []
    mock_sort.return_value = []

    with patch("builtins.input", return_value="2"):
        main.main()

    captured = capsys.readouterr()
    output = captured.out

    assert mock_read_csv.called

    assert "Транзакции не найдены." in output or "Всего банковских операций в выборке: 0" in output


@patch("src.main.read_xlsx_transactions")
@patch("src.main.sort_transactions")
def test_main_choice_3_calls_xlsx_reader(mock_sort, mock_read_xlsx, capsys):
    mock_read_xlsx.return_value = [
        {
            "date": "2020-01-01T00:00:00",
            "description": "Платеж",
            "account": "9999888877776666",
            "amount": 500,
            "currency": "руб.",
        }
    ]
    mock_sort.return_value = mock_read_xlsx.return_value

    with patch("builtins.input", return_value="3"):
        main.main()

    captured = capsys.readouterr()
    output = captured.out

    assert mock_read_xlsx.called
    assert "Всего банковских операций в выборке: 1" in output
    assert "Платеж" in output


def test_main_invalid_choice_prints_error(capsys):
    with patch("builtins.input", return_value="99"):
        main.main()

    captured = capsys.readouterr()
    assert "Неверный выбор." in captured.out


@patch("logging.Logger.info")
def test_main_logs_startup(mock_logger_info):
    with patch("src.main.read_json_transactions", return_value=[]), patch(
        "src.main.sort_transactions", return_value=[]
    ):
        with patch("builtins.input", return_value="1"):
            main.main()

    mock_logger_info.assert_called_once_with("Запуск приложения")
