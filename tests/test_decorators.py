import pytest

from src.decorators import _write_log, log


class TestWriteLog:
    """
    Набор тестов для проверки работы функции _write_log.

    Тестируются следующие сценарии:
    - запись сообщения в стандартный поток вывода (stdout);
    - запись сообщения в файл;
    - дописывание сообщений в существующий файл (проверка режима добавления).
    """

    def test_write_to_stdout(self, capsys):
        """
        Проверяет, что функция _write_log корректно записывает сообщение в stdout.

        Шаги теста:
        1. Формируется тестовое сообщение с переводом строки.
        2. Вызывается _write_log с указанием None в качестве пути к файлу (режим вывода в консоль).
        3. С помощью capsys считывается содержимое stdout.
        4. Проверяется, что вывод совпадает с ожидаемым сообщением.

        :param capsys: фикстура pytest для перехвата stdout/stderr.
        """
        message = "Test log message\n"
        _write_log(message, None)
        captured = capsys.readouterr()
        assert captured.out == message

    def test_write_to_file(self, tmp_path):
        """
        Проверяет, что функция _write_log записывает сообщение в указанный файл.

        Шаги теста:
        1. Создаётся временный файл в директории tmp_path.
        2. Формируется тестовое сообщение.
        3. Вызывается _write_log с путём к файлу.
        4. Содержимое файла читается и сравнивается с ожидаемым сообщением.

        :param tmp_path: фикстура pytest, предоставляющая временную директорию для тестов.
        """
        test_file = tmp_path / "test_log.txt"
        message = "Test file log message\n"

        _write_log(message, str(test_file))

        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert content == message

    def test_append_to_existing_file(self, tmp_path):
        """
        Проверяет, что _write_log дописывает сообщения в уже существующий файл,
        не перезаписывая его содержимое.

        Шаги теста:
        1. Создаётся файл с начальным содержимым.
        2. Дважды вызывается _write_log для добавления новых строк.
        3. Проверяется, что итоговый список строк соответствует ожидаемой последовательности.

        :param tmp_path: фикстура pytest, предоставляющая временную директорию для тестов.
        """
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
    """
    Набор тестов для проверки работы декоратора log.

    Проверяются следующие сценарии:
    - логирование успешного вызова функции в stdout;
    - логирование в файл при указании пути;
    - корректная обработка функций без аргументов;
    - отображение сложных аргументов (списки, словари, именованные параметры);
    - обработка исключений и логирование ошибки.
    """

    @pytest.fixture
    def setup_test_function(self):
        """
        Фикстура для подготовки тестовой функции, обёрнутой декоратором log.

        Создаёт функцию test_func(x, y=10), декорированную @log(),
        и возвращает её для использования в тестах.

        :return: декорированная тестовая функция.
        """

        @log()
        def test_func(x, y=10):
            return x * y

        return test_func

    def test_successful_execution_stdout(self, setup_test_function, capsys):
        """
        Проверяет логирование успешного выполнения функции в stdout.

        Шаги теста:
        1. Вызывается тестовая функция с аргументами 5 и y=3.
        2. Проверяется возвращаемое значение.
        3. Считывается вывод в stdout и разбивается на строки.
        4. Проверяется формат логов: строка вызова и строка об успешном завершении.

        :param setup_test_function: фикстура, возвращающая декорированную функцию.
        :param capsys: фикстура pytest для перехвата stdout/stderr.
        """
        result = setup_test_function(5, y=3)
        assert result == 15

        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")

        # Проверяем формат логов
        assert len(lines) == 2
        assert "test_func called with (5, y=3)" in lines[0]
        assert "test_func ok" in lines[1]

    def test_successful_execution_file(self, tmp_path):
        """
        Проверяет логирование успешного выполнения функции с записью в файл.

        Шаги теста:
        1. Определяется путь к временному файлу.
        2. Создаётся функция add(a, b), декорированная @log(путь_к_файлу).
        3. Функция вызывается, проверяется результат.
        4. Содержимое лог-файла читается и проверяется на соответствие ожидаемому формату.

        :param tmp_path: фикстура pytest, предоставляющая временную директорию для тестов.
        """
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
        """
        Проверяет корректное логирование вызова функции без аргументов.

        Шаги теста:
        1. Создаётся функция get_pi() без параметров, декорированная @log().
        2. Функция вызывается, результат проверяется.
        3. В stdout проверяется наличие строки вызова с пустыми скобками и строки об успехе.

        :param capsys: фикстура pytest для перехвата stdout/stderr.
        """

        @log()
        def get_pi():
            return 3.14159

        result = get_pi()
        assert abs(result - 3.14159) < 1e-5

        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert "get_pi called with ()" in lines[0]
        assert "get_pi ok" in lines[1]

    def test_function_with_complex_args(self, capsys):
        """
        Проверяет отображение в логах сложных аргументов: списков, словарей, булевых значений.

        Шаги теста:
        1. Создаётся функция process_data(data, config=None, verbose=False), декорированная @log.
        2. Функция вызывается с непустым списком, словарем и флагом verbose=True.
        3. Проверяется наличие в логе ключевых частей: названия аргументов и их значений.
        4. Проверяется строка об успешном выполнении.

        :param capsys: фикстура pytest для перехвата stdout/stderr.
        """

        @log(filename=None)
        def process_data(data, config=None, verbose=False):
            # Используем параметры для демонстрации их использования
            if verbose:
                print(f"Verbose mode is on. Config: {config}")
            return f"Processing {len(data)} items"

        result = process_data([1, 2, 3, 4, 5], config={"mode": "fast"}, verbose=True)

        captured = capsys.readouterr()
        log_output = captured.out

        # Проверяем, что в логе есть ключевые части
        assert "process_data called with" in log_output
        assert "[1, 2, 3, 4, 5]" in log_output
        assert "config={'mode': 'fast'}" in log_output
        assert "verbose=True" in log_output
        assert "ok" in log_output  # проверяем успешный результат

    def test_exception_handling(self, capsys):
        """
        Проверяет поведение декоратора log при возникновении исключения в декорируемой функции.

        Шаги теста:
        1. Создаётся функция divide(a, b), которая выполняет деление.
        2. Ожидается исключение ZeroDivisionError при вызове divide(10, b=0).
        3. После перехвата исключения проверяется вывод в stdout:
           ожидается, что декоратор залогирует факт ошибки.

        :param capsys: фикстура pytest для перехвата stdout/stderr.
        """

        @log()
        def divide(a, b):
            return a / b

        with pytest.raises(ZeroDivisionError):
            divide(10, b=0)

        captured = capsys.readouterr()
        output = captured.out

        assert "divide called with (10, b=0)" in output
        assert "divide error: ZeroDivisionError. Inputs: (10, {'b': 0})" in output
