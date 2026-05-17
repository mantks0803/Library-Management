import hashlib
from datetime import datetime, timedelta

import pytest
from flask import Flask
from libraryapp import db
from libraryapp.dao import books
from libraryapp.models import Book, User, Reader, BorrowSlip, BorrowSlipStatus, BorrowSlipDetail, UserRole, ReaderStatus
from libraryapp.routes import borrow_cart, book_detail
from libraryapp.routes.book_detail import book_bp
from libraryapp.routes.borrow_cart import borrow_bp
from libraryapp.routes.borrow_history import history_bp
from libraryapp.routes.home import home_bp
from libraryapp.utils import hash_password

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config['PAGE_SIZE'] = 5
    app.config['TESTING'] = True
    app.secret_key = 'fufe8fehf8fe8wkjldvdbnmfsl'
    db.init_app(app)
    from libraryapp.routes import register
    app.register_blueprint(home_bp)
    app.register_blueprint(register.register_bp)
    app.register_blueprint(borrow_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(history_bp)
    return app

@pytest.fixture
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()
    db.session.remove()

@pytest.fixture
def sample_books(test_session):
    b1 = Book(title="Clean Code", author="Robert C. Martin", type="Programming")
    b2 = Book(title="Introduction to Algorithms", author="Thomas H. Cormen", type="Computer Science")
    b3 = Book(title="Clean Code 2", author="Robert C. Martin", type="Programming")
    b4 = Book(title="Harry Potter", author="J.K. Rowling", type="Novel")
    b5 = Book(title="Atomic Habits", author="James Clear", type="Self Help")

    test_session.add_all([b1, b2, b3, b4, b5])
    test_session.commit()

    return b1, b2, b3, b4, b5


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def sample_user(test_session):
    u = User(name="Nguyen Van A",
             username='tester',
             password=hashlib.md5('Abc1234@'.encode('utf-8')).hexdigest(),
             phone='0848482273',
             email='test@gmail.com',
             user_role=UserRole.READER)
    test_session.add(u)
    test_session.commit()
    return u

@pytest.fixture
def sample_reader(test_session):
    u = User(
        name='Tester', username='tester', password='Abc123@',
        phone='0848482273', email='test@gmail.com', user_role=UserRole.READER
    )
    test_session.add(u)
    test_session.commit()

    r = Reader(id=u.id, status=ReaderStatus.ACTIVE)
    test_session.add(r)
    test_session.commit()
    return u


@pytest.fixture
def sample_books_borrow(test_session):
    books = [
        Book(id=1, title="Book A",author="Aa",type="aA", quantity=3),
        Book(id=2, title="Book B",author="Bb",type="bB", quantity=1),
        Book(id=3, title="Book C",author="Cc",type="cC", quantity=0),
    ]
    test_session.add_all(books)
    test_session.commit()
    return books

@pytest.fixture
def sample_slip(test_session, sample_reader):
    slip = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=7),
        status=BorrowSlipStatus.BORROWING,
        penalty_fee=0
    )
    test_session.add(slip)
    test_session.commit()
    return slip

@pytest.fixture
def sample_slip_pending(test_session, sample_reader):
    slip = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=7),
        status=BorrowSlipStatus.PENDING,
        penalty_fee=0
    )
    test_session.add(slip)
    test_session.commit()
    return slip

@pytest.fixture
def sample_borrow_details(test_session, sample_slip_pending, sample_books_borrow):
    book = sample_books_borrow[0]

    detail = BorrowSlipDetail(
        borrow_slip_id=sample_slip_pending.id,
        book_id=book.id,
        is_returned=False,
        return_date=None
    )

    test_session.add(detail)
    test_session.commit()
    return [detail]

@pytest.fixture
def sample_slip_borrowing(test_session, sample_reader):
    from datetime import datetime, timedelta
    from libraryapp.models import BorrowSlip, BorrowSlipStatus

    slip = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=7),
        status=BorrowSlipStatus.BORROWING,
        penalty_fee=0
    )
    test_session.add(slip)
    test_session.commit()
    return slip

@pytest.fixture
def sample_details_return(test_session, sample_slip_borrowing, sample_books_borrow):
    from libraryapp.models import BorrowSlipDetail

    book = sample_books_borrow[0]

    detail = BorrowSlipDetail(
        borrow_slip_id=sample_slip_borrowing.id,
        book_id=book.id,
        is_returned=False,
        return_date=None
    )

    test_session.add(detail)
    test_session.commit()
    return [detail]

@pytest.fixture
def mock_cloudinary(monkeypatch):
    def fake_upload(file):
        return {'secure_url': 'https://fake-image.png'}

    monkeypatch.setattr('libraryapp.dao.books.cloudinary.uploader.upload', fake_upload)
