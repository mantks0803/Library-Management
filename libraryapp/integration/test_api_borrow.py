from libraryapp import db
from libraryapp.models import BorrowSlip, Reader, ReaderStatus


def test_cart_view_renders_books_for_reader(test_client, reader_user, sample_books, mocker):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    mock_render = mocker.patch("libraryapp.routes.borrow_cart.render_template", return_value="cart view")
    test_client.post(f"/cart/add/{sample_books[0].id}")

    response = test_client.get("/cart/view")

    assert response.status_code == 200
    args, kwargs = mock_render.call_args
    assert args == ("reader/borrow_cart.html",)
    assert kwargs["cart_count"] == 1
    assert kwargs["books"][0].id == sample_books[0].id


def test_cart_confirm_success_creates_borrow_slip_and_clears_cart(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    test_client.post(f"/cart/add/{sample_books[0].id}")

    response = test_client.post("/cart/confirm")

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert BorrowSlip.query.filter_by(reader_id=reader_user.id).count() == 1
    assert test_client.get("/cart/count").get_json() == {"count": 0}


def test_cart_confirm_rejects_locked_reader(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    Reader.query.get(reader_user.id).status = ReaderStatus.LOCKED
    db.session.commit()
    test_client.post(f"/cart/add/{sample_books[0].id}")

    response = test_client.post("/cart/confirm")

    data = response.get_json()
    assert data["success"] is False
    assert data["message"]
