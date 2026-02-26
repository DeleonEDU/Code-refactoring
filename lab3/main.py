from fastapi import FastAPI
from models import PurchasePayload
from order_service import OrderService
from database import users_db

app = FastAPI()
order_service = OrderService()

@app.post("/buy")
def buy_items(payload: PurchasePayload):
    return order_service.process_order(payload)

@app.get("/users")
def get_users():
    return users_db