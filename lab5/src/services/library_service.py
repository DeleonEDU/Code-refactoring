"""
Сервіс бібліотеки — шар бізнес-логіки.

Реалізує основні бізнес-сценарії:
  1. Видача книги (issue_book)
  2. Повернення книги (return_book)
  3. Пошук книги (search_books)
  4. Реєстрація користувача (register_user)
"""

from datetime import datetime
from typing import List

from src.models.book import Book
from src.models.user import User
from src.repositories.book_repository import BookRepository
from src.repositories.user_repository import UserRepository
from src.dto.library_dto import (
    BorrowBookDTO,
    ReturnBookDTO,
    RegisterUserDTO,
    SearchBookDTO,
    BookResponseDTO,
    UserResponseDTO,
)
from src.services.exceptions import (
    BookNotFoundException,
    UserNotFoundException,
    BookNotAvailableException,
    BookNotBorrowedByUserException,
    UserAlreadyExistsException,
    BookLimitExceededException,
    DuplicateISBNException,
)


class LibraryService:
    """
    Сервіс бібліотеки — містить усю бізнес-логіку.

    Залежить від BookRepository та UserRepository (ін'єкція залежностей),
    що дозволяє легко тестувати сервіс із мок-репозиторіями.
    """

    def __init__(
        self,
        book_repository: BookRepository,
        user_repository: UserRepository,
    ) -> None:
        self._book_repo = book_repository
        self._user_repo = user_repository

    def issue_book(self, dto: BorrowBookDTO) -> BookResponseDTO:
        """
        Видає книгу користувачу.

        Бізнес-правила:
          - Користувач повинен існувати в системі.
          - Книга повинна існувати в системі.
          - Книга повинна бути доступною (не видана).
          - Користувач не може мати більше MAX_BOOKS_ALLOWED книг одночасно.

        Raises:
            UserNotFoundException: Користувача не знайдено.
            BookNotFoundException: Книгу не знайдено.
            BookNotAvailableException: Книга вже видана.
            BookLimitExceededException: Перевищено ліміт книг.
        """
        user = self._get_user_or_raise(dto.user_id)
        book = self._get_book_or_raise(dto.book_id)

        if not book.is_available:
            raise BookNotAvailableException(dto.book_id)

        if len(user.borrowed_book_ids) >= User.MAX_BOOKS_ALLOWED:
            raise BookLimitExceededException(dto.user_id, User.MAX_BOOKS_ALLOWED)

        book.is_available = False
        book.borrowed_by_user_id = user.id
        book.borrowed_at = datetime.now()
        self._book_repo.save(book)

        user.borrowed_book_ids.append(book.id)
        self._user_repo.save(user)

        return BookResponseDTO.from_book(book)

    def return_book(self, dto: ReturnBookDTO) -> BookResponseDTO:
        """
        Повертає книгу до бібліотеки.

        Бізнес-правила:
          - Користувач повинен існувати.
          - Книга повинна існувати.
          - Книга повинна бути у списку виданих саме цьому користувачу.

        Raises:
            UserNotFoundException: Користувача не знайдено.
            BookNotFoundException: Книгу не знайдено.
            BookNotBorrowedByUserException: Книга не належить цьому користувачу.
        """
        user = self._get_user_or_raise(dto.user_id)
        book = self._get_book_or_raise(dto.book_id)

        if book.id not in user.borrowed_book_ids:
            raise BookNotBorrowedByUserException(dto.user_id, dto.book_id)

        book.is_available = True
        book.borrowed_by_user_id = None
        book.borrowed_at = None
        self._book_repo.save(book)

        user.borrowed_book_ids.remove(book.id)
        self._user_repo.save(user)

        return BookResponseDTO.from_book(book)

    def search_books(self, dto: SearchBookDTO) -> List[BookResponseDTO]:
        """
        Шукає книги за назвою, автором або ISBN.

        Якщо передано кілька критеріїв — повертає результати першого непорожнього.
        Якщо жодного критерію не вказано — повертає всі книги.

        Returns:
            Список BookResponseDTO, що відповідають критеріям пошуку.
        """
        if dto.isbn:
            book = self._book_repo.find_by_isbn(dto.isbn)
            books = [book] if book else []
        elif dto.title:
            books = self._book_repo.find_by_title(dto.title)
        elif dto.author:
            books = self._book_repo.find_by_author(dto.author)
        else:
            books = self._book_repo.find_all()

        return [BookResponseDTO.from_book(b) for b in books]

    def get_available_books(self) -> List[BookResponseDTO]:
        """Повертає всі доступні для видачі книги."""
        books = self._book_repo.find_available()
        return [BookResponseDTO.from_book(b) for b in books]

    def register_user(self, dto: RegisterUserDTO) -> UserResponseDTO:
        """
        Реєструє нового користувача бібліотеки.

        Бізнес-правила:
          - Email повинен бути унікальним у системі.
          - Ім'я та email є обов'язковими полями.

        Raises:
            UserAlreadyExistsException: Користувач з таким email вже існує.
            ValueError: Порожнє ім'я або email.
        """
        name = dto.name.strip()
        email = dto.email.strip()

        if not name:
            raise ValueError("Ім'я користувача не може бути порожнім.")
        if not email:
            raise ValueError("Email користувача не може бути порожнім.")

        if self._user_repo.exists_by_email(email):
            raise UserAlreadyExistsException(email)

        user = User(id=0, name=name, email=email)
        saved_user = self._user_repo.save(user)

        return UserResponseDTO.from_user(saved_user)

    def add_book(self, title: str, author: str, isbn: str) -> BookResponseDTO:
        """
        Додає нову книгу до бібліотеки.

        Raises:
            DuplicateISBNException: Книга з таким ISBN вже існує.
            ValueError: Порожні обов'язкові поля.
        """
        if not title.strip() or not author.strip() or not isbn.strip():
            raise ValueError("Назва, автор та ISBN є обов'язковими полями.")

        if self._book_repo.exists_by_isbn(isbn):
            raise DuplicateISBNException(isbn)

        book = Book(id=0, title=title.strip(), author=author.strip(), isbn=isbn.strip())
        saved_book = self._book_repo.save(book)

        return BookResponseDTO.from_book(saved_book)

    def get_user_books(self, user_id: int) -> List[BookResponseDTO]:
        """Повертає список книг, виданих конкретному користувачу."""
        user = self._get_user_or_raise(user_id)
        books = []
        for book_id in user.borrowed_book_ids:
            book = self._book_repo.find_by_id(book_id)
            if book:
                books.append(BookResponseDTO.from_book(book))
        return books

    def _get_user_or_raise(self, user_id: int) -> User:
        """Повертає користувача або піднімає UserNotFoundException."""
        user = self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        return user

    def _get_book_or_raise(self, book_id: int) -> Book:
        """Повертає книгу або піднімає BookNotFoundException."""
        book = self._book_repo.find_by_id(book_id)
        if book is None:
            raise BookNotFoundException(book_id)
        return book
