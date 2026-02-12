from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import datetime

app = FastAPI()

# Імітація бази даних (Global state - це вже погано)
users_db = []
orders_db = []

# GOD OBJECT (Великий клас): Цей клас робить все: валідацію, роботу з БД, бізнес-логіку
class ShopManager:
    def process_transaction(self, user_data: dict, order_items: List[dict], payment_type: str):
        # 1. Створення або пошук користувача (змішана відповідальність)
        user_found = False
        for u in users_db:
            if u['email'] == user_data['email']:
                user_found = True
                current_user = u
                break
        
        if not user_found:
            # DUPLICATE CODE: Валідація і створення юзера повторюється в інших місцях
            if len(user_data['password']) < 8: # Magic number
                raise HTTPException(status_code=400, detail="Password too short")
            if '@' not in user_data['email']:
                raise HTTPException(status_code=400, detail="Invalid email")
            
            new_user = {
                'id': len(users_db) + 1,
                'email': user_data['email'],
                'role': user_data.get('role', 'customer'),
                'password': user_data['password']
            }
            users_db.append(new_user)
            current_user = new_user

        # 2. Розрахунок ціни (COMPLEXITY + MAGIC NUMBERS)
        total_price = 0
        for item in order_items:
            price = item['price']
            
            # Hardcoded logic for categories
            if item['category'] == 1: # Що таке 1? (Magic Number) - Електроніка?
                if current_user['role'] == 'vip':
                    price = price * 0.90 # Знижка 10%
                elif current_user['role'] == 'admin':
                    price = price * 0.50 # Знижка 50%
            elif item['category'] == 2: # Одяг?
                if datetime.datetime.now().weekday() == 5: # Субота?
                    price = price - 10 # Знижка 10 грн
            
            total_price += price

        # 3. Обробка оплати (COMPLEXITY)
        if payment_type == 'card':
            if total_price > 5000: # Magic number
                print("Fraud check required...") # Side effect
                if current_user['role'] == 'new':
                    raise HTTPException(status_code=403, detail="Limit exceeded")
        elif payment_type == 'bonus':
            # Ще одна логіка...
            pass
        
        # 4. Збереження замовлення
        order = {
            'id': len(orders_db) + 1,
            'user_id': current_user['id'],
            'total': total_price,
            'items': order_items,
            'status': 'completed'
        }
        orders_db.append(order)
        return {"status": "success", "total": total_price, "order_id": order['id']}

manager = ShopManager()

@app.post("/buy")
def buy_items(payload: dict):
    # Payload очікує: {"user": {...}, "items": [...], "payment":Str}
    # Погана практика: передача dict замість Pydantic models
    return manager.process_transaction(payload['user'], payload['items'], payload['payment'])

@app.get("/users")
def get_users():
    return users_db