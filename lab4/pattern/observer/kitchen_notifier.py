"""
KitchenNotifier — конкретний Observer, що сповіщає кухню про нові замовлення.
SRP: лише прийом та реєстрація сповіщень.
"""
from pattern.observer.order_observer import OrderObserver
from model.order import Order


class KitchenNotifier(OrderObserver):
    def __init__(self) -> None:
        self._received_orders: list[Order] = []

    def on_new_order(self, order: Order) -> None:
        self._received_orders.append(order)
        print(f"[КУХНЯ] Нове замовлення: {order}")

    def has_received(self, order: Order) -> bool:
        return order in self._received_orders

    def get_received_orders(self) -> list[Order]:
        return list(self._received_orders)

    def __repr__(self) -> str:
        return f"KitchenNotifier(received={len(self._received_orders)})"
