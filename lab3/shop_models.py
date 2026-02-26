from typing import List

class Product:
    def __init__(self, product_id: int, name: str, price: float):
        self._id = product_id
        self._name = name
        self._price = price

    @property
    def price(self) -> float:
        return self._price

    @property
    def name(self) -> str:
        return self._name

    def get_details(self) -> str:
        return f"Product #{self._id}: {self._name} - ${self._price}"

class Order:
    def __init__(self, order_id: int, user: 'User'):
        self._order_id = order_id
        self._user = user
        self._products: List[Product] = []
        self._status = "New"

    @property
    def products(self) -> List[Product]:
        return self._products

    def add_product(self, product: Product) -> None:
        self._products.append(product)

    def remove_product(self, product: Product) -> bool:
        if product in self._products:
            self._products.remove(product)
            return True
        return False

    def calculate_total(self) -> float:
        return sum(p.price for p in self._products)

class User:
    def __init__(self, user_id: int, username: str, password: str):
        self._id = user_id
        self._username = username
        self._password = password
        self._orders: List[Order] = []
        self._is_logged_in = False

    @property
    def username(self) -> str:
        return self._username

    def register(self) -> bool:
        if len(self._password) >= 6:
            return True
        return False

    def login(self, password_attempt: str) -> bool:
        if self._password == password_attempt:
            self._is_logged_in = True
            return True
        return False

    def create_order(self, order_id: int) -> Order:
        if not self._is_logged_in:
            raise PermissionError("User must be logged in to create an order.")
        new_order = Order(order_id, self)
        self._orders.append(new_order)
        return new_order

    def view_orders(self) -> List[Order]:
        return self._orders
