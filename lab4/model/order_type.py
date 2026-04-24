"""
OrderType — тип замовлення.
"""
from enum import Enum, auto


class OrderType(Enum):
    REGULAR = auto()
    BULK = auto()
