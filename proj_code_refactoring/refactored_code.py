from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

# ТЕХНІКА 2: Заміна магічних чисел символічними константами
DISCOUNT_TIER_1_THRESHOLD = 500
DISCOUNT_TIER_1_RATE = 0.95
DISCOUNT_TIER_2_THRESHOLD = 1000
DISCOUNT_TIER_2_RATE = 0.90
STANDARD_SHIPPING_COST = 50
FREE_SHIPPING_CITY = "Kyiv"


# ТЕХНІКА 5: Введення об'єкта параметра (Використання Pydantic для валідації)
# ТЕХНІКА 7: Видобування класу (Address)
class Address(BaseModel):
    street: str
    city: str
    zip_code: str = Field(alias="zip")


class OrderItem(BaseModel):
    price: float = Field(ge=0)
    qty: int = Field(ge=0)


class OrderRequest(BaseModel):
    user_id: int = Field(gt=0)
    items: List[OrderItem]
    address: Address


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total: float
    address: Address


app = FastAPI()


# ТЕХНІКА 10: Інкапсуляція колекції (Репозиторій)
class OrderRepository:
    def __init__(self):
        self._db: List[OrderResponse] = []

    def save(self, order: OrderResponse) -> None:
        self._db.append(order)

    def get_by_id(self, order_id: int) -> OrderResponse | None:
        return next((order for order in self._db if order.id == order_id), None)

    def get_next_id(self) -> int:
        return len(self._db) + 1


order_repo = OrderRepository()


# ТЕХНІКА 1: Видобування методу (Логіка знижок винесена окремо)
def calculate_discounted_total(items: List[OrderItem]) -> float:
    total = sum(item.price * item.qty for item in items)
    if total > DISCOUNT_TIER_2_THRESHOLD:
        return total * DISCOUNT_TIER_2_RATE
    if total > DISCOUNT_TIER_1_THRESHOLD:
        return total * DISCOUNT_TIER_1_RATE
    return total


# ТЕХНІКА 8: Переміщення методу (Логіка доставки винесена)
def calculate_shipping(city: str) -> float:
    if city == FREE_SHIPPING_CITY:
        return 0
    return STANDARD_SHIPPING_COST


# ТЕХНІКА 3: Перейменування методу (process_order замість p_o)
@app.post("/process_order", response_model=OrderResponse)
def process_order(request: OrderRequest):
    # ТЕХНІКА 6: Заміна вкладених умов на Guard Clauses (Реалізовано під капотом Pydantic)
    if not request.items:
        raise HTTPException(status_code=400, detail="No items provided")

    # ТЕХНІКА 9: Розщеплення тимчасової змінної (окремо знижка, окремо доставка)
    items_total = calculate_discounted_total(request.items)
    shipping_cost = calculate_shipping(request.address.city)
    final_total = items_total + shipping_cost

    order = OrderResponse(
        id=order_repo.get_next_id(),
        user_id=request.user_id,
        total=final_total,
        address=request.address,
    )
    order_repo.save(order)

    return order


@app.get("/order/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    order = order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
