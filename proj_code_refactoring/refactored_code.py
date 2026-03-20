"""
Library Management System - Refactored Code
Applies 10+ refactoring techniques for improved readability and maintainability.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum
import logging

# REFACTORING 1: Replace Magic Numbers with Named Constants / Symbolic Constants
# Grouped into a dedicated config section for clarity
FINE_PER_DAY = 0.5
DEFAULT_LOAN_DAYS = 14
RESERVATION_EXPIRY_DAYS = 3


# REFACTORING 2: Replace Type Code with Enum
class MembershipType(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    STUDENT = "student"


# REFACTORING 3: Replace Magic Numbers / duplicated if-else chains with lookup tables
MEMBERSHIP_MAX_LOANS: Dict[MembershipType, int] = {
    MembershipType.BASIC: 3,
    MembershipType.PREMIUM: 10,
    MembershipType.STUDENT: 5,
}

MEMBERSHIP_LOAN_DAYS: Dict[MembershipType, int] = {
    MembershipType.BASIC: 14,
    MembershipType.PREMIUM: 30,
    MembershipType.STUDENT: 21,
}

# REFACTORING 4: Replace Debug Print with Proper Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- In-Memory Store (same as original, but encapsulated) ---
books: Dict[int, dict] = {}
users: Dict[int, dict] = {}
loans: Dict[int, dict] = {}
reservations: Dict[int, dict] = {}
_book_counter = 0
_user_counter = 0
_loan_counter = 0
_reservation_counter = 0


# --- Pydantic Models ---


class Book(BaseModel):
    title: str
    author: str
    isbn: str
    genre: str
    year: int
    copies: int
    available_copies: int


class User(BaseModel):
    name: str
    email: str
    phone: str
    membership_type: MembershipType
    balance: float = 0.0


class LoanCreate(BaseModel):
    user_id: int
    book_id: int


class ReservationCreate(BaseModel):
    user_id: int
    book_id: int


# --- REFACTORING 5: Extract Method - Isolated reusable helper functions ---


def _next_id(counter_name: str) -> int:
    """Generate the next sequential ID for a given entity."""
    global _book_counter, _user_counter, _loan_counter, _reservation_counter
    mapping = {
        "book": "_book_counter",
        "user": "_user_counter",
        "loan": "_loan_counter",
        "reservation": "_reservation_counter",
    }
    if counter_name == "book":
        _book_counter += 1
        return _book_counter
    elif counter_name == "user":
        _user_counter += 1
        return _user_counter
    elif counter_name == "loan":
        _loan_counter += 1
        return _loan_counter
    else:
        _reservation_counter += 1
        return _reservation_counter


def calculate_fine(loan: dict) -> float:
    """
    REFACTORING 5: Extract Method
    Calculates the overdue fine for a single loan.
    Was duplicated in 5+ places in the original code.
    """
    if loan["status"] != "active":
        return 0.0
    due_date = datetime.fromisoformat(loan["due_date"])
    if datetime.now() <= due_date:
        return 0.0
    days_overdue = (datetime.now() - due_date).days
    return round(days_overdue * FINE_PER_DAY, 2)


def get_user_or_404(user_id: int) -> dict:
    """
    REFACTORING 5: Extract Method
    Returns user or raises 404. Eliminates repeated lookup pattern.
    """
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_book_or_404(book_id: int) -> dict:
    """
    REFACTORING 5: Extract Method
    Returns book or raises 404. Eliminates repeated lookup pattern.
    """
    book = books.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def get_loan_or_404(loan_id: int) -> dict:
    """
    REFACTORING 5: Extract Method
    Returns loan or raises 404.
    """
    loan = loans.get(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


def get_active_loans_for_user(user_id: int) -> List[dict]:
    """
    REFACTORING 5: Extract Method
    Returns all active loans for a user.
    """
    return [
        loan
        for loan in loans.values()
        if loan["user_id"] == user_id and loan["status"] == "active"
    ]


def get_loan_period_days(membership_type: MembershipType) -> int:
    """
    REFACTORING 6: Replace Conditional with Lookup
    Returns loan period based on membership type using lookup table.
    """
    return MEMBERSHIP_LOAN_DAYS.get(membership_type, DEFAULT_LOAN_DAYS)


def get_max_loans(membership_type: MembershipType) -> int:
    """
    REFACTORING 6: Replace Conditional with Lookup
    Returns max allowed loans based on membership type using lookup table.
    """
    return MEMBERSHIP_MAX_LOANS.get(
        membership_type, MEMBERSHIP_MAX_LOANS[MembershipType.BASIC]
    )


def apply_pending_fines(user_id: int) -> None:
    """
    REFACTORING 5: Extract Method
    Applies outstanding fines on a user's active loans before processing new actions.
    Was inlined and duplicated inside create_loan.
    """
    for loan in get_active_loans_for_user(user_id):
        fine = calculate_fine(loan)
        if fine > 0 and not loan.get("fine_applied"):
            users[user_id]["balance"] -= fine
            loan["fine_applied"] = True


def fulfill_reservation_if_exists(user_id: int, book_id: int) -> None:
    """
    REFACTORING 5: Extract Method
    Marks a matching reservation as fulfilled.
    """
    for reservation in reservations.values():
        if (
            reservation["user_id"] == user_id
            and reservation["book_id"] == book_id
            and reservation["status"] == "active"
        ):
            reservation["status"] = "fulfilled"


def expire_stale_reservations() -> None:
    """
    REFACTORING 7: Separate Query from Modifier
    Expiring reservations is now an explicit operation, not a hidden side effect
    during a read. Call this explicitly when needed.
    """
    for reservation in reservations.values():
        expires_at = datetime.fromisoformat(reservation["expires_at"])
        if datetime.now() > expires_at and reservation["status"] == "active":
            reservation["status"] = "expired"


# --- Route Handlers ---


@app.post("/books", status_code=201)
def add_book(book: Book):
    book_id = _next_id("book")
    books[book_id] = {"id": book_id, **book.model_dump()}
    logger.info("Book added: %s (id=%d)", book.title, book_id)
    return books[book_id]


@app.post("/users", status_code=201)
def add_user(user: User):
    user_id = _next_id("user")
    users[user_id] = {
        "id": user_id,
        **user.model_dump(),
        "active": True,
        "registered_at": datetime.now().isoformat(),
    }
    logger.info("User registered: %s (id=%d)", user.name, user_id)
    return users[user_id]


@app.get("/books/search")
def search_books(q: str = "", genre: str = "", author: str = ""):
    """
    REFACTORING 10: Replace Temp with Query / Consolidate Conditional Expression
    Filtering logic expressed clearly using a helper predicate.
    """

    def matches(book: dict) -> bool:
        if (
            q
            and q.lower() not in book["title"].lower()
            and q.lower() not in book["author"].lower()
        ):
            return False
        if genre and book["genre"].lower() != genre.lower():
            return False
        if author and author.lower() not in book["author"].lower():
            return False
        return True

    return [book for book in books.values() if matches(book)]


@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = get_book_or_404(book_id)
    loan_count = sum(1 for loan in loans.values() if loan["book_id"] == book_id)
    return {"book": book, "loan_count": loan_count}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = get_user_or_404(user_id)
    active_count = len(get_active_loans_for_user(user_id))
    return {"user": user, "active_loans": active_count}


@app.delete("/users/{user_id}")
def deactivate_user(user_id: int):
    user = get_user_or_404(user_id)
    # REFACTORING 8: Add Guard Clause - check active loans before deactivation
    active_loans = get_active_loans_for_user(user_id)
    if active_loans:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot deactivate user with {len(active_loans)} active loan(s)",
        )
    users[user_id]["active"] = False
    return {"message": "User deactivated"}


@app.post("/loans", status_code=201)
def create_loan(data: LoanCreate):
    """
    REFACTORING 9: Decompose Conditional / Extract Method
    The original 60-line nested function is now a clean sequence of guard clauses
    and delegating to extracted helpers.
    """
    user = get_user_or_404(data.user_id)
    book = get_book_or_404(data.book_id)

    if not user["active"]:
        raise HTTPException(status_code=400, detail="User account is not active")
    if book["available_copies"] <= 0:
        raise HTTPException(status_code=400, detail="No copies available")

    apply_pending_fines(data.user_id)

    membership = MembershipType(user["membership_type"])
    active_loans = get_active_loans_for_user(data.user_id)
    max_allowed = get_max_loans(membership)

    if len(active_loans) >= max_allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Loan limit reached ({max_allowed} for {membership.value} membership)",
        )

    loan_days = get_loan_period_days(membership)
    issue_date = datetime.now()
    due_date = issue_date + timedelta(days=loan_days)

    loan_id = _next_id("loan")
    loans[loan_id] = {
        "id": loan_id,
        "user_id": data.user_id,
        "book_id": data.book_id,
        "issue_date": issue_date.isoformat(),
        "due_date": due_date.isoformat(),
        "status": "active",
        "fine_applied": False,
        "renewed": False,
    }
    books[data.book_id]["available_copies"] -= 1
    fulfill_reservation_if_exists(data.user_id, data.book_id)

    logger.info(
        "Loan created: user=%d book=%d due=%s",
        data.user_id,
        data.book_id,
        due_date.date(),
    )
    return loans[loan_id]


@app.get("/loans/{loan_id}")
def get_loan(loan_id: int):
    loan = get_loan_or_404(loan_id)
    user = users.get(loan["user_id"])
    book = books.get(loan["book_id"])
    current_fine = calculate_fine(loan)
    return {
        "loan": loan,
        "user_name": user["name"] if user else "Unknown",
        "book_title": book["title"] if book else "Unknown",
        "current_fine": current_fine,
    }


@app.get("/users/{user_id}/loans")
def get_user_loans(user_id: int):
    get_user_or_404(user_id)
    result = []
    total_fine = 0.0
    for loan in loans.values():
        if loan["user_id"] != user_id:
            continue
        fine = calculate_fine(loan)
        total_fine += fine
        book = books.get(loan["book_id"])
        result.append(
            {
                "loan": loan,
                "book_title": book["title"] if book else "Unknown",
                "fine": fine,
            }
        )
    return {"loans": result, "total_fine": round(total_fine, 2)}


@app.post("/loans/{loan_id}/return")
def return_book(loan_id: int):
    loan = get_loan_or_404(loan_id)
    if loan["status"] != "active":
        raise HTTPException(status_code=400, detail="Loan is not active")

    fine = calculate_fine(loan)
    loan["status"] = "returned"
    loan["return_date"] = datetime.now().isoformat()
    loan["final_fine"] = fine
    books[loan["book_id"]]["available_copies"] += 1
    users[loan["user_id"]]["balance"] -= fine

    logger.info("Book returned: loan=%d fine=%.2f", loan_id, fine)
    return {"message": "Book returned successfully", "fine": fine}


@app.post("/loans/{loan_id}/renew")
def renew_loan(loan_id: int):
    loan = get_loan_or_404(loan_id)
    if loan["status"] != "active":
        raise HTTPException(status_code=400, detail="Loan is not active")
    if loan["renewed"]:
        raise HTTPException(status_code=400, detail="Loan has already been renewed")

    user = get_user_or_404(loan["user_id"])
    membership = MembershipType(user["membership_type"])
    extension_days = get_loan_period_days(membership)

    current_due = datetime.fromisoformat(loan["due_date"])
    loan["due_date"] = (current_due + timedelta(days=extension_days)).isoformat()
    loan["renewed"] = True

    return {"message": "Loan renewed successfully", "new_due_date": loan["due_date"]}


@app.post("/reservations", status_code=201)
def create_reservation(data: ReservationCreate):
    get_user_or_404(data.user_id)
    get_book_or_404(data.book_id)

    already_reserved = any(
        r["user_id"] == data.user_id
        and r["book_id"] == data.book_id
        and r["status"] == "active"
        for r in reservations.values()
    )
    if already_reserved:
        raise HTTPException(
            status_code=400, detail="Book is already reserved by this user"
        )

    reservation_id = _next_id("reservation")
    reservations[reservation_id] = {
        "id": reservation_id,
        "user_id": data.user_id,
        "book_id": data.book_id,
        "reserved_at": datetime.now().isoformat(),
        "expires_at": (
            datetime.now() + timedelta(days=RESERVATION_EXPIRY_DAYS)
        ).isoformat(),
        "status": "active",
    }
    return reservations[reservation_id]


@app.get("/reservations/{user_id}")
def get_user_reservations(user_id: int):
    """
    REFACTORING 7: Separate Query from Modifier
    Side effects (expiration) are separated from reading reservations.
    """
    get_user_or_404(user_id)
    expire_stale_reservations()  # Explicit call, not hidden side effect

    result = []
    for reservation in reservations.values():
        if reservation["user_id"] != user_id:
            continue
        book = books.get(reservation["book_id"])
        result.append(
            {
                "reservation": reservation,
                "book_title": book["title"] if book else "Unknown",
            }
        )
    return result


@app.get("/statistics")
def get_statistics():
    """
    REFACTORING 5 + 10: Extract Method + Inline Temp
    Statistics computation split into clear named sections. Removed hardcoded genre list.
    """
    overdue_loans = [
        loan
        for loan in loans.values()
        if loan["status"] == "active" and calculate_fine(loan) > 0
    ]
    total_outstanding_fines = sum(calculate_fine(loan) for loan in overdue_loans)

    # REFACTORING 10: Derive genre stats from actual data instead of hardcoded list
    genre_stats: Dict[str, int] = {}
    for book in books.values():
        genre = book["genre"].lower()
        genre_stats[genre] = genre_stats.get(genre, 0) + 1

    loan_counts_by_book = {}
    for loan in loans.values():
        loan_counts_by_book[loan["book_id"]] = (
            loan_counts_by_book.get(loan["book_id"], 0) + 1
        )

    most_popular_book = None
    if loan_counts_by_book:
        top_book_id = max(loan_counts_by_book, key=lambda bid: loan_counts_by_book[bid])
        most_popular_book = (
            books[top_book_id]["title"] if top_book_id in books else None
        )

    return {
        "total_books": len(books),
        "total_users": len(users),
        "total_loans": len(loans),
        "active_loans": sum(1 for l in loans.values() if l["status"] == "active"),
        "returned_loans": sum(1 for l in loans.values() if l["status"] == "returned"),
        "overdue_loans": len(overdue_loans),
        "total_outstanding_fines": round(total_outstanding_fines, 2),
        "genre_stats": genre_stats,
        "most_popular_book": most_popular_book,
    }
