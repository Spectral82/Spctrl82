import pytest
from src.main import main

def base_mocks(monkeypatch, mock_inputs, transactions=None):
    input_index = 0
    def mock_input(_prompt=None):
        nonlocal input_index
        if input_index >= len(mock_inputs):
            raise RuntimeError(
                f"Неожиданный дополнительный input() после {len(mock_inputs)} ответов"
            )
        value = mock_inputs[input_index]
        input_index += 1
        return value
    monkeypatch.setattr("builtins.input", mock_input)
    monkeypatch.setattr("os.path.isfile", lambda path: True)
    captured_outputs = []
    def mock_print(*args, **kwargs):
        line = " ".join(str(a) for a in args)
        captured_outputs.append(line)
    monkeypatch.setattr("builtins.print", mock_print)
    monkeypatch.setattr(
        "src.main.read_json_transactions",
        lambda path: transactions or [
            {"id": 1, "date": "2024-06-01", "amount": 100, "currency": "RUB", "type": "test", "status": "EXECUTED"}
        ]
    )
    monkeypatch.setattr(
        "src.main.read_csv_transactions",
        lambda path: transactions or [
            {"id": 2, "date": "2024-06-02", "amount": 200, "currency": "USD", "type": "deposit", "status": "PENDING"}
        ]
    )
    monkeypatch.setattr(
        "src.main.read_xlsx_transactions",
        lambda path: transactions or [
            {"id": 3, "date": "2024-06-03", "amount": 300, "currency": "EUR", "type": "withdrawal", "status": "CANCELED"}
        ]
    )
    return captured_outputs

# Тест успешного сценария выбора JSON и "нет" на все фильтры/экспорт
def test_main_json_no_filters(monkeypatch):
    mock_inputs = ["1", "fake.json", "нет", "нет", "нет", "нет", "нет"]
    captured_outputs = base_mocks(monkeypatch, mock_inputs)
    main()
    assert any("Добро пожаловать" in line for line in captured_outputs)
    assert any("Распечатываю итоговый список транзакций" in line for line in captured_outputs)
    assert any("Экспорт отменён." in line for line in captured_outputs)

# Тест выбора CSV и экспорта в JSON
def test_main_csv_export_json(monkeypatch):
    mock_inputs = ["2", "fake.csv", "нет", "нет", "нет", "нет", "json"]
    captured_outputs = base_mocks(monkeypatch, mock_inputs)
    main()
    assert any("Добро пожаловать" in line for line in captured_outputs)
    assert any("Данные успешно сохранены в файл transactions.json" in line for line in captured_outputs)

# Тест выбора XLSX и экспорта в CSV
def test_main_xlsx_export_csv(monkeypatch):
    mock_inputs = ["3", "fake.xlsx", "нет", "нет", "нет", "нет", "csv"]
    captured_outputs = base_mocks(monkeypatch, mock_inputs)
    main()
    assert any("Добро пожаловать" in line for line in captured_outputs)
    assert any("Данные успешно сохранены в файл transactions.csv" in line for line in captured_outputs)

# Тест выбора несуществующего пункта меню
def test_main_wrong_menu(monkeypatch):
    mock_inputs = ["9"]
    input_index = 0
    def mock_input(_prompt=None):
        nonlocal input_index
        if input_index >= len(mock_inputs):
            raise RuntimeError("Неожиданный дополнительный input() после 1 ответа")
        value = mock_inputs[input_index]
        input_index += 1
        return value
    monkeypatch.setattr("builtins.input", mock_input)
    captured_outputs = []
    def mock_print(*args, **kwargs):
        line = " ".join(str(a) for a in args)
        captured_outputs.append(line)
    monkeypatch.setattr("builtins.print", mock_print)
    main()
    assert any("Неверный выбор" in line for line in captured_outputs)

# Тест если после фильтрации ничего не осталось
def test_main_empty_after_filter(monkeypatch):
    # Даем только один статус, фильтруем по другому
    mock_inputs = ["1", "fake.json", "да", "CANCELED", "нет", "нет", "нет"]
    captured_outputs = base_mocks(monkeypatch, mock_inputs, transactions=[
        {"id": 1, "date": "2024-06-01", "amount": 100, "currency": "RUB", "type": "test", "status": "EXECUTED"}
    ])
    main()
    assert any("После фильтрации не осталось транзакций для экспорта." in line for line in captured_outputs)