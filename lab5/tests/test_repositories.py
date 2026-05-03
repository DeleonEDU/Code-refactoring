"""
Юніт-тести для репозиторіїв.
"""

from src.models.book import Book
from src.models.user import User
from src.repositories.book_repository import BookRepository
from src.repositories.user_repository import UserRepository


class TestBookRepository:
    """Тести для BookRepository."""

    def test_save_and_find_by_id(self):
        repo = BookRepository()
        book = Book(id=0, title="Кобзар", author="Шевченко", isbn="TEST-001")
        saved = repo.save(book)

        found = repo.find_by_id(saved.id)

        assert found is not None
        assert found.title == "Кобзар"
        assert found.id > 0

    def test_find_by_id_not_found(self):
        repo = BookRepository()
        assert repo.find_by_id(999) is None

    def test_find_by_title(self):
        repo = BookRepository()
        repo.save(Book(id=0, title="Лісова пісня", author="Леся Українка", isbn="LES-001"))
        repo.save(Book(id=0, title="Лісовий кіт", author="Інший", isbn="LES-002"))
        repo.save(Book(id=0, title="Кобзар", author="Шевченко", isbn="KOB-001"))

        results = repo.find_by_title("Лісо")
        assert len(results) == 2

    def test_find_available(self):
        repo = BookRepository()
        b1 = repo.save(Book(id=0, title="A", author="A", isbn="A1", is_available=True))
        b2 = repo.save(Book(id=0, title="B", author="B", isbn="B1", is_available=False))

        available = repo.find_available()
        ids = [b.id for b in available]

        assert b1.id in ids
        assert b2.id not in ids

    def test_delete(self):
        repo = BookRepository()
        book = repo.save(Book(id=0, title="X", author="Y", isbn="Z1"))
        result = repo.delete(book.id)

        assert result is True
        assert repo.find_by_id(book.id) is None

    def test_exists_by_isbn(self):
        repo = BookRepository()
        repo.save(Book(id=0, title="Test", author="A", isbn="UNIQUE-ISBN"))

        assert repo.exists_by_isbn("UNIQUE-ISBN") is True
        assert repo.exists_by_isbn("NOT-EXISTS") is False


class TestUserRepository:
    """Тести для UserRepository."""

    def test_save_and_find_by_id(self):
        repo = UserRepository()
        user = User(id=0, name="Оля", email="ola@test.com")
        saved = repo.save(user)

        found = repo.find_by_id(saved.id)
        assert found is not None
        assert found.email == "ola@test.com"

    def test_find_by_email(self):
        repo = UserRepository()
        repo.save(User(id=0, name="Максим", email="max@test.com"))

        found = repo.find_by_email("max@test.com")
        assert found is not None
        assert found.name == "Максим"

    def test_find_by_email_case_insensitive(self):
        repo = UserRepository()
        repo.save(User(id=0, name="Аня", email="ANYA@TEST.COM"))

        found = repo.find_by_email("anya@test.com")
        assert found is not None

    def test_exists_by_email(self):
        repo = UserRepository()
        repo.save(User(id=0, name="Дмитро", email="dmytro@test.com"))

        assert repo.exists_by_email("dmytro@test.com") is True
        assert repo.exists_by_email("ghost@test.com") is False
