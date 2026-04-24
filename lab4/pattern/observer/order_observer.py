"""
OrderObserver — абстрактний інтерфейс для патерну Observer.
DIP: OrderService залежить від цієї абстракції, а не від конкретних класів.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.order import Order


class OrderObserver(ABC):
    @abstractmethod
    def on_new_order(self, order: "Order") -> None:
        """Викликається при розміщенні нового замовлення."""
