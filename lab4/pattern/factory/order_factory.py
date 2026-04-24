"""
OrderFactory — патерн Factory для створення різних типів замовлень.
OCP: нові типи замовлень додаються без зміни OrderService.
DIP: OrderService може залежати від абстракції OrderFactory.
"""
from abc import ABC, abstractmethod
from model.customer import Customer
from model.order import Order
from model.order_type import OrderType


class OrderFactory(ABC):
    """Абстрактна фабрика замовлень."""

    @abstractmethod
    def create_order(self, customer: Customer) -> Order:
        """Створити нове замовлення для клієнта."""


class RegularOrderFactory(OrderFactory):
    """Фабрика звичайних замовлень."""

    def create_order(self, customer: Customer) -> Order:
        return Order(customer, OrderType.REGULAR)


class BulkOrderFactory(OrderFactory):
    """Фабрика масових замовлень (знижка 10%)."""

    def create_order(self, customer: Customer) -> Order:
        return Order(customer, OrderType.BULK)
