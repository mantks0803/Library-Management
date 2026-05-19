def test_guest_cart_helpers_use_default_session_key(test_app):
    from flask import session
    from libraryapp.api.api_cart import CART_SESSION_KEY, clear_cart, get_cart, save_cart

    with test_app.test_request_context("/"):
        save_cart([1, 2])

        assert session[CART_SESSION_KEY] == [1, 2]
        assert get_cart() == [1, 2]

        clear_cart()
        assert CART_SESSION_KEY not in session


def test_cart_count_requires_login(test_client):
    response = test_client.get("/cart/count")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_cart_count_initially_zero_for_reader(test_client, reader_user):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.get("/cart/count")

    assert response.status_code == 200
    assert response.get_json() == {"count": 0}


def test_add_book_to_cart_success(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    book = sample_books[0]

    response = test_client.post(f"/cart/add/{book.id}")

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["cart_count"] == 1
    assert book.title in data["message"]


def test_add_duplicate_book_to_cart_returns_error(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    book = sample_books[0]

    test_client.post(f"/cart/add/{book.id}")
    response = test_client.post(f"/cart/add/{book.id}")

    data = response.get_json()
    assert data["success"] is False
    assert "đã có trong giỏ" in data["message"]


def test_add_out_of_stock_book_returns_error(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    out_of_stock_book = sample_books[-1]

    response = test_client.post(f"/cart/add/{out_of_stock_book.id}")

    data = response.get_json()
    assert data["success"] is False
    assert "hết" in data["message"]


def test_cart_limit_is_five_books(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    for book in sample_books[:5]:
        response = test_client.post(f"/cart/add/{book.id}")
        assert response.get_json()["success"] is True

    response = test_client.post(f"/cart/add/{sample_books[5].id}")

    data = response.get_json()
    assert data["success"] is False
    assert "tối đa 5" in data["message"]


def test_remove_book_from_cart_success(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    book = sample_books[0]

    test_client.post(f"/cart/add/{book.id}")
    response = test_client.post(f"/cart/remove/{book.id}")

    data = response.get_json()
    assert data["success"] is True
    assert data["cart_count"] == 0


def test_remove_missing_book_from_cart_returns_error(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.post(f"/cart/remove/{sample_books[0].id}")

    data = response.get_json()
    assert data["success"] is False
    assert "không có trong giỏ" in data["message"]


def test_clear_cart_success(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    test_client.post(f"/cart/add/{sample_books[0].id}")
    test_client.post(f"/cart/add/{sample_books[1].id}")
    response = test_client.post("/cart/clear")

    data = response.get_json()
    assert data["success"] is True
    assert test_client.get("/cart/count").get_json() == {"count": 0}


def test_cart_api_forbidden_for_admin(test_client, admin_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, admin_user)

    response = test_client.post(f"/cart/add/{sample_books[0].id}")

    assert response.status_code == 403
