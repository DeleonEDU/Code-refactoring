from model.dish import Dish
from model.customer import Customer
from service.menu import Menu
from service.order_service import OrderService
from pattern.factory.order_factory import RegularOrderFactory, BulkOrderFactory
from pattern.observer.kitchen_notifier import KitchenNotifier
from pattern.singleton.order_database import OrderDatabase

def main():
    print("=== Демонстрація системи замовлень ресторану ===\n")

    print("1. Створення меню та додавання страв...")
    menu = Menu()
    pizza = Dish("Піца Маргарита", 180.0)
    salad = Dish("Салат Цезар", 150.0)
    juice = Dish("Апельсиновий сік", 50.0)
    
    menu.add_dish(pizza)
    menu.add_dish(salad)
    menu.add_dish(juice)
    
    print("Поточне меню:")
    for dish in menu.get_dishes():
        print(f" - {dish.name}: {dish.price} грн")
    print()

    # 2. Налаштування сервісу замовлень та кухні (Observer Pattern)
    print("2. Налаштування сервісу замовлень та підключення кухні...")
    order_service = OrderService()
    kitchen = KitchenNotifier()
    order_service.add_observer(kitchen)
    print("Кухня підписана на нові замовлення.\n")

    print("3. Реєстрація клієнтів...")
    customer1 = Customer("Олександр", "+380501112233")
    customer2 = Customer("Марія", "+380679998877")
    print(f"Клієнти: {customer1.name}, {customer2.name}\n")

    print("4. Створення замовлень...")
    
    regular_factory = RegularOrderFactory()
    order1 = regular_factory.create_order(customer1)
    order1.add_dish(pizza)
    order1.add_dish(juice)
    print(f"Створено звичайне замовлення для {customer1.name}. Сума: {order1.get_total()} грн")

    bulk_factory = BulkOrderFactory()
    order2 = bulk_factory.create_order(customer2)
    order2.add_dish(pizza)
    order2.add_dish(pizza)
    order2.add_dish(salad)
    order2.add_dish(juice)
    print(f"Створено масове замовлення для {customer2.name} (зі знижкою 10%). Сума: {order2.get_total()} грн\n")

    print("5. Розміщення замовлень (відправка на кухню та збереження в БД)...")
    order_service.place_order(order1)
    order_service.place_order(order2)
    print()

    print("6. Перевірка бази даних замовлень...")
    db = OrderDatabase()
    print(f"Всього замовлень у базі: {db.count()}")
    
    db2 = OrderDatabase()
    print(f"Чи db і db2 є одним і тим самим об'єктом? {'Так' if db is db2 else 'Ні'}")

if __name__ == "__main__":
    main()
