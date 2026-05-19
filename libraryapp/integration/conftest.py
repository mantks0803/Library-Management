import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from libraryapp import db, login
from libraryapp.api.api_cart import api_cart_bp
from libraryapp.api.api_users import api_users_bp
from libraryapp.dao.users import get_current_user
from libraryapp.models import Book, BorrowSlip, BorrowSlipDetail, BorrowSlipStatus, Reader, ReaderStatus, User, UserRole
from libraryapp.routes.book_detail import book_bp
from libraryapp.routes.book_management import book_management_bp
from libraryapp.routes.borrow_cart import borrow_bp
from libraryapp.routes.borrow_history import history_bp
from libraryapp.routes.home import home_bp
from libraryapp.routes.login_logout import login_logout_bp
from libraryapp.routes.register import register_bp
from libraryapp.routes.return_slips import return_slips_bp
from libraryapp.routes.slip_management import slip_management_bp
from libraryapp.utils import hash_password


@pytest.fixture
def test_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    app.config["PAGE_SIZE"] = 5
    app.secret_key = "integration-test-secret"

    db.init_app(app)
    login.init_app(app)

    @login.user_loader
    def load_user(user_id):
        return get_current_user(user_id)

    app.register_blueprint(login_logout_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(borrow_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(return_slips_bp)
    app.register_blueprint(book_management_bp)
    app.register_blueprint(slip_management_bp)
    app.register_blueprint(api_users_bp)
    app.register_blueprint(api_cart_bp)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()
    db.session.remove()


def _create_user(username, password, role=UserRole.READER, name="Test User"):
    user = User(
        name=name,
        phone="0900000000",
        email=f"{username}@mail.com",
        username=username,
        password=hash_password(password),
        user_role=role,
    )
    db.session.add(user)
    db.session.flush()

    if role == UserRole.READER:
        reader = Reader(id=user.id, status=ReaderStatus.ACTIVE)
        db.session.add(reader)

    db.session.commit()
    return user


@pytest.fixture
def reader_user(test_session):
    return _create_user("reader", "OldPass123", UserRole.READER, "Reader User")


@pytest.fixture
def admin_user(test_session):
    return _create_user("admin", "Admin123", UserRole.ADMIN, "Admin User")


@pytest.fixture
def sample_books(test_session):
    books = [
        Book(title="Clean Code", author="Robert C. Martin", type="Programming", quantity=2),
        Book(title="Design Patterns", author="Erich Gamma", type="Programming", quantity=1),
        Book(title="Refactoring", author="Martin Fowler", type="Programming", quantity=1),
        Book(title="Algorithms", author="Thomas Cormen", type="Computer Science", quantity=1),
        Book(title="Atomic Habits", author="James Clear", type="Self Help", quantity=1),
        Book(title="Harry Potter", author="J.K. Rowling", type="Novel", quantity=1),
        Book(title="Empty Book", author="No Author", type="Novel", quantity=0),
    ]
    test_session.add_all(books)
    test_session.commit()
    return books


def login_as(client, user):
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)
        session["_fresh"] = True


@pytest.fixture
def borrowing_slip(test_session, reader_user, sample_books):
    slip = BorrowSlip(
        reader_id=reader_user.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=7),
        status=BorrowSlipStatus.BORROWING,
        penalty_fee=0,
    )
    test_session.add(slip)
    test_session.flush()

    detail = BorrowSlipDetail(
        borrow_slip_id=slip.id,
        book_id=sample_books[0].id,
        is_returned=False,
    )
    test_session.add(detail)
    test_session.commit()
    return slip
