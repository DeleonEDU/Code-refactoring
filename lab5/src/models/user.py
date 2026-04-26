"""
Модель користувача для бібліотечної системи.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class User:
    """Представляє зареєстрованого користувача бібліотеки."""

    id: int
    name: str
    email: str
    borrowed_book_ids: List[int] = field(default_factory=list)

    MAX_BOOKS_ALLOWED = 3

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, name='{self.name}', "
            f"email='{self.email}', borrowed={self.borrowed_book_ids})"
        )
