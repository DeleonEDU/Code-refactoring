"""
Unit Tests for Library Management System
Compatible with both original_code.py and refactored_code.py logic.
Run: pytest tests/test_cases.py -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


from refactored_code import (
    app,
    books,
    users,
    loans,
    reservations,
    calculate_fine,
    get_loan_period_days,
    get_max_loans,
    get_active_loans_for_user,
    expire_stale_reservations,
    fulfill_reservation_if_exists,
    MembershipType,
    _next_id,
)
import refactored_code as rc


@pytest.fixture(autouse=True)
def clear_state():
    """Reset all in-memory state before each test."""
    books.clear()
    users.clear()
    loans.clear()
    reservations.clear()
    rc._book_counter = 0
    rc._user_counter = 0
    rc._loan_counter = 0
    rc._reservation_counter = 0
    yield


client = TestClient(app)


# ────────────────────────────────────────────────
# BOOK TESTS (1–5)
# ────────────────────────────────────────────────


def test_add_book_returns_created_book():
    """Test 1: POST /books creates a book and returns it."""
    payload = {
        "title": "Clean Code",
        "author": "Robert Martin",
        "isbn": "978-0132350884",
        "genre": "technology",
        "year": 2008,
        "copies": 3,
        "available_copies": 3,
    }
    response = client.post("/books", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Clean Code"
    assert data["id"] == 1


def test_get_book_returns_loan_count():
    """Test 2: GET /books/{id} includes loan_count field."""
    client.post(
        "/books",
        json={
            "title": "Refactoring",
            "author": "Fowler",
            "isbn": "111",
            "genre": "tech",
            "year": 2018,
            "copies": 2,
            "available_copies": 2,
        },
    )
    response = client.get("/books/1")
    assert response.status_code == 200
    assert "loan_count" in response.json()


def test_get_book_not_found():
    """Test 3: GET /books/999 returns 404."""
    response = client.get("/books/999")
    assert response.status_code == 404


def test_search_books_by_title():
    """Test 4: Search returns matching books."""
    client.post(
        "/books",
        json={
            "title": "Python Cookbook",
            "author": "Beazley",
            "isbn": "222",
            "genre": "tech",
            "year": 2013,
            "copies": 1,
            "available_copies": 1,
        },
    )
    response = client.get("/books/search?q=python")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_books_no_match_returns_empty():
    """Test 5: Search with no match returns empty list."""
    client.post(
        "/books",
        json={
            "title": "The Hobbit",
            "author": "Tolkien",
            "isbn": "333",
            "genre": "fiction",
            "year": 1937,
            "copies": 2,
            "available_copies": 2,
        },
    )
    response = client.get("/books/search?genre=science")
    assert response.status_code == 200
    assert response.json() == []


# ────────────────────────────────────────────────
# USER TESTS (6–10)
# ────────────────────────────────────────────────


def test_add_user_returns_created_user():
    """Test 6: POST /users creates a user."""
    response = client.post(
        "/users",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "phone": "123",
            "membership_type": "premium",
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"


def test_user_is_active_on_creation():
    """Test 7: Newly created user has active=True."""
    client.post(
        "/users",
        json={
            "name": "Bob",
            "email": "bob@example.com",
            "phone": "456",
            "membership_type": "basic",
        },
    )
    response = client.get("/users/1")
    assert response.json()["user"]["active"] is True


def test_deactivate_user_success():
    """Test 8: Deactivate a user with no loans."""
    client.post(
        "/users",
        json={
            "name": "Carol",
            "email": "carol@example.com",
            "phone": "789",
            "membership_type": "basic",
        },
    )
    response = client.delete("/users/1")
    assert response.status_code == 200
    assert users[1]["active"] is False


def test_deactivate_user_with_active_loans_fails():
    """Test 9: Cannot deactivate user who has active loans."""
    _setup_user_and_book()
    client.post("/loans", json={"user_id": 1, "book_id": 1})
    response = client.delete("/users/1")
    assert response.status_code == 400


def test_get_user_not_found():
    """Test 10: GET /users/999 returns 404."""
    response = client.get("/users/999")
    assert response.status_code == 404


# ────────────────────────────────────────────────
# LOAN TESTS (11–17)
# ────────────────────────────────────────────────


def test_create_loan_success():
    """Test 11: Create a loan reduces available_copies."""
    _setup_user_and_book()
    response = client.post("/loans", json={"user_id": 1, "book_id": 1})
    assert response.status_code == 201
    assert books[1]["available_copies"] == 0


def test_create_loan_no_copies_fails():
    """Test 12: Loan fails when no copies are available."""
    _setup_user_and_book(available_copies=0)
    response = client.post("/loans", json={"user_id": 1, "book_id": 1})
    assert response.status_code == 400


def test_create_loan_inactive_user_fails():
    """Test 13: Inactive user cannot create a loan."""
    _setup_user_and_book()
    client.delete("/users/1")  # deactivate before loan
    users[1]["active"] = False  # direct state change since no loans
    response = client.post("/loans", json={"user_id": 1, "book_id": 1})
    assert response.status_code == 400


def test_loan_limit_basic_membership():
    """Test 14: Basic user cannot exceed 3 loans."""
    _setup_user_and_book(copies=5, available_copies=5)
    for _ in range(3):
        client.post("/loans", json={"user_id": 1, "book_id": 1})
        books[1]["available_copies"] = 5  # reset copies manually
    response = client.post("/loans", json={"user_id": 1, "book_id": 1})
    assert response.status_code == 400


def test_return_book_restores_copy():
    """Test 15: Returning a book restores available_copies."""
    _setup_user_and_book()
    client.post("/loans", json={"user_id": 1, "book_id": 1})
    client.post("/loans/1/return")
    assert books[1]["available_copies"] == 1


def test_renew_loan_extends_due_date():
    """Test 16: Renewing a loan extends the due date."""
    _setup_user_and_book()
    client.post("/loans", json={"user_id": 1, "book_id": 1})
    original_due = loans[1]["due_date"]
    client.post("/loans/1/renew")
    assert loans[1]["due_date"] > original_due


def test_renew_loan_twice_fails():
    """Test 17: A loan cannot be renewed more than once."""
    _setup_user_and_book()
    client.post("/loans", json={"user_id": 1, "book_id": 1})
    client.post("/loans/1/renew")
    response = client.post("/loans/1/renew")
    assert response.status_code == 400


# ────────────────────────────────────────────────
# FINE CALCULATION TESTS (18–21)
# ────────────────────────────────────────────────


def test_calculate_fine_no_overdue():
    """Test 18: No fine for non-overdue loan."""
    loan = {
        "status": "active",
        "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
    }
    assert calculate_fine(loan) == 0.0


def test_calculate_fine_overdue():
    """Test 19: Fine calculated correctly for overdue loan."""
    loan = {
        "status": "active",
        "due_date": (datetime.now() - timedelta(days=4)).isoformat(),
    }
    assert calculate_fine(loan) == pytest.approx(2.0)


def test_calculate_fine_returned_loan_is_zero():
    """Test 20: Returned loan has zero fine regardless of dates."""
    loan = {
        "status": "returned",
        "due_date": (datetime.now() - timedelta(days=10)).isoformat(),
    }
    assert calculate_fine(loan) == 0.0


def test_return_book_charges_fine():
    """Test 21: Return endpoint charges fine for overdue book."""
    _setup_user_and_book()
    client.post("/loans", json={"user_id": 1, "book_id": 1})
    # Manually set due_date in the past
    loans[1]["due_date"] = (datetime.now() - timedelta(days=3)).isoformat()
    response = client.post("/loans/1/return")
    assert response.status_code == 200
    assert response.json()["fine"] == pytest.approx(1.5)


# ────────────────────────────────────────────────
# RESERVATION TESTS (22–23)
# ────────────────────────────────────────────────


def test_create_reservation_success():
    """Test 22: Create reservation succeeds."""
    _setup_user_and_book()
    response = client.post("/reservations", json={"user_id": 1, "book_id": 1})
    assert response.status_code == 201
    assert response.json()["status"] == "active"


def test_duplicate_reservation_fails():
    """Test 23: Cannot reserve the same book twice."""
    _setup_user_and_book()
    client.post("/reservations", json={"user_id": 1, "book_id": 1})
    response = client.post("/reservations", json={"user_id": 1, "book_id": 1})
    assert response.status_code == 400


# ────────────────────────────────────────────────
# MEMBERSHIP / HELPER TESTS (24–25)
# ────────────────────────────────────────────────


def test_membership_loan_days():
    """Test 24: Correct loan days per membership type."""
    assert get_loan_period_days(MembershipType.BASIC) == 14
    assert get_loan_period_days(MembershipType.PREMIUM) == 30
    assert get_loan_period_days(MembershipType.STUDENT) == 21


def test_membership_max_loans():
    """Test 25: Correct max loans per membership type."""
    assert get_max_loans(MembershipType.BASIC) == 3
    assert get_max_loans(MembershipType.PREMIUM) == 10
    assert get_max_loans(MembershipType.STUDENT) == 5


# ────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────


def _setup_user_and_book(copies: int = 1, available_copies: int = 1):
    """Create a basic user and book for use in loan tests."""
    client.post(
        "/users",
        json={
            "name": "TestUser",
            "email": "test@example.com",
            "phone": "000",
            "membership_type": "basic",
        },
    )
    client.post(
        "/books",
        json={
            "title": "Test Book",
            "author": "Author",
            "isbn": "000",
            "genre": "fiction",
            "year": 2020,
            "copies": copies,
            "available_copies": available_copies,
        },
    )
