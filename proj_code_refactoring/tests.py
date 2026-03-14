import pytest
from fastapi.testclient import TestClient

# Імпортуємо відрефакторений додаток (замініть на original_code для перевірки старого)
from refactored_code import app, order_repo

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    # Очищуємо імітовану БД перед кожним тестом
    order_repo._db.clear()


# 1-3. Тести на знижки
def test_order_no_discount():
    payload = {
        "user_id": 1,
        "items": [{"price": 100, "qty": 2}],
        "street": "Main",
        "city": "Lviv",
        "zip": "79000",
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    response = client.post("/process_order", json=payload)
    assert response.status_code == 200
    assert response.json()["total"] == 250.0  # 200 + 50 доставка


def test_order_tier1_discount():
    payload = {
        "user_id": 1,
        "items": [{"price": 300, "qty": 2}],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    response = client.post("/process_order", json=payload)
    assert response.json()["total"] == 600 * 0.95 + 50


def test_order_tier2_discount():
    payload = {
        "user_id": 1,
        "items": [{"price": 600, "qty": 2}],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    response = client.post("/process_order", json=payload)
    assert response.json()["total"] == 1200 * 0.9 + 50


# 4-5. Тести на доставку
def test_free_shipping_kyiv():
    payload = {
        "user_id": 1,
        "items": [{"price": 100, "qty": 1}],
        "address": {"street": "Khreshchatyk", "city": "Kyiv", "zip": "01001"},
    }
    response = client.post("/process_order", json=payload)
    assert response.json()["total"] == 100.0  # Безкоштовна доставка


def test_paid_shipping_other_city():
    payload = {
        "user_id": 1,
        "items": [{"price": 100, "qty": 1}],
        "address": {"street": "Deribasivska", "city": "Odesa", "zip": "65000"},
    }
    response = client.post("/process_order", json=payload)
    assert response.json()["total"] == 150.0  # 100 + 50


# 6-8. Валідація користувача
def test_missing_user_id():
    payload = {
        "items": [{"price": 100, "qty": 1}],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    assert client.post("/process_order", json=payload).status_code == 422


def test_zero_user_id():
    payload = {
        "user_id": 0,
        "items": [{"price": 100, "qty": 1}],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    assert client.post("/process_order", json=payload).status_code == 422


def test_negative_user_id():
    payload = {
        "user_id": -5,
        "items": [{"price": 100, "qty": 1}],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    assert client.post("/process_order", json=payload).status_code == 422


# 9-11. Валідація товарів (Items)
def test_missing_items():
    payload = {
        "user_id": 1,
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    assert client.post("/process_order", json=payload).status_code == 422


def test_empty_items_list():
    payload = {
        "user_id": 1,
        "items": [],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    assert client.post("/process_order", json=payload).status_code == 400


def test_item_missing_price():
    payload = {
        "user_id": 1,
        "items": [{"qty": 1}],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    assert client.post("/process_order", json=payload).status_code == 422


# 12-14. Валідація значень товарів
def test_item_negative_price():
    payload = {
        "user_id": 1,
        "items": [{"price": -10, "qty": 1}],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    assert client.post("/process_order", json=payload).status_code == 422


def test_item_zero_qty():
    payload = {
        "user_id": 1,
        "items": [{"price": 10, "qty": 0}],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    response = client.post("/process_order", json=payload)
    assert response.status_code == 200  # Дозволено 0 кількість, але сума 0
    assert response.json()["total"] == 50.0


def test_item_negative_qty():
    payload = {
        "user_id": 1,
        "items": [{"price": 10, "qty": -1}],
        "address": {"street": "Main", "city": "Lviv", "zip": "79000"},
    }
    assert client.post("/process_order", json=payload).status_code == 422


# 15-17. Валідація адреси
def test_missing_address():
    payload = {"user_id": 1, "items": [{"price": 100, "qty": 1}]}
    assert client.post("/process_order", json=payload).status_code == 422


def test_missing_city_in_address():
    payload = {
        "user_id": 1,
        "items": [{"price": 100, "qty": 1}],
        "address": {"street": "Main", "zip": "79000"},
    }
    assert client.post("/process_order", json=payload).status_code == 422


def test_missing_zip_in_address():
    payload = {
        "user_id": 1,
        "items": [{"price": 100, "qty": 1}],
        "address": {"street": "Main", "city": "Lviv"},
    }
    assert client.post("/process_order", json=payload).status_code == 422


# 18-20. Отримання замовлень (GET)
def test_get_order_success():
    payload = {
        "user_id": 1,
        "items": [{"price": 100, "qty": 1}],
        "address": {"street": "Main", "city": "Kyiv", "zip": "01001"},
    }
    create_resp = client.post("/process_order", json=payload)
    order_id = create_resp.json()["id"]

    get_resp = client.get(f"/order/{order_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["user_id"] == 1


def test_get_order_not_found():
    assert client.get("/order/999").status_code == 404


def test_multiple_orders_increment_id():
    payload = {
        "user_id": 1,
        "items": [{"price": 100, "qty": 1}],
        "address": {"street": "Main", "city": "Kyiv", "zip": "01001"},
    }
    resp1 = client.post("/process_order", json=payload)
    resp2 = client.post("/process_order", json=payload)
    assert resp1.json()["id"] == 1
    assert resp2.json()["id"] == 2
