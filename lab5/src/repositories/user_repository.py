"""
Репозиторій для роботи з даними користувачів.
"""

from typing import Dict, List, Optional

from src.models.user import User


class UserRepository:
    """
    Репозиторій користувачів — шар доступу до даних.

    Зберігає користувачів в пам'яті (in-memory).
    """

    def __init__(self) -> None:
        self._storage: Dict[int, User] = {}
        self._next_id: int = 1

    def save(self, user: User) -> User:
        """Зберігає або оновлює користувача у сховищі."""
        if user.id == 0:
            user.id = self._next_id
            self._next_id += 1
        self._storage[user.id] = user
        return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Повертає користувача за його ідентифікатором або None."""
        return self._storage.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        """Повертає користувача за email або None."""
        for user in self._storage.values():
            if user.email.lower() == email.lower():
                return user
        return None

    def find_all(self) -> List[User]:
        """Повертає всіх користувачів."""
        return list(self._storage.values())

    def exists_by_email(self, email: str) -> bool:
        """Перевіряє чи існує користувач з таким email."""
        return self.find_by_email(email) is not None

    def delete(self, user_id: int) -> bool:
        """Видаляє користувача. Повертає True якщо успішно."""
        if user_id in self._storage:
            del self._storage[user_id]
            return True
        return False
