"""
OrderDatabase — Singleton: єдина БД замовлень у всьому застосунку.
Патерн Singleton через метаклас для потокобезпечності.
"""
import threading
from model.order import Order


class _SingletonMeta(type):
    _instances: dict = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class OrderDatabase(metaclass=_SingletonMeta):
    def __init__(self) -> None:
        # __init__ викликається лише один раз завдяки метакласу
        if not hasattr(self, "_initialized"):
            self._orders: list[Order] = []
            self._initialized = True

    def save(self, order: Order) -> None:
        self._orders.append(order)

    def get_all_orders(self) -> list[Order]:
        return list(self._orders)

    def contains(self, order: Order) -> bool:
        return order in self._orders

    def count(self) -> int:
        return len(self._orders)

    @classmethod
    def reset_for_testing(cls) -> None:
        """Скидає Singleton — лише для ізоляції тестів."""
        with _SingletonMeta._lock:
            _SingletonMeta._instances.pop(cls, None)

    def __repr__(self) -> str:
        return f"OrderDatabase(orders={len(self._orders)})"
