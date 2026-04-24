from model.order import Order
from pattern.observer.order_observer import OrderObserver
from pattern.singleton.order_database import OrderDatabase


class OrderService:
    def __init__(self) -> None:
        self._observers: list[OrderObserver] = []
        self._database = OrderDatabase()

    def add_observer(self, observer: OrderObserver) -> None:
        self._observers.append(observer)

    def remove_observer(self, observer: OrderObserver) -> None:
        self._observers.remove(observer)

    def place_order(self, order: Order) -> None:
        if order is None:
            raise ValueError("Замовлення не може бути None")
        self._database.save(order)
        self._notify_observers(order)

    def _notify_observers(self, order: Order) -> None:
        for observer in self._observers:
            observer.on_new_order(order)
