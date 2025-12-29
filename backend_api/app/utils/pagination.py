from typing import Any, List, Tuple


def paginate(items_query, page: int, size: int) -> Tuple[List[Any], int]:
    total = items_query.count()
    items = items_query.offset((page - 1) * size).limit(size).all()
    return items, total
