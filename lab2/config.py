from enum import IntEnum, Enum

# Константи
VIP_DISCOUNT_RATE = 0.90
ADMIN_DISCOUNT_RATE = 0.50
SATURDAY_DISCOUNT_AMOUNT = 10
FRAUD_LIMIT_AMOUNT = 5000
MIN_PASSWORD_LENGTH = 8
SATURDAY_WEEKDAY_INDEX = 5

# Enums
class Category(IntEnum):
    ELECTRONICS = 1
    CLOTHING = 2

class Role(str, Enum):
    CUSTOMER = "customer"
    VIP = "vip"
    ADMIN = "admin"
    NEW = "new"