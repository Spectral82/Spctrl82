import functools
import sys
from datetime import datetime
from typing import Any, Callable, Optional


def log(filename: Optional[str] = None) -> Callable[[Callable], Callable]:
    """
    Декоратор для логирования вызова функций: время, имя, аргументы, результат или ошибка.

    Args:
        filename: путь к файлу для записи логов. Если None — вывод в консоль.

    Returns:
        Декоратор, оборачивающий функцию логированием.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Фиксируем время начала выполнения
            start_time = datetime.now()

            # Подготавливаем представление аргументов
            args_repr = [repr(arg) for arg in args]
            kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
            all_args_repr = ", ".join(args_repr + kwargs_repr)

            # Формируем базовую запись о вызове функции
            log_message = f"[{start_time.isoformat()}] {func.__name__} called with ({all_args_repr})\n"

            try:
                # Выполняем функцию
                result = func(*args, **kwargs)

                # Логируем успешный результат
                end_time = datetime.now()
                log_message += f"[{end_time.isoformat()}] {func.__name__} ok\n"

                _write_log(log_message, filename)
                return result

            except Exception as e:
                # Логируем ошибку
                end_time = datetime.now()
                error_type = type(e).__name__
                inputs_repr = f"Inputs: ({', '.join(args_repr)}, {dict(kwargs)})"
                log_message += f"[{end_time.isoformat()}] " f"{func.__name__} error: {error_type}. {inputs_repr}\n"

                _write_log(log_message, filename)
                raise  # Перебрасываем исключение дальше

        return wrapper

    return decorator


def _write_log(message: str, filename: Optional[str]) -> None:
    """
    Записывает лог-сообщение в файл или в консоль.

    Args:
        message: текст сообщения для логирования.
        filename: путь к файлу. Если None, вывод в stdout.
    """
    if filename:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(message)
    else:
        sys.stdout.write(message)
