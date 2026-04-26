"""
Контролер бібліотечної системи.

Виступає точкою входу для взаємодії з користувачем через CLI.
Не містить бізнес-логіки — лише делегує виклики до LibraryService
та форматує виведення результатів.
"""

from src.services.library_service import LibraryService
from src.services.exceptions import LibraryException
from src.dto.library_dto import (
    BorrowBookDTO,
    ReturnBookDTO,
    RegisterUserDTO,
    SearchBookDTO,
)


class LibraryController:
    """
    CLI-контролер бібліотеки.

    Приймає команди від користувача, передає їх сервісу
    та виводить результат на екран.
    """

    def __init__(self, service: LibraryService) -> None:
        self._service = service

    def cmd_register_user(self, name: str, email: str) -> None:
        """Команда: зареєструвати нового користувача."""
        try:
            dto = RegisterUserDTO(name=name, email=email)
            user = self._service.register_user(dto)
            print(f"Користувача зареєстровано: ID={user.id}, {user.name} ({user.email})")
        except LibraryException as e:
            print(f"Помилка: {e}")
        except ValueError as e:
            print(f"Валідація: {e}")

    def cmd_add_book(self, title: str, author: str, isbn: str) -> None:
        """Команда: додати книгу до бібліотеки."""
        try:
            book = self._service.add_book(title, author, isbn)
            print(f"Книгу додано: ID={book.id}, '{book.title}' — {book.author}")
        except LibraryException as e:
            print(f"Помилка: {e}")
        except ValueError as e:
            print(f"Валідація: {e}")

    def cmd_issue_book(self, user_id: int, book_id: int) -> None:
        """Команда: видати книгу користувачу."""
        try:
            dto = BorrowBookDTO(user_id=user_id, book_id=book_id)
            book = self._service.issue_book(dto)
            print(f"Книгу видано: '{book.title}' → користувач ID={user_id}")
        except LibraryException as e:
            print(f"Помилка: {e}")

    def cmd_return_book(self, user_id: int, book_id: int) -> None:
        """Команда: прийняти повернення книги."""
        try:
            dto = ReturnBookDTO(user_id=user_id, book_id=book_id)
            book = self._service.return_book(dto)
            print(f"Книгу повернено: '{book.title}' (тепер доступна)")
        except LibraryException as e:
            print(f"Помилка: {e}")

    def cmd_search_books(
        self,
        title: str = None,
        author: str = None,
        isbn: str = None,
    ) -> None:
        """Команда: пошук книг."""
        dto = SearchBookDTO(title=title, author=author, isbn=isbn)
        books = self._service.search_books(dto)
        if not books:
            print("Книг за вказаними критеріями не знайдено.")
            return
        print(f"Знайдено книг: {len(books)}")
        for book in books:
            status = "доступна" if book.is_available else "видана"
            print(f"  [{book.id}] '{book.title}' — {book.author} | ISBN: {book.isbn} | {status}")

    def cmd_list_available(self) -> None:
        """Команда: показати всі доступні книги."""
        books = self._service.get_available_books()
        if not books:
            print("Немає доступних книг.")
            return
        print(f"Доступні книги ({len(books)}):")
        for book in books:
            print(f"  [{book.id}] '{book.title}' — {book.author}")

    def cmd_user_books(self, user_id: int) -> None:
        """Команда: показати книги конкретного користувача."""
        try:
            books = self._service.get_user_books(user_id)
            if not books:
                print(f"Користувач ID={user_id} не має виданих книг.")
                return
            print(f"Книги користувача ID={user_id} ({len(books)}):")
            for book in books:
                print(f"  [{book.id}] '{book.title}' — {book.author}")
        except LibraryException as e:
            print(f"Помилка: {e}")
