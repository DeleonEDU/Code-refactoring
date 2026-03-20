"""
Library Management System - Original Code (with code smells)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import json
import os

app = FastAPI()

# SMELL 1: Global mutable state instead of proper DB layer
books = {}
users = {}
loans = {}
reservations = {}
cnt = 0
cnt2 = 0
cnt3 = 0

# SMELL 2: Magic numbers scattered throughout code
FINE_PER_DAY = 0.5
MAX_LOANS = 5
LOAN_DAYS = 14
RESERVATION_DAYS = 3


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
    membership_type: str  # 'basic', 'premium', 'student'
    balance: float = 0.0


class LoanCreate(BaseModel):
    user_id: int
    book_id: int


class ReservationCreate(BaseModel):
    user_id: int
    book_id: int


# SMELL 3: Huge god-function with multiple responsibilities
@app.post("/loans")
def create_loan(data: LoanCreate):
    global cnt3
    uid = data.user_id
    bid = data.book_id

    # SMELL 4: Deep nesting
    if uid in users:
        u = users[uid]
        if u["active"]:
            if bid in books:
                b = books[bid]
                if b["available_copies"] > 0:
                    # SMELL 5: Duplicated fine calculation logic (also in get_user_loans)
                    user_loans = [
                        l
                        for l in loans.values()
                        if l["user_id"] == uid and l["status"] == "active"
                    ]
                    total_fine = 0
                    for l in user_loans:
                        due = datetime.fromisoformat(l["due_date"])
                        if datetime.now() > due:
                            days_overdue = (datetime.now() - due).days
                            total_fine += days_overdue * FINE_PER_DAY
                    if total_fine > 0:
                        users[uid]["balance"] -= total_fine
                        for l in user_loans:
                            due = datetime.fromisoformat(l["due_date"])
                            if datetime.now() > due:
                                l["fine_applied"] = True

                    # Check loan limit based on membership
                    # SMELL 6: Long if-else chains instead of polymorphism/dict lookup
                    max_loans_allowed = 0
                    if u["membership_type"] == "basic":
                        max_loans_allowed = 3
                    elif u["membership_type"] == "premium":
                        max_loans_allowed = 10
                    elif u["membership_type"] == "student":
                        max_loans_allowed = 5
                    else:
                        max_loans_allowed = 3

                    active_loans_count = len(
                        [
                            l
                            for l in loans.values()
                            if l["user_id"] == uid and l["status"] == "active"
                        ]
                    )
                    if active_loans_count >= max_loans_allowed:
                        raise HTTPException(
                            status_code=400, detail="Loan limit reached"
                        )

                    # SMELL 7: Duplicated loan period logic (also in renew_loan)
                    loan_period = 0
                    if u["membership_type"] == "basic":
                        loan_period = 14
                    elif u["membership_type"] == "premium":
                        loan_period = 30
                    elif u["membership_type"] == "student":
                        loan_period = 21
                    else:
                        loan_period = 14

                    cnt3 += 1
                    loan_id = cnt3
                    issue_date = datetime.now()
                    due_date = issue_date + timedelta(days=loan_period)
                    loans[loan_id] = {
                        "id": loan_id,
                        "user_id": uid,
                        "book_id": bid,
                        "issue_date": issue_date.isoformat(),
                        "due_date": due_date.isoformat(),
                        "status": "active",
                        "fine_applied": False,
                        "renewed": False,
                    }
                    books[bid]["available_copies"] -= 1
                    # Cancel reservation if exists
                    for r in list(reservations.values()):
                        if (
                            r["user_id"] == uid
                            and r["book_id"] == bid
                            and r["status"] == "active"
                        ):
                            r["status"] = "fulfilled"
                    return loans[loan_id]
                else:
                    raise HTTPException(status_code=400, detail="No copies available")
            else:
                raise HTTPException(status_code=404, detail="Book not found")
        else:
            raise HTTPException(status_code=400, detail="User not active")
    else:
        raise HTTPException(status_code=404, detail="User not found")


# SMELL 8: Inconsistent error handling and return types
@app.post("/books")
def add_book(book: Book):
    global cnt
    cnt += 1
    bid = cnt
    books[bid] = {
        "id": bid,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "genre": book.genre,
        "year": book.year,
        "copies": book.copies,
        "available_copies": book.available_copies,
    }
    print(
        f"Book added: {book.title}"
    )  # SMELL 9: Debug print statements in production code
    return {"id": bid, "message": "ok"}


@app.post("/users")
def add_user(user: User):
    global cnt2
    cnt2 += 1
    uid = cnt2
    users[uid] = {
        "id": uid,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "membership_type": user.membership_type,
        "balance": user.balance,
        "active": True,
        "registered_at": datetime.now().isoformat(),
    }
    print(f"User added: {user.name}")  # SMELL 9: Debug print
    return {"id": uid, "message": "ok"}


@app.get("/loans/{loan_id}")
def get_loan(loan_id: int):
    if loan_id in loans:
        l = loans[loan_id]
        # SMELL 10: Inconsistent variable naming (l, u, b vs descriptive names)
        u = users.get(l["user_id"])
        b = books.get(l["book_id"])
        due = datetime.fromisoformat(l["due_date"])
        f = 0
        if datetime.now() > due and l["status"] == "active":
            days = (datetime.now() - due).days
            f = days * FINE_PER_DAY  # SMELL 5: fine calculation duplicated again
        return {
            "loan": l,
            "user_name": u["name"] if u else "Unknown",
            "book_title": b["title"] if b else "Unknown",
            "current_fine": f,
        }
    raise HTTPException(status_code=404, detail="Loan not found")


@app.get("/users/{user_id}/loans")
def get_user_loans(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    result = []
    total_fine = 0
    for l in loans.values():
        if l["user_id"] == user_id:
            due = datetime.fromisoformat(l["due_date"])
            f = 0
            # SMELL 5: fine calculation copy-pasted AGAIN
            if datetime.now() > due and l["status"] == "active":
                days_overdue = (datetime.now() - due).days
                f = days_overdue * FINE_PER_DAY
                total_fine += f
            b = books.get(l["book_id"])
            result.append(
                {"loan": l, "book_title": b["title"] if b else "Unknown", "fine": f}
            )
    return {"loans": result, "total_fine": total_fine}


@app.post("/loans/{loan_id}/return")
def return_book(loan_id: int):
    if loan_id not in loans:
        raise HTTPException(status_code=404, detail="Loan not found")
    l = loans[loan_id]
    if l["status"] != "active":
        raise HTTPException(status_code=400, detail="Loan not active")
    due = datetime.fromisoformat(l["due_date"])
    fine = 0
    if datetime.now() > due:
        days = (datetime.now() - due).days
        fine = days * FINE_PER_DAY  # SMELL 5: Duplicated again!
    l["status"] = "returned"
    l["return_date"] = datetime.now().isoformat()
    l["final_fine"] = fine
    books[l["book_id"]]["available_copies"] += 1
    users[l["user_id"]]["balance"] -= fine
    return {"message": "Book returned", "fine": fine}


@app.post("/loans/{loan_id}/renew")
def renew_loan(loan_id: int):
    if loan_id not in loans:
        raise HTTPException(status_code=404, detail="Loan not found")
    l = loans[loan_id]
    if l["status"] != "active":
        raise HTTPException(status_code=400, detail="Loan not active")
    if l["renewed"]:
        raise HTTPException(status_code=400, detail="Already renewed")
    uid = l["user_id"]
    u = users.get(uid)
    # SMELL 7: Loan period logic duplicated from create_loan
    loan_period = 0
    if u["membership_type"] == "basic":
        loan_period = 14
    elif u["membership_type"] == "premium":
        loan_period = 30
    elif u["membership_type"] == "student":
        loan_period = 21
    else:
        loan_period = 14
    due = datetime.fromisoformat(l["due_date"])
    l["due_date"] = (due + timedelta(days=loan_period)).isoformat()
    l["renewed"] = True
    return {"message": "Renewed", "new_due_date": l["due_date"]}


@app.post("/reservations")
def create_reservation(data: ReservationCreate):
    uid = data.user_id
    bid = data.book_id
    if uid not in users:
        raise HTTPException(status_code=404, detail="User not found")
    if bid not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    # Check if already reserved
    for r in reservations.values():
        if r["user_id"] == uid and r["book_id"] == bid and r["status"] == "active":
            raise HTTPException(status_code=400, detail="Already reserved")
    # SMELL 11: Temporary variable used once and adds no clarity
    x = len(reservations) + 1
    reservations[x] = {
        "id": x,
        "user_id": uid,
        "book_id": bid,
        "reserved_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=RESERVATION_DAYS)).isoformat(),
        "status": "active",
    }
    return reservations[x]


@app.get("/books/search")
def search_books(q: str = "", genre: str = "", author: str = ""):
    # SMELL 12: Inefficient O(n) search with no indexing, repeated conditionals
    result = []
    for b in books.values():
        match = True
        if q:
            if (
                q.lower() not in b["title"].lower()
                and q.lower() not in b["author"].lower()
            ):
                match = False
        if genre:
            if b["genre"].lower() != genre.lower():
                match = False
        if author:
            if author.lower() not in b["author"].lower():
                match = False
        if match:
            result.append(b)
    return result


@app.get("/statistics")
def get_statistics():
    # SMELL 3: Another large function doing everything
    total_books = len(books)
    total_users = len(users)
    total_loans = len(loans)
    active_loans = len([l for l in loans.values() if l["status"] == "active"])
    returned_loans = len([l for l in loans.values() if l["status"] == "returned"])
    overdue_loans = 0
    total_fines = 0
    for l in loans.values():
        if l["status"] == "active":
            due = datetime.fromisoformat(l["due_date"])
            if datetime.now() > due:
                overdue_loans += 1
                days = (datetime.now() - due).days
                total_fines += days * FINE_PER_DAY  # SMELL 5: Again!
    # SMELL 13: Hardcoded genre list instead of deriving from data
    genre_stats = {
        "fiction": 0,
        "non-fiction": 0,
        "science": 0,
        "history": 0,
        "technology": 0,
    }
    for b in books.values():
        g = b["genre"].lower()
        if g in genre_stats:
            genre_stats[g] += 1
    most_popular_book = None
    most_loans = 0
    for bid, b in books.items():
        c = len([l for l in loans.values() if l["book_id"] == bid])
        if c > most_loans:
            most_loans = c
            most_popular_book = b["title"]
    return {
        "total_books": total_books,
        "total_users": total_users,
        "total_loans": total_loans,
        "active_loans": active_loans,
        "returned_loans": returned_loans,
        "overdue_loans": overdue_loans,
        "total_outstanding_fines": total_fines,
        "genre_stats": genre_stats,
        "most_popular_book": most_popular_book,
    }


@app.get("/books/{book_id}")
def get_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    b = books[book_id]
    loan_history = [l for l in loans.values() if l["book_id"] == book_id]
    return {"book": b, "loan_count": len(loan_history)}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    u = users[user_id]
    active = len(
        [
            l
            for l in loans.values()
            if l["user_id"] == user_id and l["status"] == "active"
        ]
    )
    return {"user": u, "active_loans": active}


@app.delete("/users/{user_id}")
def deactivate_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    # SMELL 14: No check if user has active loans before deactivation
    users[user_id]["active"] = False
    return {"message": "User deactivated"}


@app.get("/reservations/{user_id}")
def get_user_reservations(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    result = []
    # SMELL 15: Mutating shared state inside a read operation (side effect)
    for r in reservations.values():
        if r["user_id"] == user_id:
            # Auto-expire reservations during read - unexpected side effect!
            exp = datetime.fromisoformat(r["expires_at"])
            if datetime.now() > exp and r["status"] == "active":
                r["status"] = "expired"
            b = books.get(r["book_id"])
            result.append(
                {"reservation": r, "book_title": b["title"] if b else "Unknown"}
            )
    return result
