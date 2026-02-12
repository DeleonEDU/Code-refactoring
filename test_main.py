from fastapi.testclient import TestClient
from draft import app, users_db, orders_db
import pytest

client = TestClient(app)

# Фікстура для очищення "бази" перед кожним тестом
@pytest.fixture(autouse=True)
def clean_db():
    users_db.clear()
    orders_db.clear()

def test_regular_purchase_electronics():
    payload = {
        "user": {"email": "test@example.com", "password": "password123", "role": "customer"},
        "items": [{"category": 1, "price": 1000}], # Категорія 1 - електроніка
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 200
    assert response.json()["total"] == 1000  # Звичайна ціна

def test_vip_discount_electronics():
    payload = {
        "user": {"email": "vip@example.com", "password": "password123", "role": "vip"},
        "items": [{"category": 1, "price": 1000}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 200
    # 1000 * 0.90 = 900
    assert response.json()["total"] == 900 

def test_admin_discount_electronics():
    payload = {
        "user": {"email": "admin@example.com", "password": "password123", "role": "admin"},
        "items": [{"category": 1, "price": 1000}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 200
    # 1000 * 0.50 = 500
    assert response.json()["total"] == 500

def test_short_password_validation():
    payload = {
        "user": {"email": "bad@example.com", "password": "short", "role": "customer"}, # < 8 chars
        "items": [{"category": 1, "price": 100}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password too short"

def test_fraud_check_new_user_high_amount():
    # Новий юзер + сума > 5000 + карта = помилка
    payload = {
        "user": {"email": "fraud@example.com", "password": "password123", "role": "new"},
        "items": [{"category": 1, "price": 6000}],
        "payment": "card"
    }
    response = client.post("/buy", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Limit exceeded"

def test_user_creation_side_effect():
    # Перевіряємо, що юзер створився в "БД" під час покупки
    payload = {
        "user": {"email": "newuser@example.com", "password": "password123", "role": "customer"},
        "items": [{"category": 1, "price": 100}],
        "payment": "card"
    }
    client.post("/buy", json=payload)
    
    response = client.get("/users")
    users = response.json()
    assert len(users) == 1
    assert users[0]["email"] == "newuser@example.com"