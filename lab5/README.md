# Бібліотечна система — Лабораторна робота №5

## Опис проєкту

Система управління бібліотекою, реалізована на Python з дотриманням шаблону **Controller-Service-Repository**. Система реалізує 4 основні бізнес-сценарії та покрита 35 юніт-тестами.

---

## Структура проєкту

```
library_system/
├── src/
│   ├── models/
│   │   ├── book.py          # Модель книги
│   │   └── user.py          # Модель користувача
│   ├── repositories/
│   │   ├── book_repository.py   # Репозиторій книг
│   │   └── user_repository.py   # Репозиторій користувачів
│   ├── services/
│   │   ├── library_service.py   # Бізнес-логіка (головний сервіс)
│   │   └── exceptions.py        # Власні виключення
│   ├── controllers/
│   │   └── library_controller.py  # CLI-контролер
│   └── dto/
│       └── library_dto.py       # Data Transfer Objects
├── tests/
│   ├── test_library_service.py  # 25 тестів сервісу
│   └── test_repositories.py     # 10 тестів репозиторіїв
├── main.py                      # Демонстрація системи
├── pytest.ini                   # Конфігурація pytest
└── README.md
```

---

## Бізнес-сценарії

### 1. Видача книги (`issue_book`)
Користувач бере книгу з бібліотеки. Перевіряється:
- існування користувача і книги в системі
- доступність книги (не видана іншому)
- ліміт книг на руках (max 3)

### 2. Повернення книги (`return_book`)
Користувач повертає книгу. Перевіряється:
- існування користувача і книги
- що книга дійсно була видана саме цьому користувачу

### 3. Пошук книги (`search_books`)
Пошук за назвою, автором або ISBN. Регістр не враховується.

### 4. Реєстрація користувача (`register_user`)
Реєстрація нового читача. Перевіряється унікальність email.

---

## Встановлення та запуск

### Вимоги
- Python 3.8+
- pytest

### Встановлення залежностей
```bash
pip install pytest pylint
```

### Запуск тестів
```bash
# Усі тести з детальним виводом
pytest tests/ -v

# Тільки тести сервісу
pytest tests/test_library_service.py -v

# Тільки тести репозиторіїв
pytest tests/test_repositories.py -v

# Показати зведений результат
pytest tests/ -v --tb=short
```

### Запуск демонстрації
```bash
python main.py
```

### Перевірка якості коду (flake8)
```bash
pylint src/
```

---

## Результати тестів

```
============================= test session starts ==============================
collected 35 items

tests/test_library_service.py::TestIssueBook::test_issue_book_success PASSED
tests/test_library_service.py::TestIssueBook::test_issued_book_appears_in_user_list PASSED
tests/test_library_service.py::TestIssueBook::test_issue_book_user_not_found PASSED
tests/test_library_service.py::TestIssueBook::test_issue_book_book_not_found PASSED
tests/test_library_service.py::TestIssueBook::test_issue_already_borrowed_book PASSED
tests/test_library_service.py::TestIssueBook::test_issue_book_exceeds_limit PASSED
tests/test_library_service.py::TestReturnBook::test_return_book_success PASSED
tests/test_library_service.py::TestReturnBook::test_returned_book_removed_from_user_list PASSED
tests/test_library_service.py::TestReturnBook::test_return_book_not_borrowed_by_user PASSED
tests/test_library_service.py::TestReturnBook::test_return_book_user_not_found PASSED
tests/test_library_service.py::TestReturnBook::test_book_available_again_after_return PASSED
tests/test_library_service.py::TestSearchBooks::test_search_by_title_found PASSED
tests/test_library_service.py::TestSearchBooks::test_search_by_title_case_insensitive PASSED
tests/test_library_service.py::TestSearchBooks::test_search_by_author PASSED
tests/test_library_service.py::TestSearchBooks::test_search_by_isbn PASSED
tests/test_library_service.py::TestSearchBooks::test_search_not_found PASSED
tests/test_library_service.py::TestSearchBooks::test_search_all_when_no_criteria PASSED
tests/test_library_service.py::TestRegisterUser::test_register_user_success PASSED
tests/test_library_service.py::TestRegisterUser::test_register_duplicate_email PASSED
tests/test_library_service.py::TestRegisterUser::test_register_empty_name_raises PASSED
tests/test_library_service.py::TestRegisterUser::test_register_empty_email_raises PASSED
tests/test_library_service.py::TestAddBook::test_add_book_success PASSED
tests/test_library_service.py::TestAddBook::test_add_book_duplicate_isbn PASSED
tests/test_library_service.py::TestAddBook::test_add_book_empty_fields_raises PASSED
tests/test_library_service.py::TestGetAvailableBooks::test_available_books_excludes_issued PASSED
tests/test_repositories.py::TestBookRepository::test_save_and_find_by_id PASSED
tests/test_repositories.py::TestBookRepository::test_find_by_id_not_found PASSED
tests/test_repositories.py::TestBookRepository::test_find_by_title PASSED
tests/test_repositories.py::TestBookRepository::test_find_available PASSED
tests/test_repositories.py::TestBookRepository::test_delete PASSED
tests/test_repositories.py::TestBookRepository::test_exists_by_isbn PASSED
tests/test_repositories.py::TestUserRepository::test_save_and_find_by_id PASSED
tests/test_repositories.py::TestUserRepository::test_find_by_email PASSED
tests/test_repositories.py::TestUserRepository::test_find_by_email_case_insensitive PASSED
tests/test_repositories.py::TestUserRepository::test_exists_by_email PASSED

============================== 35 passed in 0.18s ==============================
```

## Результат pylint

```
------------------------------------------------------------------
Your code has been rated at 9.75/10
```
