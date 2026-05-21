from libraryapp import db
from libraryapp.models import Book, Reader, ReaderStatus, User, UserRole
from libraryapp.test.test_base import test_app, test_session


def test_model_string_methods(test_session):
    user = User(
        name="Reader Name",
        phone="0900000000",
        email="reader@gmail.com",
        username="reader_name",
        password="password",
        user_role=UserRole.READER,
    )
    book = Book(title="Book Name", author="Author", type="Novel")
    test_session.add_all([user, book])
    test_session.flush()
    reader = Reader(id=user.id, status=ReaderStatus.ACTIVE)
    test_session.add(reader)
    test_session.commit()

    assert str(user) == "Reader Name"
    assert str(reader) == "Reader Name"
    assert str(book) == "Book Name"


def test_reader_string_without_user():
    reader = Reader(id=99, status=ReaderStatus.ACTIVE)

    assert str(reader) == "99"


def test_create_db_uses_configured_app(test_app, mocker):
    import libraryapp.models as models

    mocker.patch.object(models, "app", test_app)

    models.create_db()


def test_init_all_data_seeds_books_and_users(test_app, mocker):
    import libraryapp.models as models

    mocker.patch.object(models, "app", test_app)

    models.init_all_data()

    assert Book.query.count() > 0
    usernames = {user.username for user in User.query.all()}
    assert {"admin", "man", "tester", "ndqbao"}.issubset(usernames)
