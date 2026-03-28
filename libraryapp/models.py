from libraryapp import db, app
from sqlalchemy import Column, Integer, String, DATE, DateTime, Double, Boolean, ForeignKey, Enum, UniqueConstraint, \
    Text, and_, func
from sqlalchemy.orm import relationship
import enum
from flask_login import UserMixin
from datetime import datetime, date, timedelta, time
import random
from libraryapp.utils import hash_password


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)

class UserRole(enum.Enum):
    ADMIN = 1
    READER = 2

class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    name = Column(String(50), nullable=False)
    phone = Column(String(10), nullable=False)
    email = Column(String(100), nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.READER)
    reader = relationship("Reader", backref="user", uselist=False)

    def __str__(self):
        return self.name

class Reader(BaseModel):
    __tablename__ = "reader"

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    borrow_slips = relationship("BorrowSlip", backref="reader", lazy=True)

    def __str__(self):
        return self.name

class Book(BaseModel):
    __tablename__ = "book"

    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    type = Column(String(100), nullable=False)
    publish_year = Column(Integer, nullable=True)
    quantity = Column(Integer, default=1)

    borrow_slip_details = relationship("BorrowSlipDetail", backref="book", lazy=True)

    def __str__(self):
        return self.title

class BorrowSlip(BaseModel):
    __tablename__ = "borrow_slip"

    reader_id = Column(Integer, ForeignKey("reader.id"), nullable=False)

    borrow_date = Column(DateTime, default=datetime.now())
    due_date = Column(DateTime, nullable=False)

    borrow_slip_details = relationship("BorrowSlipDetail", lazy=True)

class BorrowSlipDetail(BaseModel):
    __tablename__ = "borrow_slip_detail"

    borrow_slip_id = Column(Integer, ForeignKey("borrow_slip.id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("book.id"))

    return_date = Column(DateTime, nullable=True)
    is_returned = Column(Boolean, default=False)

def create_db():
    with app.app_context():
        db.create_all()
        db.session.commit()

def insert_books():
    books = [
        {"title": "Clean Code", "author": "Robert C. Martin", "type": "Programming", "publish_year": 2008, "quantity": 5},
        {"title": "Design Patterns", "author": "Erich Gamma", "type": "Programming", "publish_year": 1994, "quantity": 3},
        {"title": "Refactoring", "author": "Martin Fowler", "type": "Programming", "publish_year": 1999, "quantity": 4},
        {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "type": "Programming", "publish_year": 1999, "quantity": 6},
        {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "type": "Computer Science", "publish_year": 2009, "quantity": 2},
        {"title": "Python Crash Course", "author": "Eric Matthes", "type": "Programming", "publish_year": 2019, "quantity": 7},
        {"title": "Fluent Python", "author": "Luciano Ramalho", "type": "Programming", "publish_year": 2015, "quantity": 3},
        {"title": "Harry Potter", "author": "J.K. Rowling", "type": "Novel", "publish_year": 1997, "quantity": 5},
        {"title": "Sherlock Holmes", "author": "Arthur Conan Doyle", "type": "Detective", "publish_year": 1892, "quantity": 4},
        {"title": "Atomic Habits", "author": "James Clear", "type": "Self Help", "publish_year": 2018, "quantity": 6}
    ]

    with app.app_context():
        for b in books:
            db.session.add(Book(**b))
        db.session.commit()

def create_user_base(name, phone, email, username, password, role):
    password = hash_password(password)
    user = User(name=name, phone=phone, email=email, username=username, password=password, user_role=role)
    db.session.add(user)
    db.session.flush()
    return user

def init_all_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

    insert_books()
    with app.app_context():
        create_user_base("Nguyễn Thanh Thuận", "0334903055","thuan@gmail.com", "admin", "123", UserRole.ADMIN)
        db.session.commit()


if __name__ == "__main__":
    create_db()
    init_all_data()