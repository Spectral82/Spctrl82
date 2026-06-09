import pytest
from src.decorators import log, _write_log

class TestWriteLog:
    """Тесты для функции _write_log"""

    def test_write_to_stdout(self, capsys):
        """Тест записи в консоль (stdout)"""
        message = "Test log message\n"
        _write_log(message, None)
        captured = capsys.readouterr()
        assert captured.out == message

    def test_write_to_file(self, tmp_path):
        """Тест записи в файл"""
        test_file = tmp_path / "test_log.txt"
        message = "Test file log message\n"

        _write_log(message, str(test_file))

        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert content == message

    def test_append_to_existing_file(self, tmp_path):
        """Тест дописывания в существующий файл"""
        test_file = tmp_path / "append_log.txt"

        # Создаём файл с начальным содержимым
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("First line\n")

        message1 = "Second line\n"
        message2 = "Third line\n"

        _write_log(message1, str(test_file))
        _write_log(message2, str(test_file))

        with open(test_file, "r", encoding="utf-8") as f:
            content = f.readlines()

        expected = ["First line\n", "Second line\n", "Third line\n"]
        assert content == expected



class TestLogDecorator:
    """Тесты для декоратора log"""

    @pytest.fixture
    def setup_test_function(self):
        """Фикстура для создания тестовой функции"""
        @log()
        def test_func(x, y=10):
            return x * y

        return test_func

    def test_successful_execution_stdout(self, setup_test_function, capsys):
        """Тест успешного выполнения функции с логированием в консоль"""
        result = setup_test_function(5, y=3)
        assert result == 15

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')

        # Проверяем формат логов
        assert len(lines) == 2
        assert "test_func called with (5, y=3)" in lines[0]
        assert "test_func ok" in lines[1]

    def test_successful_execution_file(self, tmp_path):
        """Тест успешного выполнения с записью в файл"""
        log_file = tmp_path / "function_log.txt"

        @log(str(log_file))
        def add(a, b):
            return a + b

        result = add(10, b=20)
        assert result == 30

        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 2
        assert "add called with (10, b=20)" in lines[0]
        assert "add ok" in lines[1]

    def test_function_with_no_args(self, capsys):
        """Тест функции без аргументов"""
        @log()
        def get_pi():
            return 3.14159

        result = get_pi()
        assert abs(result - 3.14159) < 1e-5

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        assert "get_pi called with ()" in lines[0]
        assert "get_pi ok" in lines[1]

    def test_function_with_complex_args(self, capsys):
        @log(filename=None)
        def process_data(data, config=None, verbose=False):
            return f"Processing {len(data)} items"

        result = process_data([1, 2, 3, 4, 5], config={'mode': 'fast'}, verbose=True)

        captured = capsys.readouterr()
        log_output = captured.out

        # Проверяем, что в логе есть ключевые части
        assert "process_data called with" in log_output
        assert "[1, 2, 3, 4, 5]" in log_output
        assert "config={'mode': 'fast'}" in log_output
        assert "verbose=True" in log_output
        assert "ok" in log_output  # проверяем успешный результат

    def test_exception_handling(self, capsys):
        @log()
        def divide(a, b):
            return a / b

        with pytest.raises(ZeroDivisionError):
            divide(10, b=0)

        captured = capsys.readouterr()
        output = captured.out

        assert "divide called with (10, b=0)" in output
        assert "ZeroDivisionError" in output
        # Если нужно проверить именно формат Inputs:
        assert "Inputs: (10, {'b': 0})" in output or "Inputs: (10, b=0)" in output

    def test_invalid_log_path(self, capsys):
        """Тест с некорректным путём для логирования"""
        with pytest.raises(OSError):  # Или другой подходящий тип исключения
            @log("/invalid/path/that/does/not/exist.log")
            def test_func():
                pass

            test_func()

    def test_large_arguments(self, capsys):
        """Тест с большими аргументами"""
        @log()
        def handle_large_data(data):
            return len(data)

        large_list = list(range(1000))
        result = handle_large_data(large_list)
        assert result == 1000

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        assert "handle_large_data called with" in lines[0]
        assert "handle_large_data ok" in lines[1]