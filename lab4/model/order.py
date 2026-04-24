"""
Order — представляє замовлення клієнта.
SRP: управляє списком страв та підрахунком суми.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from model.order_type import OrderType

if TYPE_CHECKING:
    from model.dish import Dish
    from model.customer import Customer

_counter = 0


class Order:
    def __init__(self, customer: "Customer", order_type: OrderType = OrderType.REGULAR) -> None:
        if customer is None:
            raise ValueError("Клієнт не може бути None")
        global _counter
        _counter += 1
        self._id = _counter
        self._customer = customer
        self._type = order_type
        self._dishes: list["Dish"] = []

    @property
    def id(self) -> int:
        return self._id

    @property
    def customer(self) -> "Customer":
        return self._customer

    @property
    def order_type(self) -> OrderType:
        return self._type

    @property
    def dishes(self) -> list["Dish"]:
        return list(self._dishes)

    def add_dish(self, dish: "Dish") -> None:
        if dish is None:
            raise ValueError("Страва не може бути None")
        self._dishes.append(dish)

    def get_total(self) -> float:
        base = sum(d.price for d in self._dishes)
        return round(base * 0.9, 2) if self._type == OrderType.BULK else base

    def __repr__(self) -> str:
        return (
            f"Order(id={self._id}, type={self._type.name}, "
            f"customer='{self._customer.name}', "
            f"dishes={len(self._dishes)}, total={self.get_total()})"
        )
