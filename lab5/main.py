"""
Демонстраційний запуск бібліотечної системи.
Показує роботу всіх 4 бізнес-сценаріїв через CLI контролер.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# pylint: disable=wrong-import-position
from src.repositories.book_repository import BookRepository  # noqa: E402
from src.repositories.user_repository import UserRepository  # noqa: E402
from src.services.library_service import LibraryService  # noqa: E402
from src.controllers.library_controller import LibraryController  # noqa: E402
# pylint: enable=wrong-import-position


def main():
    book_repo = BookRepository()
    user_repo = UserRepository()
    service = LibraryService(book_repo, user_repo)
    controller = LibraryController(service)

    print("=" * 60)
    print("       БІБЛІОТЕЧНА СИСТЕМА — ДЕМОНСТРАЦІЯ")
    print("=" * 60)

    print("\nРеєстрація користувачів:")
    controller.cmd_register_user("Іван Франко", "ivan@library.ua")
    controller.cmd_register_user("Леся Українка", "lesia@library.ua")
    controller.cmd_register_user("Іван Франко", "ivan@library.ua")

    print("\nДодавання книг:")
    controller.cmd_add_book("Кобзар", "Тарас Шевченко", "978-966-01-0001-1")
    controller.cmd_add_book("Лісова пісня", "Леся Українка", "978-966-01-0002-2")
    controller.cmd_add_book("Майстер і Маргарита", "Михайло Булгаков", "978-966-01-0003-3")
    controller.cmd_add_book("Кобзар", "Інший Автор", "978-966-01-0001-1")

    print("\nПошук книг:")
    controller.cmd_search_books(title="Кобзар")
    controller.cmd_search_books(author="Леся")
    controller.cmd_search_books(title="Гаррі Поттер")

    print("\nДоступні книги:")
    controller.cmd_list_available()

    print("\nВидача книг:")
    controller.cmd_issue_book(user_id=1, book_id=1)
    controller.cmd_issue_book(user_id=2, book_id=1)
    controller.cmd_issue_book(user_id=2, book_id=2)
    controller.cmd_issue_book(user_id=999, book_id=2)

    print("\nКниги Івана Франка:")
    controller.cmd_user_books(user_id=1)

    print("\nПовернення книг:")
    controller.cmd_return_book(user_id=1, book_id=1)
    controller.cmd_return_book(user_id=1, book_id=2)

    print("\nДоступні книги після повернення:")
    controller.cmd_list_available()

    print("\n" + "=" * 60)
    print("       ДЕМОНСТРАЦІЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    main()
