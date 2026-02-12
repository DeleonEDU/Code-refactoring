from fastapi import HTTPException, status
from models import PurchasePayload
from database import orders_db
from config import FRAUD_LIMIT_AMOUNT, Role
from auth_service import AuthService
from pricing_service import PricingService

class OrderService:
    def __init__(self):
        self.auth_service = AuthService()
        self.pricing_service = PricingService()

    def process_order(self, payload: PurchasePayload):
        # 1. Отримуємо юзера
        user = self.auth_service.get_or_create_user(payload.user)
        
        # 2. Рахуємо суму
        total_price = self.pricing_service.calculate_total(payload.items, user['role'])
        
        # 3. Перевіряємо фрод
        self._check_fraud(total_price, payload.payment, user['role'])
        
        # 4. Зберігаємо замовлення
        order = {
            'id': len(orders_db) + 1,
            'user_id': user['id'],
            'total': total_price,
            'items': [item.dict() for item in payload.items],
            'status': 'completed'
        }
        orders_db.append(order)
        
        return {
            "status": "success", 
            "total": total_price, 
            "order_id": order['id']
        }

    def _check_fraud(self, amount: float, payment_type: str, user_role: str):
        if payment_type == 'card' and amount > FRAUD_LIMIT_AMOUNT:
            if user_role == Role.NEW:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Limit exceeded"
                )