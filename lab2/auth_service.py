from models import UserSchema
from database import users_db

class AuthService:
    def get_or_create_user(self, user_data: UserSchema):
        # Шукаємо існуючого
        for u in users_db:
            if u['email'] == user_data.email:
                return u
        
        # Створюємо нового
        new_user = {
            'id': len(users_db) + 1,
            'email': user_data.email,
            'role': user_data.role,
            'password': user_data.password
        }
        users_db.append(new_user)
        return new_user