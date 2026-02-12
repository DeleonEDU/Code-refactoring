import datetime
from typing import List
from models import ItemSchema
from config import (
    Category, Role, VIP_DISCOUNT_RATE, ADMIN_DISCOUNT_RATE,
    SATURDAY_DISCOUNT_AMOUNT, SATURDAY_WEEKDAY_INDEX
)

class PricingService:
    def calculate_total(self, items: List[ItemSchema], user_role: str) -> float:
        total = 0.0
        for item in items:
            total += self._calculate_item_price(item, user_role)
        return total

    def _calculate_item_price(self, item: ItemSchema, user_role: str) -> float:
        price = item.price
        
        # Електроніка
        if item.category == Category.ELECTRONICS:
            if user_role == Role.VIP:
                price *= VIP_DISCOUNT_RATE
            elif user_role == Role.ADMIN:
                price *= ADMIN_DISCOUNT_RATE
        
        # Одяг
        elif item.category == Category.CLOTHING:
            if self._is_discount_day():
                price -= SATURDAY_DISCOUNT_AMOUNT
        
        return max(price, 0)

    def _is_discount_day(self) -> bool:
        return datetime.datetime.now().weekday() == SATURDAY_WEEKDAY_INDEX