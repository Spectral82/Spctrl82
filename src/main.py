import os
import json
import logging
from typing import List, Dict, Any, Optional
from src.utils import sort_transactions

from src.data_reader import read_csv_transactions, read_xlsx_transactions, read_json_transactions

import pandas as pd
AVAILABLE_STATUSES = ['EXECUTED', 'CANCELED', 'PENDING']

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

logger = logging.getLogger(__name__)


def get_transactions() -> List[Dict[str, Any]]:
    return [
        {"id": 1, "date": "2024-06-01", "amount": 1500.50, "currency": "RUB", "type": "withdrawal", "status": "EXECUTED"},
        {"id": 2, "date": "2024-06-03", "amount": 3200.00, "currency": "RUB", "type": "deposit", "status": "PENDING"},
        {"id": 3, "date": "2024-06-10", "amount": -800.75, "currency": "RUB", "type": "transfer", "status": "CANCELED"},
        {"id": 4, "date": "2024-06-12", "amount": 500.00, "currency": "RUB", "type": "deposit", "status": "EXECUTED"},
    ]


def export_to_json(data: List[Dict[str, Any]], filename: str = "transactions.json") -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Данные сохранены в JSON: %s", filename)
        print(f" Данные успешно сохранены в файл {filename}")
    except OSError as e:
        logger.error("Ошибка при записи JSON: %s", e, exc_info=True)
        raise


def export_to_csv(data: List[Dict[str, Any]], filename: str = "transactions.csv") -> None:
    df = pd.DataFrame(data)
    try:
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        logger.info("Данные сохранены в CSV: %s", filename)
        print(f" Данные успешно сохранены в файл {filename}")
    except OSError as e:
        logger.error("Ошибка при записи CSV: %s", e, exc_info=True)
        raise


def export_to_xlsx(data: List[Dict[str, Any]], filename: str = "transactions.xlsx") -> None:
    df = pd.DataFrame(data)
    try:
        df.to_excel(filename, index=False, sheet_name="Transactions")
        logger.info("Данные сохранены в XLSX: %s", filename)
        print(f" Данные успешно сохранены в файл {filename}")
    except OSError as e:
        logger.error("Ошибка при записи XLSX: %s", e, exc_info=True)
        raise


def normalize_status(status: str) -> Optional[str]:
    normalized = status.strip().upper()
    allowed_set = {s.strip().upper() for s in AVAILABLE_STATUSES}
    if normalized in allowed_set:
        return normalized
    return None


def ask_for_status() -> str:
    available_display = ", ".join(s.strip().upper() for s in AVAILABLE_STATUSES)
    while True:
        user_input = input(
            f"Введите статус, по которому необходимо выполнить фильтрацию.\n"
            f"Доступные для фильтрации статусы: {available_display}\n> "
        )
        status = normalize_status(user_input)
        if status is not None:
            logger.info("Пользователь выбрал статус: %s", status)
            return status
        print("Неверный статус. Пожалуйста, выберите один из доступных.")


def filter_transactions_by_status(
    transactions: List[Dict[str, Any]],
    status: Optional[str],
) -> List[Dict[str, Any]]:
    if status is None:
        return transactions
    filtered = [
        t for t in transactions
        if normalize_status(t.get("status", "")) == status
    ]
    logger.debug("Отфильтровано транзакций: %d (из %d)", len(filtered), len(transactions))
    return filtered


def main() -> None:
    logger.info("Запуск приложения")
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    menu_choice = input("Ваш выбор (1/2/3): ").strip()
    if menu_choice == "1":
        print("Для обработки выбран JSON-файл.")
        file_path = input("Введите путь к JSON-файлу: ").strip()
        if not os.path.isfile(file_path):
            print("Файл не найден. Программа завершена.")
            return
        transactions = read_json_transactions(file_path)

    elif menu_choice == "2":
        print("Для обработки выбран CSV-файл.")
        file_path = input("Введите путь к CSV-файлу: ").strip()
        if not os.path.isfile(file_path):
            print("Файл не найден. Программа завершена.")
            return
        transactions = read_csv_transactions(file_path)

    elif menu_choice == "3":
        # Аналогично для XLSX при необходимости
        print("Для обработки выбран XLSX-файл.")
        file_path = input("Введите путь к XLSX-файлу: ").strip()
        if not os.path.isfile(file_path):
            print("Файл не найден. Программа завершена.")
            return
        transactions = read_xlsx_transactions(file_path)

    else:
        print("Неверный выбор. Программа завершена.")
        return


    use_filter = input("Хотите отфильтровать транзакции по статусу? (да/нет): ").strip().lower()
    status_filter: Optional[str] = None
    if use_filter in ("да", "д", "yes", "y"):
        status_filter = ask_for_status()

    filtered_transactions = filter_transactions_by_status(transactions, status_filter)

    if not filtered_transactions:
        print("После фильтрации не осталось транзакций для экспорта.")
        logger.warning("Пустой набор транзакций после фильтрации.")
        return

    # Запрашиваем уточняющие параметры
    sort_choice = input("Отсортировать операции по дате? (да/нет): ").strip().lower()
    if sort_choice in ("да", "д", "yes", "y"):
        order_choice = input("Отсортировать по возрастанию или по убыванию? ").strip().lower()
        ascending = order_choice in ("возрастанию", "по возрастанию", "да", "д", "yes", "y")
        filtered_transactions = sort_transactions(filtered_transactions, ascending)

    currency_filter = input("Выводить только рублевые транзакции? (да/нет): ").strip().lower()
    if currency_filter in ("да", "д", "yes", "y"):
        filtered_transactions = [t for t in filtered_transactions if t["currency"] == "RUB"]

    description_filter = input(
        "Отфильтровать список транзакций по определенному слову в описании? (да/нет): ").strip().lower()
    if description_filter in ("да", "д", "yes", "y"):
        keyword = input("Введите слово для фильтрации: ").strip().lower()
        filtered_transactions = [t for t in filtered_transactions if keyword in t["type"].lower()]

    print("Распечатываю итоговый список транзакций...")
    for transaction in filtered_transactions:
        print(transaction)

    print(f"\nВсего банковских операций в выборке: {len(filtered_transactions)}")
    choice = input("Выберите формат экспорта (json/csv/xlsx) или 'нет': ").strip().lower()
    if choice == "json":
        export_to_json(filtered_transactions)
    elif choice == "csv":
        export_to_csv(filtered_transactions)
    elif choice == "xlsx":
        export_to_xlsx(filtered_transactions)
    else:
        print("Экспорт отменён.")
        logger.info("Пользователь отменил экспорт.")



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
    main()