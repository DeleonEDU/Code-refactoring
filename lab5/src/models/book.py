"""
Модель книги для бібліотечної системи.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """Представляє книгу в бібліотеці."""

    id: int
    title: str
    author: str
    isbn: str
    is_available: bool = True
    borrowed_by_user_id: Optional[int] = None
    borrowed_at: Optional[datetime] = None

    def __repr__(self) -> str:
        status = "доступна" if self.is_available else f"видана (user_id={self.borrowed_by_user_id})"
        return f"Book(id={self.id}, title='{self.title}', author='{self.author}', status={status})"
