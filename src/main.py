import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from src.data_reader import read_csv_transactions, read_json_transactions, read_xlsx_transactions
from src.utils import sort_transactions

AVAILABLE_STATUSES = ["EXECUTED", "CANCELED", "PENDING"]

logger = logging.getLogger(__name__)


def mask_account(account: Optional[str]) -> str:
    """Маскирует номер счёта/карты, оставляя последние 4 цифры."""
    if not account:
        return ""
    account = str(account).strip()
    if len(account) <= 4:
        return account
    return "**" + account[-4:]


def format_date_iso_to_ddmmyyyy(iso_date: str) -> str:
    """Преобразует ISO дату в DD.MM.YYYY."""
    clean = iso_date.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(clean)
    except ValueError:
        return iso_date
    return dt.strftime("%d.%m.%Y")


def get_formatted_transaction_line(t: Dict[str, Any]) -> str:
    """
    Формирует одну строку транзакции в требуемом виде.
    Формат как в примере:
      08.12.2019 Открытие вклада
      Счет **4321
      Сумма: 40542 руб.
    или
      12.11.2019 Перевод с карты на карту
      MasterCard 7771 27** **** 3727 -> Visa Platinum 1293 38** **** 9203
      Сумма: 130 USD
    """
    raw_date = t.get("date", "")
    date_str = format_date_iso_to_ddmmyyyy(raw_date) if isinstance(raw_date, str) else str(raw_date)

    description = t.get("description", "Без описания")

    amount_info = t.get("operationAmount", {})
    amount = amount_info.get("amount", 0)
    currency_info = amount_info.get("currency", {})
    currency_code = currency_info.get("code", "").upper()
    currency_display = "руб." if currency_code == "RUB" else currency_code

    from_acc = None
    to_acc = None

    if "from" in t and isinstance(t["from"], dict):
        from_acc = t["from"].get("account") or t["from"].get("cardNumber")
    elif "fromAccount" in t:
        from_acc = t["fromAccount"]

    if "to" in t and isinstance(t["to"], dict):
        to_acc = t["to"].get("account") or t["to"].get("cardNumber")
    elif "toAccount" in t:
        to_acc = t["toAccount"]

    lines = []
    lines.append(f"{date_str} {description}")

    if from_acc and to_acc:
        from_name = t["from"].get("cardType") if isinstance(t.get("from"), dict) else None
        to_name = t["to"].get("cardType") if isinstance(t.get("to"), dict) else None

        from_part = f"{from_name} {from_acc}" if from_name else mask_account(from_acc)
        to_part = f"{to_name} {to_acc}" if to_name else mask_account(to_acc)

        lines.append(f"{from_part} -> {to_part}")
    elif from_acc:
        lines.append(f"Счет {mask_account(from_acc)}")
    elif to_acc:
        lines.append(f"Счет {mask_account(to_acc)}")

    lines.append(f"Сумма: {amount} {currency_display}")

    return "\n".join(lines)


def print_transactions_target_format(transactions: List[Dict[str, Any]]) -> None:
    """Выводит список транзакций строго в требуемом формате."""
    print(f"Всего банковских операций в выборке: {len(transactions)}")
    for t in transactions:
        print(get_formatted_transaction_line(t))
        print()


def export_to_json(data: List[Dict[str, Any]], filename: str = "transactions.json") -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Данные сохранены в JSON: %s", filename)
        print(f"Данные успешно сохранены в файл {filename}")
    except OSError as e:
        logger.error("Ошибка при записи JSON: %s", e, exc_info=True)
        raise


def export_to_csv(data: List[Dict[str, Any]], filename: str = "transactions.csv") -> None:
    df = pd.DataFrame(data)
    try:
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        logger.info("Данные сохранены в CSV: %s", filename)
        print(f"Данные успешно сохранены в файл {filename}")
    except OSError as e:
        logger.error("Ошибка при записи CSV: %s", e, exc_info=True)
        raise


def export_to_xlsx(data: List[Dict[str, Any]], filename: str = "transactions.xlsx") -> None:
    df = pd.DataFrame(data)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["date"] = df["date"].dt.tz_localize(None)

    try:
        df.to_excel(filename, index=False, sheet_name="Transactions")
        logger.info("Данные сохранены в XLSX: %s", filename)
        print(f"Данные успешно сохранены в файл {filename}")
    except OSError as e:
        logger.error("Ошибка при записи XLSX: %s", e, exc_info=True)
        raise


def normalize_status(status: str) -> Optional[str]:
    if status is None or isinstance(status, float):
        return None
    normalized = str(status).strip().upper()
    allowed_set = {s.strip().upper() for s in AVAILABLE_STATUSES}
    if normalized in allowed_set:
        return normalized
    return None


def filter_transactions_by_status(
    transactions: List[Dict[str, Any]],
    status: Optional[str],
) -> List[Dict[str, Any]]:
    if status is None:
        return transactions
    filtered = [t for t in transactions if normalize_status(t.get("status", t.get("state", ""))) == status]
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

    file_path = ""
    transactions: List[Dict[str, Any]] = []

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
        print("Для обработки выбран XLSX-файл.")
        file_path = input("Введите путь к XLSX-файлу: ").strip()
        if not os.path.isfile(file_path):
            print("Файл не найден. Программа завершена.")
            return
        transactions = read_xlsx_transactions(file_path)
    else:
        print("Неверный выбор. Программа завершена.")
        return

    available_display = ", ".join(AVAILABLE_STATUSES)
    while True:
        user_input = input(
            f"Введите статус, по которому необходимо выполнить фильтрацию.\n"
            f"Доступные для фильтрации статусы: {available_display}\n> "
        )
        status = normalize_status(user_input)
        if status is not None:
            logger.info("Пользователь выбрал статус: %s", status)
            print(f'Операции отфильтрованы по статусу "{status}"')
            break
        print(f'Статус операции "{user_input}" недоступен.')

    filtered_transactions = filter_transactions_by_status(transactions, status)

    sort_choice = input("Отсортировать операции по дате? Да/Нет: ").strip().lower()
    if sort_choice in ("да", "д", "yes", "y"):
        order_choice = input("Отсортировать по возрастанию или по убыванию? ").strip().lower()
        ascending = order_choice in ("возрастанию", "по возрастанию", "да", "д", "yes", "y")
        filtered_transactions = sort_transactions(filtered_transactions, ascending)

    currency_filter = input("Выводить только рублевые транзакции? Да/Нет: ").strip().lower()
    if currency_filter in ("да", "д", "yes", "y"):
        filtered_transactions = [
            t
            for t in filtered_transactions
            if t.get("operationAmount", {}).get("currency", {}).get("code", "") == "RUB"
        ]

    description_filter = (
        input("Отфильтровать список транзакций по определённому слову в описании? Да/Нет: ").strip().lower()
    )

    if description_filter in ("да", "д", "yes", "y"):
        keyword = input("Введите слово для фильтрации: ").strip().lower()
        filtered_transactions = [t for t in filtered_transactions if keyword in t.get("description", "").lower()]

    if not filtered_transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        logger.warning("Пустой набор транзакций после всех фильтров.")
        return

    print("Распечатываю итоговый список транзакций...")
    print()
    print_transactions_target_format(filtered_transactions)

    choice = input("\nВыберите формат экспорта (json/csv/xlsx) или 'нет': ").strip().lower()
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
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
