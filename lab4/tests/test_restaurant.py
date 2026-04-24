"""
Повний набір модульних тестів для системи замовлень ресторану.
Покриває: SOLID-класи, TDD-функціонал, патерни Singleton / Factory / Observer.
"""
import unittest

from model.dish import Dish
from model.customer import Customer
from model.order import Order
from model.order_type import OrderType
from service.menu import Menu
from service.order_service import OrderService
from pattern.singleton.order_database import OrderDatabase
from pattern.factory.order_factory import RegularOrderFactory, BulkOrderFactory
from pattern.observer.kitchen_notifier import KitchenNotifier


# ─────────────────────────────────────────────────────────────
# Частина 1 — Базові класи (SRP / OCP / DIP)
# ─────────────────────────────────────────────────────────────

class TestDish(unittest.TestCase):

    def test_01_create_dish_with_name_and_price(self):
        """Можна створити страву з назвою та ціною."""
        dish = Dish("Піца", 150.0)
        self.assertEqual(dish.name, "Піца")
        self.assertEqual(dish.price, 150.0)

    def test_02_dish_rejects_blank_name(self):
        """Страва відхиляє порожню назву."""
        with self.assertRaises(ValueError):
            Dish("", 100)

    def test_03_dish_rejects_negative_price(self):
        """Страва відхиляє від'ємну ціну."""
        with self.assertRaises(ValueError):
            Dish("Суп", -1)


class TestCustomer(unittest.TestCase):

    def test_04_create_customer(self):
        """Можна створити клієнта з ім'ям та телефоном."""
        customer = Customer("Олена", "+380501234567")
        self.assertEqual(customer.name, "Олена")
        self.assertEqual(customer.phone, "+380501234567")

    def test_05_customer_rejects_blank_name(self):
        """Клієнт відхиляє порожнє ім'я."""
        with self.assertRaises(ValueError):
            Customer("", "123")


class TestMenu(unittest.TestCase):

    def setUp(self):
        self.menu = Menu()
        self.dish = Dish("Піца", 150.0)

    def test_06_add_dish_to_menu(self):
        """Страву можна додати до меню та перевірити наявність."""
        self.menu.add_dish(self.dish)
        self.assertTrue(self.menu.contains_dish(self.dish))

    def test_07_menu_starts_empty(self):
        """Меню порожнє на початку."""
        self.assertTrue(self.menu.is_empty())

    def test_08_menu_size_grows_correctly(self):
        """Розмір меню збільшується при додаванні страв."""
        self.menu.add_dish(Dish("Борщ", 80))
        self.menu.add_dish(Dish("Вареники", 60))
        self.assertEqual(len(self.menu), 2)

    def test_09_remove_dish_from_menu(self):
        """Страву можна видалити з меню."""
        self.menu.add_dish(self.dish)
        self.menu.remove_dish(self.dish)
        self.assertFalse(self.menu.contains_dish(self.dish))

    def test_28_menu_not_contains_unadded_dish(self):
        """Меню не містить страву, яку не додавали."""
        self.assertFalse(self.menu.contains_dish(Dish("Пельмені", 70)))

    def test_29_menu_get_dishes_returns_copy(self):
        """get_dishes() повертає копію — зміна не впливає на меню."""
        self.menu.add_dish(self.dish)
        copy = self.menu.get_dishes()
        copy.clear()
        self.assertFalse(self.menu.is_empty())


class TestOrder(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("Іван", "0501111111")

    def test_10_order_associated_with_customer(self):
        """Замовлення пов'язане з правильним клієнтом."""
        order = Order(self.customer, OrderType.REGULAR)
        self.assertIs(order.customer, self.customer)

    def test_11_order_total_calculated_correctly(self):
        """Сума замовлення підраховується правильно."""
        order = Order(self.customer, OrderType.REGULAR)
        order.add_dish(Dish("Піца", 150))
        order.add_dish(Dish("Сік", 30))
        self.assertAlmostEqual(order.get_total(), 180.0)

    def test_12_order_rejects_none_customer(self):
        """Замовлення відхиляє None замість клієнта."""
        with self.assertRaises(ValueError):
            Order(None, OrderType.REGULAR)

    def test_27_empty_order_has_zero_total(self):
        """Замовлення без страв має суму 0."""
        order = Order(self.customer, OrderType.REGULAR)
        self.assertEqual(order.get_total(), 0.0)


# ─────────────────────────────────────────────────────────────
# Частина 2 — TDD: OrderService та повний сценарій
# ─────────────────────────────────────────────────────────────

class TestOrderService(unittest.TestCase):

    def setUp(self):
        OrderDatabase.reset_for_testing()
        self.customer = Customer("Петро", "0503333333")
        self.service = OrderService()

    def test_13_placing_order_saves_to_database(self):
        """Розміщення замовлення зберігає його в БД."""
        order = Order(self.customer, OrderType.REGULAR)
        self.service.place_order(order)
        self.assertTrue(OrderDatabase().contains(order))

    def test_14_multiple_orders_saved_to_database(self):
        """Кілька замовлень зберігаються в БД."""
        self.service.place_order(Order(self.customer, OrderType.REGULAR))
        self.service.place_order(Order(self.customer, OrderType.REGULAR))
        self.assertEqual(OrderDatabase().count(), 2)

    def test_15_kitchen_notified_on_order(self):
        """KitchenNotifier сповіщається при розміщенні замовлення."""
        order = Order(self.customer, OrderType.REGULAR)
        kitchen = KitchenNotifier()
        self.service.add_observer(kitchen)
        self.service.place_order(order)
        self.assertTrue(kitchen.has_received(order))

    def test_16_kitchen_not_notified_after_removal(self):
        """Кухня НЕ сповіщається після видалення Observer."""
        order = Order(self.customer, OrderType.REGULAR)
        kitchen = KitchenNotifier()
        self.service.add_observer(kitchen)
        self.service.remove_observer(kitchen)
        self.service.place_order(order)
        self.assertFalse(kitchen.has_received(order))

    def test_17_multiple_observers_all_notified(self):
        """Всі Observer-и отримують сповіщення."""
        order = Order(self.customer, OrderType.REGULAR)
        k1, k2 = KitchenNotifier(), KitchenNotifier()
        self.service.add_observer(k1)
        self.service.add_observer(k2)
        self.service.place_order(order)
        self.assertTrue(k1.has_received(order))
        self.assertTrue(k2.has_received(order))

    def test_18_service_rejects_none_order(self):
        """OrderService відхиляє None замість замовлення."""
        with self.assertRaises(ValueError):
            self.service.place_order(None)


# ─────────────────────────────────────────────────────────────
# Частина 3 — Патерни проектування
# ─────────────────────────────────────────────────────────────

class TestSingleton(unittest.TestCase):

    def setUp(self):
        OrderDatabase.reset_for_testing()

    def test_19_singleton_returns_same_instance(self):
        """Singleton повертає той самий екземпляр."""
        db1 = OrderDatabase()
        db2 = OrderDatabase()
        self.assertIs(db1, db2)

    def test_20_singleton_data_persists(self):
        """Дані зберігаються між викликами getInstance."""
        customer = Customer("Галина", "0508888888")
        order = Order(customer, OrderType.REGULAR)
        OrderDatabase().save(order)
        self.assertEqual(OrderDatabase().count(), 1)


class TestFactory(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("Сергій", "0509999999")

    def test_21_regular_factory_creates_regular_order(self):
        """RegularOrderFactory створює замовлення типу REGULAR."""
        order = RegularOrderFactory().create_order(self.customer)
        self.assertEqual(order.order_type, OrderType.REGULAR)
        self.assertIs(order.customer, self.customer)

    def test_22_bulk_factory_creates_bulk_order(self):
        """BulkOrderFactory створює замовлення типу BULK."""
        order = BulkOrderFactory().create_order(self.customer)
        self.assertEqual(order.order_type, OrderType.BULK)

    def test_23_bulk_order_applies_10_percent_discount(self):
        """Масове замовлення застосовує знижку 10%."""
        order = BulkOrderFactory().create_order(self.customer)
        order.add_dish(Dish("Курка", 200))
        self.assertAlmostEqual(order.get_total(), 180.0)

    def test_24_regular_order_has_no_discount(self):
        """Звичайне замовлення не має знижки."""
        order = RegularOrderFactory().create_order(self.customer)
        order.add_dish(Dish("Салат", 100))
        self.assertAlmostEqual(order.get_total(), 100.0)


class TestObserver(unittest.TestCase):

    def setUp(self):
        OrderDatabase.reset_for_testing()
        self.customer = Customer("Богдан", "0501111114")
        self.service = OrderService()
        self.kitchen = KitchenNotifier()
        self.service.add_observer(self.kitchen)

    def test_25_kitchen_receives_all_orders(self):
        """KitchenNotifier отримує всі розміщені замовлення."""
        o1 = Order(self.customer, OrderType.REGULAR)
        o2 = Order(self.customer, OrderType.BULK)
        self.service.place_order(o1)
        self.service.place_order(o2)
        self.assertEqual(len(self.kitchen.get_received_orders()), 2)
        self.assertTrue(self.kitchen.has_received(o1))
        self.assertTrue(self.kitchen.has_received(o2))

    def test_26_kitchen_empty_before_orders(self):
        """KitchenNotifier порожній до першого замовлення."""
        fresh_kitchen = KitchenNotifier()
        self.assertTrue(len(fresh_kitchen.get_received_orders()) == 0)


# ─────────────────────────────────────────────────────────────
# Інтеграційний тест
# ─────────────────────────────────────────────────────────────

class TestFullIntegration(unittest.TestCase):

    def setUp(self):
        OrderDatabase.reset_for_testing()

    def test_30_full_flow(self):
        """Повний сценарій: меню → замовлення → кухня → БД."""

        menu = Menu()
        pizza = Dish("Піца Маргарита", 180)
        menu.add_dish(pizza)
        self.assertTrue(menu.contains_dish(pizza))

        customer = Customer("Тарас", "0501111116")
        order = RegularOrderFactory().create_order(customer)
        order.add_dish(pizza)
        self.assertAlmostEqual(order.get_total(), 180.0)

        kitchen = KitchenNotifier()
        service = OrderService()
        service.add_observer(kitchen)
        service.place_order(order)

        self.assertTrue(OrderDatabase().contains(order))
        self.assertTrue(kitchen.has_received(order))
        self.assertEqual(OrderDatabase().count(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
