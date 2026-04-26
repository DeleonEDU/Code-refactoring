"""
Власні виключення для бібліотечної системи.
"""


class LibraryException(Exception):
    """Базовий клас для всіх виключень бібліотечної системи."""
    pass


class BookNotFoundException(LibraryException):
    """Виникає коли книгу не знайдено."""

    def __init__(self, book_id: int):
        self.book_id = book_id
        super().__init__(f"Книгу з ID={book_id} не знайдено.")


class UserNotFoundException(LibraryException):
    """Виникає коли користувача не знайдено."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Користувача з ID={user_id} не знайдено.")


class BookNotAvailableException(LibraryException):
    """Виникає коли книга вже видана іншому користувачу."""

    def __init__(self, book_id: int):
        self.book_id = book_id
        super().__init__(f"Книга ID={book_id} наразі недоступна (вже видана).")


class BookNotBorrowedByUserException(LibraryException):
    """Виникає коли користувач намагається повернути книгу, яку він не брав."""

    def __init__(self, user_id: int, book_id: int):
        self.user_id = user_id
        self.book_id = book_id
        super().__init__(
            f"Користувач ID={user_id} не має книги ID={book_id} на руках."
        )


class UserAlreadyExistsException(LibraryException):
    """Виникає при спробі зареєструвати користувача з уже існуючим email."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Користувач з email '{email}' вже зареєстрований.")


class BookLimitExceededException(LibraryException):
    """Виникає коли користувач перевищив ліміт книг."""

    def __init__(self, user_id: int, limit: int):
        self.user_id = user_id
        self.limit = limit
        super().__init__(
            f"Користувач ID={user_id} досяг ліміту в {limit} книги."
        )


class DuplicateISBNException(LibraryException):
    """Виникає при спробі додати книгу з уже існуючим ISBN."""

    def __init__(self, isbn: str):
        self.isbn = isbn
        super().__init__(f"Книга з ISBN '{isbn}' вже існує в системі.")
