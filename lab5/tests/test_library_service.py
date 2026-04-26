"""
Юніт-тести для LibraryService.

Покривають усі 4 бізнес-сценарії (позитивні та негативні випадки):
  1. Видача книги
  2. Повернення книги
  3. Пошук книги
  4. Реєстрація користувача

Запуск: pytest tests/ -v
"""

import pytest
from src.models.book import Book
from src.models.user import User
from src.repositories.book_repository import BookRepository
from src.repositories.user_repository import UserRepository
from src.services.library_service import LibraryService
from src.services.exceptions import (
    BookNotFoundException,
    UserNotFoundException,
    BookNotAvailableException,
    BookNotBorrowedByUserException,
    UserAlreadyExistsException,
    BookLimitExceededException,
    DuplicateISBNException,
)
from src.dto.library_dto import (
    BorrowBookDTO,
    ReturnBookDTO,
    RegisterUserDTO,
    SearchBookDTO,
)


@pytest.fixture
def book_repo() -> BookRepository:
    """Чистий репозиторій книг для кожного тесту."""
    return BookRepository()


@pytest.fixture
def user_repo() -> UserRepository:
    """Чистий репозиторій користувачів для кожного тесту."""
    return UserRepository()


@pytest.fixture
def service(book_repo: BookRepository, user_repo: UserRepository) -> LibraryService:
    """Сервіс із чистими репозиторіями."""
    return LibraryService(book_repo, user_repo)


@pytest.fixture
def sample_book(book_repo: BookRepository) -> Book:
    """Збережена тестова книга."""
    book = Book(id=0, title="Майстер і Маргарита", author="Булгаков", isbn="978-966-03-1234-5")
    return book_repo.save(book)


@pytest.fixture
def sample_user(user_repo: UserRepository) -> User:
    """Збережений тестовий користувач."""
    user = User(id=0, name="Іван Франко", email="ivan@example.com")
    return user_repo.save(user)


class TestIssueBook:
    """Тести для бізнес-логіки видачі книги."""

    def test_issue_book_success(self, service, sample_user, sample_book):
        """Позитивний: успішна видача книги читачу."""
        dto = BorrowBookDTO(user_id=sample_user.id, book_id=sample_book.id)
        result = service.issue_book(dto)

        assert result.id == sample_book.id
        assert result.is_available is False

    def test_issued_book_appears_in_user_list(self, service, user_repo, sample_user, sample_book):
        """Позитивний: книга з'являється у списку виданих користувача."""
        dto = BorrowBookDTO(user_id=sample_user.id, book_id=sample_book.id)
        service.issue_book(dto)

        updated_user = user_repo.find_by_id(sample_user.id)
        assert sample_book.id in updated_user.borrowed_book_ids

    def test_issue_book_user_not_found(self, service, sample_book):
        """Негативний: видача книги неіснуючому користувачу."""
        dto = BorrowBookDTO(user_id=999, book_id=sample_book.id)

        with pytest.raises(UserNotFoundException) as exc_info:
            service.issue_book(dto)

        assert exc_info.value.user_id == 999

    def test_issue_book_book_not_found(self, service, sample_user):
        """Негативний: видача неіснуючої книги."""
        dto = BorrowBookDTO(user_id=sample_user.id, book_id=999)

        with pytest.raises(BookNotFoundException) as exc_info:
            service.issue_book(dto)

        assert exc_info.value.book_id == 999

    def test_issue_already_borrowed_book(self, service, user_repo, sample_book):
        """Негативний: спроба видати книгу, яка вже видана."""
        user1 = user_repo.save(User(id=0, name="Олег", email="oleg@test.com"))
        user2 = user_repo.save(User(id=0, name="Марія", email="maria@test.com"))

        service.issue_book(BorrowBookDTO(user_id=user1.id, book_id=sample_book.id))

        with pytest.raises(BookNotAvailableException) as exc_info:
            service.issue_book(BorrowBookDTO(user_id=user2.id, book_id=sample_book.id))

        assert exc_info.value.book_id == sample_book.id

    def test_issue_book_exceeds_limit(self, service, book_repo, sample_user):
        """Негативний: перевищення ліміту книг для користувача."""
        books = []
        for i in range(4):
            book = book_repo.save(
                Book(id=0, title=f"Книга {i}", author="Автор", isbn=f"ISBN-{i:03d}")
            )
            books.append(book)

        for book in books[:3]:
            service.issue_book(BorrowBookDTO(user_id=sample_user.id, book_id=book.id))

        with pytest.raises(BookLimitExceededException) as exc_info:
            service.issue_book(BorrowBookDTO(user_id=sample_user.id, book_id=books[3].id))

        assert exc_info.value.limit == User.MAX_BOOKS_ALLOWED


class TestReturnBook:
    """Тести для бізнес-логіки повернення книги."""

    def test_return_book_success(self, service, book_repo, sample_user, sample_book):
        """Позитивний: успішне повернення книги."""

        service.issue_book(BorrowBookDTO(user_id=sample_user.id, book_id=sample_book.id))

        dto = ReturnBookDTO(user_id=sample_user.id, book_id=sample_book.id)
        result = service.return_book(dto)

        assert result.is_available is True
        book_in_repo = book_repo.find_by_id(sample_book.id)
        assert book_in_repo.is_available is True
        assert book_in_repo.borrowed_by_user_id is None

    def test_returned_book_removed_from_user_list(self, service, user_repo, sample_user, sample_book):
        """Позитивний: книга зникає зі списку користувача після повернення."""
        service.issue_book(BorrowBookDTO(user_id=sample_user.id, book_id=sample_book.id))
        service.return_book(ReturnBookDTO(user_id=sample_user.id, book_id=sample_book.id))

        updated_user = user_repo.find_by_id(sample_user.id)
        assert sample_book.id not in updated_user.borrowed_book_ids

    def test_return_book_not_borrowed_by_user(self, service, user_repo, sample_book):
        """Негативний: повернення книги, яку цей користувач не брав."""
        other_user = user_repo.save(User(id=0, name="Петро", email="petro@test.com"))
        wrong_user = user_repo.save(User(id=0, name="Оксана", email="oksana@test.com"))

        service.issue_book(BorrowBookDTO(user_id=other_user.id, book_id=sample_book.id))

        with pytest.raises(BookNotBorrowedByUserException) as exc_info:
            service.return_book(ReturnBookDTO(user_id=wrong_user.id, book_id=sample_book.id))

        assert exc_info.value.user_id == wrong_user.id
        assert exc_info.value.book_id == sample_book.id

    def test_return_book_user_not_found(self, service, sample_book):
        """Негативний: повернення від неіснуючого користувача."""
        with pytest.raises(UserNotFoundException):
            service.return_book(ReturnBookDTO(user_id=999, book_id=sample_book.id))

    def test_book_available_again_after_return(self, service, user_repo, book_repo, sample_user, sample_book):
        """Позитивний: після повернення книгу можна видати знову."""
        service.issue_book(BorrowBookDTO(user_id=sample_user.id, book_id=sample_book.id))
        service.return_book(ReturnBookDTO(user_id=sample_user.id, book_id=sample_book.id))

        second_user = user_repo.save(User(id=0, name="Другий", email="second@test.com"))
        result = service.issue_book(BorrowBookDTO(user_id=second_user.id, book_id=sample_book.id))

        assert result.is_available is False


class TestSearchBooks:
    """Тести для бізнес-логіки пошуку книг."""

    def test_search_by_title_found(self, service, book_repo):
        """Позитивний: пошук за назвою повертає правильний результат."""
        book_repo.save(Book(id=0, title="Кобзар", author="Шевченко", isbn="ISBN-001"))
        book_repo.save(Book(id=0, title="Лісова пісня", author="Леся Українка", isbn="ISBN-002"))

        results = service.search_books(SearchBookDTO(title="Кобзар"))

        assert len(results) == 1
        assert results[0].title == "Кобзар"

    def test_search_by_title_case_insensitive(self, service, book_repo):
        """Позитивний: пошук нечутливий до регістру."""
        book_repo.save(Book(id=0, title="Майстер і Маргарита", author="Булгаков", isbn="ISBN-003"))

        results = service.search_books(SearchBookDTO(title="майстер"))

        assert len(results) == 1

    def test_search_by_author(self, service, book_repo):
        """Позитивний: пошук за автором."""
        book_repo.save(Book(id=0, title="Кобзар", author="Шевченко", isbn="ISBN-004"))
        book_repo.save(Book(id=0, title="Гайдамаки", author="Шевченко", isbn="ISBN-005"))
        book_repo.save(Book(id=0, title="Лісова пісня", author="Леся Українка", isbn="ISBN-006"))

        results = service.search_books(SearchBookDTO(author="Шевченко"))

        assert len(results) == 2

    def test_search_by_isbn(self, service, book_repo):
        """Позитивний: пошук за ISBN."""
        book_repo.save(Book(id=0, title="Тест", author="Автор", isbn="978-123-456"))

        results = service.search_books(SearchBookDTO(isbn="978-123-456"))

        assert len(results) == 1
        assert results[0].isbn == "978-123-456"

    def test_search_not_found(self, service, book_repo):
        """Негативний: пошук без результатів."""
        book_repo.save(Book(id=0, title="Кобзар", author="Шевченко", isbn="ISBN-007"))

        results = service.search_books(SearchBookDTO(title="Гаррі Поттер"))

        assert results == []

    def test_search_all_when_no_criteria(self, service, book_repo):
        """Позитивний: без критеріїв повертає всі книги."""
        book_repo.save(Book(id=0, title="Книга 1", author="Автор 1", isbn="ISBN-A"))
        book_repo.save(Book(id=0, title="Книга 2", author="Автор 2", isbn="ISBN-B"))

        results = service.search_books(SearchBookDTO())

        assert len(results) == 2


class TestRegisterUser:
    """Тести для бізнес-логіки реєстрації користувача."""

    def test_register_user_success(self, service):
        """Позитивний: успішна реєстрація нового користувача."""
        dto = RegisterUserDTO(name="Тарас Шевченко", email="taras@kobzar.ua")
        result = service.register_user(dto)

        assert result.id > 0
        assert result.name == "Тарас Шевченко"
        assert result.email == "taras@kobzar.ua"
        assert result.borrowed_books_count == 0

    def test_register_duplicate_email(self, service):
        """Негативний: реєстрація з уже існуючим email."""
        email = "duplicate@test.com"
        service.register_user(RegisterUserDTO(name="Перший", email=email))

        with pytest.raises(UserAlreadyExistsException) as exc_info:
            service.register_user(RegisterUserDTO(name="Другий", email=email))

        assert exc_info.value.email == email

    def test_register_empty_name_raises(self, service):
        """Негативний: реєстрація з порожнім іменем."""
        with pytest.raises(ValueError):
            service.register_user(RegisterUserDTO(name="   ", email="valid@test.com"))

    def test_register_empty_email_raises(self, service):
        """Негативний: реєстрація з порожнім email."""
        with pytest.raises(ValueError):
            service.register_user(RegisterUserDTO(name="Ім'я", email="   "))


class TestAddBook:
    """Тести для додавання книг до бібліотеки."""

    def test_add_book_success(self, service):
        """Позитивний: успішне додавання книги."""
        result = service.add_book("Нова книга", "Автор", "978-000-001")

        assert result.id > 0
        assert result.title == "Нова книга"
        assert result.is_available is True

    def test_add_book_duplicate_isbn(self, service):
        """Негативний: додавання книги з дублікатом ISBN."""
        service.add_book("Перша книга", "Автор", "ISBN-UNIQUE")

        with pytest.raises(DuplicateISBNException) as exc_info:
            service.add_book("Друга книга з тим самим ISBN", "Автор 2", "ISBN-UNIQUE")

        assert exc_info.value.isbn == "ISBN-UNIQUE"

    def test_add_book_empty_fields_raises(self, service):
        """Негативний: порожні поля при додаванні книги."""
        with pytest.raises(ValueError):
            service.add_book("", "Автор", "ISBN-X")


class TestGetAvailableBooks:
    """Тести для отримання доступних книг."""

    def test_available_books_excludes_issued(self, service, book_repo, user_repo):
        """Позитивний: видана книга не відображається у доступних."""
        book1 = book_repo.save(Book(id=0, title="Книга 1", author="Авт", isbn="A-001"))
        book2 = book_repo.save(Book(id=0, title="Книга 2", author="Авт", isbn="A-002"))
        user = user_repo.save(User(id=0, name="Читач", email="reader@test.com"))

        service.issue_book(BorrowBookDTO(user_id=user.id, book_id=book1.id))

        available = service.get_available_books()
        available_ids = [b.id for b in available]

        assert book1.id not in available_ids
        assert book2.id in available_ids
