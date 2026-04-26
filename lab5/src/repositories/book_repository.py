"""
Репозиторій для роботи з даними книг.
Відповідає за зберігання та отримання книг.
"""

from typing import Dict, List, Optional

from src.models.book import Book


class BookRepository:
    """
    Репозиторій книг — шар доступу до даних.

    Зберігає книги в пам'яті (in-memory), що імітує роботу з БД.
    У реальному проєкті тут були б запити до бази даних.
    """

    def __init__(self) -> None:
        self._storage: Dict[int, Book] = {}
        self._next_id: int = 1

    def save(self, book: Book) -> Book:
        """Зберігає або оновлює книгу у сховищі."""
        if book.id == 0:
            book.id = self._next_id
            self._next_id += 1
        self._storage[book.id] = book
        return book

    def find_by_id(self, book_id: int) -> Optional[Book]:
        """Повертає книгу за її ідентифікатором або None."""
        return self._storage.get(book_id)

    def find_by_title(self, title: str) -> List[Book]:
        """Повертає список книг, де назва містить вказаний рядок (регістр не враховується)."""
        title_lower = title.lower()
        return [
            book for book in self._storage.values()
            if title_lower in book.title.lower()
        ]

    def find_by_author(self, author: str) -> List[Book]:
        """Повертає список книг за автором (регістр не враховується)."""
        author_lower = author.lower()
        return [
            book for book in self._storage.values()
            if author_lower in book.author.lower()
        ]

    def find_by_isbn(self, isbn: str) -> Optional[Book]:
        """Повертає книгу за ISBN або None."""
        for book in self._storage.values():
            if book.isbn == isbn:
                return book
        return None

    def find_all(self) -> List[Book]:
        """Повертає всі книги зі сховища."""
        return list(self._storage.values())

    def find_available(self) -> List[Book]:
        """Повертає всі доступні (не видані) книги."""
        return [book for book in self._storage.values() if book.is_available]

    def delete(self, book_id: int) -> bool:
        """Видаляє книгу зі сховища. Повертає True якщо успішно."""
        if book_id in self._storage:
            del self._storage[book_id]
            return True
        return False

    def exists_by_isbn(self, isbn: str) -> bool:
        """Перевіряє чи існує книга з таким ISBN."""
        return self.find_by_isbn(isbn) is not None
