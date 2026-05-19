from datetime import datetime, timedelta
from io import BytesIO

import pytest

from libraryapp import db
from libraryapp.models import BorrowSlip, BorrowSlipStatus, Reader, ReaderStatus, User, UserRole
from libraryapp.test.test_base import sample_reader, sample_user, test_app, test_client, test_session
from libraryapp.utils import hash_password


def login_as(client, user):
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)
        session["_fresh"] = True


@pytest.fixture
def admin_user(test_session):
    user = User(
        name="Admin",
        username="admin",
        password=hash_password("Admin123"),
        phone="0900000001",
        email="admin@gmail.com",
        user_role=UserRole.ADMIN,
    )
    test_session.add(user)
    test_session.commit()
    return user


def _file(filename):
    return BytesIO(b"fake image content"), filename


def test_book_management_renders_books_for_admin(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_get_books = mocker.patch("libraryapp.routes.book_management.get_list_books")
    mock_count_books = mocker.patch("libraryapp.routes.book_management.count_books", return_value=12)
    mock_render = mocker.patch("libraryapp.routes.book_management.render_template", return_value="book html")
    mock_get_books.return_value = ["book 1", "book 2"]

    response = test_client.get("/book?page=2")

    assert response.status_code == 200
    mock_get_books.assert_called_once_with(full=True, page=2)
    mock_count_books.assert_called_once_with()
    args, kwargs = mock_render.call_args
    assert args == ("admin/book_management.html",)
    assert kwargs["books"] == ["book 1", "book 2"]
    assert kwargs["total_books"] == 12
    assert kwargs["current_page"] == 2
    assert kwargs["pages"] == 1


def test_book_management_requires_admin(test_client, sample_user):
    login_as(test_client, sample_user)

    response = test_client.get("/book")

    assert response.status_code == 403


def test_add_book_success_redirects_and_calls_dao(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_add = mocker.patch("libraryapp.routes.book_management.add_book", return_value=(True, object()))

    response = test_client.post(
        "/book/add",
        data={
            "title": "New Book",
            "author": "New Author",
            "type": "Programming",
            "publish_year": "2024",
            "quantity": "2",
            "avatar": _file("cover.jpg"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book")
    mock_add.assert_called_once()
    assert mock_add.call_args.kwargs["title"] == "New Book"
    assert mock_add.call_args.kwargs["publish_year"] == 2024
    assert mock_add.call_args.kwargs["quantity"] == 2


def test_add_book_missing_title_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_add = mocker.patch("libraryapp.routes.book_management.add_book")

    response = test_client.post(
        "/book/add",
        data={"title": "", "author": "Author", "type": "Novel"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book")
    mock_add.assert_not_called()


def test_add_book_missing_author_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_add = mocker.patch("libraryapp.routes.book_management.add_book")

    response = test_client.post(
        "/book/add",
        data={"title": "Book", "author": "", "type": "Novel"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book")
    mock_add.assert_not_called()


def test_add_book_missing_type_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_add = mocker.patch("libraryapp.routes.book_management.add_book")

    response = test_client.post(
        "/book/add",
        data={"title": "Book", "author": "Author", "type": ""},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book")
    mock_add.assert_not_called()


def test_add_book_invalid_file_renders_error(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_render = mocker.patch("libraryapp.routes.book_management.render_template", return_value="invalid file")

    response = test_client.post(
        "/book/add",
        data={
            "title": "Book",
            "author": "Author",
            "type": "Novel",
            "avatar": _file("cover.txt"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    args, kwargs = mock_render.call_args
    assert args == ("admin/book_management.html",)
    assert "err_msg" in kwargs


def test_add_book_quantity_less_than_one_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_add = mocker.patch("libraryapp.routes.book_management.add_book")

    response = test_client.post(
        "/book/add",
        data={
            "title": "Book",
            "author": "Author",
            "type": "Novel",
            "quantity": "0",
            "avatar": _file("cover.png"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book")
    mock_add.assert_not_called()


def test_add_book_invalid_publish_year_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_add = mocker.patch("libraryapp.routes.book_management.add_book")

    response = test_client.post(
        "/book/add",
        data={
            "title": "Book",
            "author": "Author",
            "type": "Novel",
            "publish_year": "wrong",
            "quantity": "1",
            "avatar": _file("cover.png"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book")
    mock_add.assert_not_called()


def test_add_book_dao_failure_still_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_add = mocker.patch("libraryapp.routes.book_management.add_book", return_value=(False, "failed"))

    response = test_client.post(
        "/book/add",
        data={
            "title": "Book",
            "author": "Author",
            "type": "Novel",
            "quantity": "1",
            "avatar": _file("cover.png"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book")
    mock_add.assert_called_once()


def test_add_book_dao_exception_still_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mocker.patch("libraryapp.routes.book_management.add_book", side_effect=Exception("boom"))

    response = test_client.post(
        "/book/add",
        data={
            "title": "Book",
            "author": "Author",
            "type": "Novel",
            "quantity": "1",
            "avatar": _file("cover.png"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book")


def test_slip_management_filters_pending_and_counts_stats(test_client, admin_user, sample_reader, mocker):
    login_as(test_client, admin_user)
    mocker.patch("libraryapp.routes.slip_management.check_and_update_overdue_slips")
    mock_render = mocker.patch("libraryapp.routes.slip_management.render_template", return_value="slip html")

    pending = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=7),
        status=BorrowSlipStatus.PENDING,
    )
    returned = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=7),
        status=BorrowSlipStatus.RETURNED,
    )
    db.session.add_all([pending, returned])
    db.session.commit()

    response = test_client.get("/slip?status=pending&page=1")

    assert response.status_code == 200
    args, kwargs = mock_render.call_args
    assert args == ("admin/slip_management.html",)
    assert kwargs["status_filter"] == "pending"
    assert kwargs["total_slips"] == 1
    assert kwargs["total_pending"] == 1
    assert kwargs["total_returned"] == 1
    assert kwargs["slips"][0].id == pending.id


def test_slip_management_overdue_filter(test_client, admin_user, sample_reader, mocker):
    login_as(test_client, admin_user)
    mocker.patch("libraryapp.routes.slip_management.check_and_update_overdue_slips")
    mock_render = mocker.patch("libraryapp.routes.slip_management.render_template", return_value="slip html")

    overdue = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() - timedelta(days=2),
        status=BorrowSlipStatus.OVERDUE,
    )
    db.session.add(overdue)
    db.session.commit()

    response = test_client.get("/slip?status=overdue")

    assert response.status_code == 200
    assert mock_render.call_args.kwargs["total_slips"] == 1
    assert mock_render.call_args.kwargs["slips"][0].status == BorrowSlipStatus.OVERDUE


@pytest.mark.parametrize(
    ("status", "expected_status"),
    [
        ("borrowing", BorrowSlipStatus.BORROWING),
        ("returned", BorrowSlipStatus.RETURNED),
    ],
)
def test_slip_management_other_status_filters(test_client, admin_user, sample_reader, mocker, status, expected_status):
    login_as(test_client, admin_user)
    mocker.patch("libraryapp.routes.slip_management.check_and_update_overdue_slips")
    mock_render = mocker.patch("libraryapp.routes.slip_management.render_template", return_value="slip html")

    slip = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=7),
        status=expected_status,
    )
    db.session.add(slip)
    db.session.commit()

    response = test_client.get(f"/slip?status={status}")

    assert response.status_code == 200
    assert mock_render.call_args.kwargs["total_slips"] == 1
    assert mock_render.call_args.kwargs["slips"][0].status == expected_status


def test_approve_slip_success_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mock_confirm = mocker.patch(
        "libraryapp.routes.slip_management.confirm_return_borrow_slip",
        return_value=(True, "ok"),
    )

    response = test_client.post("/slip/approve/1")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/slip?status=pending")
    mock_confirm.assert_called_once_with(1)


def test_approve_slip_failure_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mocker.patch(
        "libraryapp.routes.slip_management.confirm_return_borrow_slip",
        return_value=(False, "error"),
    )

    response = test_client.post("/slip/approve/1")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/slip?status=pending")


def test_approve_slip_exception_redirects(test_client, admin_user, mocker):
    login_as(test_client, admin_user)
    mocker.patch(
        "libraryapp.routes.slip_management.confirm_return_borrow_slip",
        side_effect=Exception("boom"),
    )

    response = test_client.post("/slip/approve/1")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/slip?status=pending")


def test_return_slip_route_returns_json(test_client, sample_user, mocker):
    login_as(test_client, sample_user)
    mock_return = mocker.patch("libraryapp.routes.return_slips.return_slip", return_value=(True, "ok"))

    response = test_client.post("/return-slip/10")

    assert response.status_code == 200
    assert response.get_json() == {"success": True, "message": "ok"}
    mock_return.assert_called_once_with(10, sample_user.id)


def test_return_slip_route_requires_login(test_client):
    response = test_client.post("/return-slip/10")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
