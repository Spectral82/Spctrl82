# main.py
import logging
from typing import List, Dict, Any, Optional, Tuple

# Настройка корневого логгера
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

def main() -> None:
    """Точка входа в приложение: интерактивное меню для работы с транзакциями."""
    logger.info("Запуск приложения")
    print("Добро пожаловать в программу работы с банковскими транзакциями")

    choice = input("Выберите формат данных:\n1 — JSON\n2 — CSV\n3 — XLSX\nВаш выбор: ")

    if choice == "1":
        # логика для JSON
        ...
    elif choice == "2":
        # логика для CSV
        ...
    elif choice == "3":
        # логика для XLSX
        ...
    else:
        print("Неверный выбор. Пожалуйста, введите 1, 2 или 3.")


if __name__ == "__main__":
    main()

# Импорты модулей проекта (подстройте пути под свою структуру)
from src.utils import read_transactions
from src.data_reader import (
    AVAILABLE_STATUSES,
    filter_by_status,
    read_csv_transactions,
    read_xlsx_transactions,
)


def normalize_status(status: str) -> Optional[str]:
    """
    Приводит статус к единому регистру (верхний) и проверяет на допустимость.

    Функция принимает строку со статусом, удаляет лишние пробелы по краям,
    приводит к верхнему регистру и проверяет, содержится ли результат в списке
    допустимых статусов (AVAILABLE_STATUSES).

    Parameters
    ----------
    status : str
        Введённый пользователем статус операции.

    Returns
    -------
    Optional[str]
        Нормализованный статус в верхнем регистре, если он допустим;
        иначе None.
    """
    normalized = status.strip().upper()
    if normalized in [s.upper() for s in AVAILABLE_STATUSES]:
        return normalized
    return None


def ask_for_status() -> str:
    """
    Запрашивает у пользователя статус для фильтрации транзакций.

    Выводит список доступных статусов (на основе AVAILABLE_STATUSES),
    принимает ввод от пользователя и валидирует его с помощью
    функции normalize_status. Цикл продолжается, пока пользователь
    не введёт допустимый статус. После успешного ввода статус логируется
    на уровне INFO.

    Returns
    -------
    str
        Выбранный пользователем допустимый статус в верхнем регистре.
    """
    available_display = ", ".join(s.upper() for s in AVAILABLE_STATUSES)
    while True:
        user_input = input(
            f"Введите статус, по которому необходимо выполнить фильтрацию.\n"
            f"Доступные для фильтрации статусы: {available_display}\n> "
        )
        status = normalize_status(user_input)
        if status is not None:
            logger.info("Пользователь выбрал статус: %s", status)
            return status
        print(f'Статус операции "{user_input}" недоступен.')


def ask_sort_by_date() -> bool:
    """
    Спрашивает пользователя, нужно ли сортировать операции по дате.

    Принимает ввод «Да/Нет» в разных вариантах (включая английские сокращения)
    и возвращает логическое значение. Цикл продолжается, пока не будет
    получено корректное значение.

    Returns
    -------
    bool
        True, если пользователь хочет сортировку по дате; иначе False.
    """
    while True:
        answer = input("Отсортировать операции по дате? Да/Нет\n> ").strip().lower()
        if answer in ("да", "д", "yes", "y"):
            return True
        elif answer in ("нет", "н", "no", "n"):
            return False
        print("Пожалуйста, введите 'Да' или 'Нет'.")


def ask_sort_order() -> str:
    """
    Запрашивает порядок сортировки транзакций по дате.

    Спрашивает, нужно ли отсортировать по возрастанию или убыванию,
    принимая разные варианты ввода (включая сокращения и английские слова).
    Возвращает строку 'asc' или 'desc'.

    Returns
    -------
    str
        'asc' — сортировка по возрастанию;
        'desc' — сортировка по убыванию.
    """
    while True:
        answer = input("Отсортировать по возрастанию или по убыванию?\n> ").strip().lower()
        if "возр" in answer or "asc" in answer:
            return "asc"
        elif "убыв" in answer or "desc" in answer:
            return "desc"
        print("Пожалуйста, укажите 'по возрастанию' или 'по убыванию'.")


def ask_rub_only() -> bool:
    """
    Спрашивает пользователя, нужно ли выводить только рублёвые транзакции.

    Принимает ввод «Да/Нет» в разных вариантах и возвращает логическое значение.
    Цикл продолжается, пока не будет получено корректное значение.

    Returns
    -------
    bool
        True, если нужно отображать только транзакции в рублях; иначе False.
    """
    while True:
        answer = input("Выводить только рублёвые транзакции? Да/Нет\n> ").strip().lower()
        if answer in ("да", "д", "yes", "y"):
            return True
        elif answer in ("нет", "н", "no", "n"):
            return False
        print("Пожалуйста, введите 'Да' или 'Нет'.")


def ask_filter_by_keyword() -> Tuple[bool, Optional[str]]:
    """
    Предлагает пользователю отфильтровать транзакции по ключевому слову в описании.

    Сначала спрашивает, нужна ли фильтрация (Да/Нет), затем, при положительном
    ответе, запрашивает само слово. Пустое слово не принимается.

    Returns
    -------
    Tuple[bool, Optional[str]]
        Кортеж вида (нужно_фильтровать, ключевое_слово).
        Если фильтрация не нужна — (False, None).
        Если нужна — (True, слово).
    """
    while True:
        answer = input(
            "Отфильтровать список транзакций по определённому слову в описании? Да/Нет\n> "
        ).strip().lower()
        if answer in ("да", "д", "yes", "y"):
            keyword = input("Введите слово для поиска в описании:\n> ").strip()
            if not keyword:
                print("Слово не может быть пустым. Попробуйте ещё раз.")
                continue
            return True, keyword
        elif answer in ("нет", "н", "no", "n"):
            return False, None
        print("Пожалуйста, введите 'Да' или 'Нет'.")


def sort_transactions(
    transactions: List[Dict[str, Any]],
    order: str
) -> List[Dict[str, Any]]:
    """
    Сортирует список транзакций по полю 'date'.

    Предполагается, что каждая транзакция — это словарь, содержащий ключ 'date',
    значение которого может быть строкой в формате YYYY-MM-DD либо timestamp.
    Для строк формата YYYY-MM-DD лексикографическая сортировка корректна.

    Parameters
    ----------
    transactions : List[Dict[str, Any]]
        Список транзакций (словарей).
    order : str
        Порядок сортировки: 'asc' — по возрастанию, 'desc' — по убыванию.

    Returns
    -------
    List[Dict[str, Any]]
        Отсортированный список транзакций.
    """
    reverse = order == "desc"
    # Если даты в формате строки YYYY-MM-DD, лексикографическая сортировка корректна.
    return sorted(transactions, key=lambda t: t.get("date", ""), reverse=reverse)


def filter_by_currency_rub(
    transactions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции, оставляя только те, что в валюте RUB.

    Предполагается, что валюта транзакции хранится в поле 'currency'
    каждого словаря-транзакции. Сравнение выполняется без учёта регистра.

    Parameters
    ----------
    transactions : List[Dict[str, Any]]
        Список транзакций (словарей).

    Returns
    -------
    List[Dict[str, Any]]
        Список транзакций, где валюта равна 'RUB'.
    """
    return [t for t in transactions if t.get("currency", "").upper() == "RUB"]


def filter_by_description_keyword(
    transactions: List[Dict[str, Any]],
    keyword: str
) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по наличию ключевого слова в описании.

    Ищет подстроку `keyword` в поле 'description' каждой транзакции.
    Поиск выполняется без учёта регистра. Если поле отсутствует,
    транзакция не проходит фильтр.

    Parameters
    ----------
    transactions : List[Dict[str, Any]]
        Список транзакций (словарей).
    keyword : str
        Ключевое слово для поиска в поле 'description'.

    Returns
    -------
    List[Dict[str, Any]]
        Список транзакций, в описании которых содержится указанное слово.
    """
    keyword_lower = keyword.lower()
    result = []
    for t in transactions:
        desc = t.get("description", "")
        if isinstance(desc, str) and keyword_lower in desc.lower():
            result.append(t)
    return result

