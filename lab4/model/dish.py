"""
Dish — представляє одну страву в меню.
SRP: зберігає лише дані страви.
"""


class Dish:
    def __init__(self, name: str, price: float) -> None:
        if not name or not name.strip():
            raise ValueError("Назва страви не може бути порожньою")
        if price < 0:
            raise ValueError("Ціна не може бути від'ємною")
        self._name = name.strip()
        self._price = price

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    def __repr__(self) -> str:
        return f"Dish(name='{self._name}', price={self._price})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dish):
            return NotImplemented
        return self._name == other._name and self._price == other._price
