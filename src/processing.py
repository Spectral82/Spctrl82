from typing import List, Dict, Any

def filter_by_state(operations: List[Dict[str, Any]], state: str = 'EXECUTED') -> List[Dict[str, Any]]:
    """
    Фильтрует список операций по значению ключа 'state'.

    :param operations: list[dict] — список операций
    :param state: str — значение статуса (по умолчанию 'EXECUTED')
    :return: list[dict] — отфильтрованный список
    """
    return [op for op in operations if op.get('state') == state]


def sort_by_date(operations: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список операций по ключу 'date'.

    :param operations: list[dict] — список операций
    :param reverse: bool — сортировка по убыванию (по умолчанию True)
    :return: list[dict] — отсортированный список
    """
    return sorted(operations, key=lambda op: op.get('date', ''), reverse=reverse)

operations = [
    {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
    {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
    {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
    {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}
]

executed = filter_by_state(operations)
canceled = filter_by_state(operations, state='CANCELED')
sorted_ops = sort_by_date(operations)