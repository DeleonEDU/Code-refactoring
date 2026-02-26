import pytest
from shop_models import User, Product, Order

# Фікстури для зручності
@pytest.fixture
def sample_user():
    return User(1, "test_user", "secure123")

@pytest.fixture
def sample_products():
    return [
        Product(101, "Laptop", 1200.0),
        Product(102, "Mouse", 25.0)
    ]

# Тести для класу User

def test_user_registration_success(sample_user):
    """Перевірка успішної реєстрації (пароль достатньої довжини)"""
    assert sample_user.register() is True

def test_user_registration_fail():
    """Перевірка помилки реєстрації (короткий пароль)"""
    user = User(2, "bad_user", "123")
    assert user.register() is False

def test_user_login_success(sample_user):
    """Перевірка успішного логіну"""
    assert sample_user.login("secure123") is True

def test_user_login_fail(sample_user):
    """Перевірка помилки логіну з неправильним паролем"""
    assert sample_user.login("wrong_password") is False

# Тести для класу Product

def test_product_details():
    """Перевірка виводу інформації про товар"""
    product = Product(99, "Keyboard", 50.0)
    assert product.get_details() == "Product #99: Keyboard - $50.0"

# Тести для класу Order (та взаємодії)

def test_order_add_product(sample_user, sample_products):
    """Перевірка додавання товару в замовлення"""
    sample_user.login("secure123")
    order = sample_user.create_order(1)
    
    order.add_product(sample_products[0])
    assert len(order.products) == 1
    assert order.products[0].name == "Laptop"

def test_order_remove_existing_product(sample_user, sample_products):
    """Перевірка видалення існуючого товару з кошика"""
    sample_user.login("secure123")
    order = sample_user.create_order(1)
    
    order.add_product(sample_products[0])
    order.add_product(sample_products[1])
    
    result = order.remove_product(sample_products[0])
    assert result is True
    assert len(order.products) == 1

def test_order_remove_nonexistent_product(sample_user, sample_products):
    """Крайній випадок: спроба видалити товар, якого немає в замовленні"""
    sample_user.login("secure123")
    order = sample_user.create_order(1)
    
    order.add_product(sample_products[0])
    
    result = order.remove_product(sample_products[1]) # Намагаємось видалити Mouse
    assert result is False

def test_order_calculate_total(sample_user, sample_products):
    """Перевірка правильного підрахунку загальної суми замовлення"""
    sample_user.login("secure123")
    order = sample_user.create_order(1)
    
    order.add_product(sample_products[0]) # 1200.0
    order.add_product(sample_products[1]) # 25.0
    
    assert order.calculate_total() == 1225.0

def test_integration_user_orders_history(sample_user, sample_products):
    """Тестування взаємодії об'єктів: Користувач створює кілька замовлень і переглядає історію"""
    sample_user.login("secure123")
    
    # Створюємо перше замовлення
    order1 = sample_user.create_order(1)
    order1.add_product(sample_products[0])
    
    # Створюємо друге замовлення
    order2 = sample_user.create_order(2)
    order2.add_product(sample_products[1])
    
    # Перевіряємо, чи обидва замовлення прив'язані до користувача
    history = sample_user.view_orders()
    assert len(history) == 2
    assert history[0].calculate_total() == 1200.0
    assert history[1].calculate_total() == 25.0

def test_create_order_without_login_raises_error(sample_user):
    """Крайній випадок: створення замовлення без авторизації викликає помилку"""
    with pytest.raises(PermissionError):
        sample_user.create_order(1)
