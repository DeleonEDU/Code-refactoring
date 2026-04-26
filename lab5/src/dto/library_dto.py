"""
Data Transfer Objects (DTO) для бібліотечної системи.
Використовуються для передачі даних між шарами.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BorrowBookDTO:
    """DTO для запиту на видачу книги."""

    user_id: int
    book_id: int


@dataclass
class ReturnBookDTO:
    """DTO для запиту на повернення книги."""

    user_id: int
    book_id: int


@dataclass
class RegisterUserDTO:
    """DTO для реєстрації нового користувача."""

    name: str
    email: str


@dataclass
class SearchBookDTO:
    """DTO для пошуку книги."""

    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None


@dataclass
class BookResponseDTO:
    """DTO відповіді з інформацією про книгу."""

    id: int
    title: str
    author: str
    isbn: str
    is_available: bool

    @classmethod
    def from_book(cls, book) -> "BookResponseDTO":
        return cls(
            id=book.id,
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            is_available=book.is_available,
        )


@dataclass
class UserResponseDTO:
    """DTO відповіді з інформацією про користувача."""

    id: int
    name: str
    email: str
    borrowed_books_count: int

    @classmethod
    def from_user(cls, user) -> "UserResponseDTO":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            borrowed_books_count=len(user.borrowed_book_ids),
        )
