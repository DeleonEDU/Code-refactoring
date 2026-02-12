from fastapi.testclient import TestClient
from unittest.mock import patch
import datetime

from main import app
from database import clear_db, users_db, orders_db
from config import Role, Category
import pytest

client = TestClient(app)

# Ця фікстура запускається перед кожним тестом автоматично.
# Вона гарантує, що тести не впливають один на одного.
@pytest.fixture(autouse=True)
def clean_db_fixture():
    clear_db()


# Тест 1: Звичайна покупка
def test_regular_purchase_electronics():
    """Перевіряє успішну покупку електроніки звичайним користувачем без знижок."""
    payload = {
        "user": {"email": "user@test.com", "password": "password123", "role": "customer"},
        "items": [{"category": Category.ELECTRONICS, "price": 1000}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 200
    assert response.json()["total"] == 1000

# Тест 2: VIP знижка
def test_vip_discount_electronics():
    """Перевіряє, чи застосовується знижка 10% для VIP клієнтів."""
    payload = {
        "user": {"email": "vip@test.com", "password": "password123", "role": "vip"},
        "items": [{"category": Category.ELECTRONICS, "price": 1000}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 200
    # 1000 - 10% = 900
    assert response.json()["total"] == 900

# Тест 3: Admin знижка
def test_admin_discount_electronics():
    """Перевіряє, чи застосовується знижка 50% для Адмінів."""
    payload = {
        "user": {"email": "admin@test.com", "password": "password123", "role": "admin"},
        "items": [{"category": Category.ELECTRONICS, "price": 1000}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 200
    # 1000 - 50% = 500
    assert response.json()["total"] == 500

# Тест 4: Валідація короткого пароля (Pydantic)
def test_short_password_validation():
    """Перевіряє, чи API відхиляє паролі коротші за 8 символів."""
    payload = {
        "user": {"email": "bad@test.com", "password": "short", "role": "customer"},
        "items": [{"category": 1, "price": 100}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    # 422 Unprocessable Entity - стандартна помилка валідації FastAPI
    assert response.status_code == 422 

# Тест 5: Валідація формату Email
def test_invalid_email_validation():
    """Перевіряє, чи API відхиляє некоректні email адреси."""
    payload = {
        "user": {"email": "not-an-email", "password": "password123", "role": "customer"},
        "items": [{"category": 1, "price": 100}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 422

# Тест 6: Фрод-контроль (Fraud Check)
def test_fraud_check_new_user_limit():
    """Перевіряє блокування транзакції > 5000 для нових користувачів при оплаті карткою."""
    payload = {
        "user": {"email": "fraud@test.com", "password": "password123", "role": "new"},
        "items": [{"category": Category.ELECTRONICS, "price": 6000}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Limit exceeded"

# Тест 7: Знижка вихідного дня
# Ми "обманюємо" програму, змушуючи її думати, що сьогодні субота (день 5)
@patch("pricing_service.datetime") 
def test_saturday_discount_clothing(mock_datetime):
    """Перевіряє знижку на одяг у суботу (використовує Mock)."""
    # Налаштовуємо мок: .now() повертає суботу
    mock_datetime.datetime.now.return_value.weekday.return_value = 5
    
    payload = {
        "user": {"email": "sat@test.com", "password": "password123", "role": "customer"},
        "items": [{"category": Category.CLOTHING, "price": 100}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 200
    # 100 - 10 (знижка вихідного дня) = 90
    assert response.json()["total"] == 90

# Тест 8: Змішаний кошик
def test_mixed_cart_calculation():
    """Перевіряє правильність суми для кількох товарів."""
    payload = {
        "user": {"email": "mix@test.com", "password": "password123", "role": "customer"},
        "items": [
            {"category": Category.ELECTRONICS, "price": 100},
            {"category": Category.CLOTHING, "price": 200}
        ],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 200
    # Якщо не субота і не VIP, то просто сума: 100 + 200 = 300
    # (Ми припускаємо, що тест запускається не в суботу, або перевіряємо >= 290)
    assert response.json()["total"] in [300, 290]

# Тест 9: Створення користувача (Side Effect)
def test_user_creation_in_db():
    """Перевіряє, що новий користувач дійсно зберігається в 'базі'."""
    email = "db_check@test.com"
    payload = {
        "user": {"email": email, "password": "password123", "role": "customer"},
        "items": [{"category": 1, "price": 100}],
        "payment": "card"
    }
    client.post("/buy", json=payload)
    
    # Робимо запит до ендпоінту отримання користувачів
    response = client.get("/users")
    users = response.json()
    
    # Шукаємо нашого юзера
    found = any(u['email'] == email for u in users)
    assert found is True

# Тест 10: Уникнення дублікатів користувачів
def test_existing_user_no_duplicate():
    """Перевіряє, що система не створює дублікат юзера, якщо він вже існує."""
    user_data = {"email": "repeat@test.com", "password": "password123", "role": "customer"}
    
    # Дві покупки підряд одним юзером
    client.post("/buy", json={"user": user_data, "items": [], "payment": "card"})
    client.post("/buy", json={"user": user_data, "items": [], "payment": "card"})
    
    response = client.get("/users")
    users_list = response.json()
    
    # Фільтруємо юзерів з таким email
    matching_users = [u for u in users_list if u['email'] == "repeat@test.com"]
    assert len(matching_users) == 1