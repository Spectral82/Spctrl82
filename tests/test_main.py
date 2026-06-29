# tests/test_main.py
import pytest
from src.main import main


def test_main_runs_without_errors(monkeypatch):
    # Заготавливаем ответы для input по порядку:
    # 1 -> JSON, "нет" (не фильтровать), "нет" (не сортировать)
    mock_inputs = ["1", "нет", "нет"]

    # Генератор, который будет отдавать эти ответы по очереди
    def input_generator():
        for answer in mock_inputs:
            yield answer

    # Подменяем встроенную функцию input
    monkeypatch.setattr('builtins.input', lambda _: next(input_generator()))

    captured_outputs = []

    def mock_print(*args, **kwargs):
        # Собираем всё, что печатается, чтобы можно было проверить вывод при необходимости
        captured_outputs.append(" ".join(str(a) for a in args))

    # Подменяем встроенную функцию print
    monkeypatch.setattr('builtins.print', mock_print)

    # Запускаем основную функцию
    main()

    # Проверки
    # Можно дополнительно проверить, что вывод содержит приветствие:
    assert any("Добро пожаловать в программу работы с банковскими транзакциями" in line for line in captured_outputs)

    if __name__ == "__main__":
        main()