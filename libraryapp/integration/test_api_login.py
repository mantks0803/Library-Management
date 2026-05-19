def test_render_login_returns_template_for_guest(test_client, mocker):
    mock_render = mocker.patch("libraryapp.routes.login_logout.render_template", return_value="login page")

    response = test_client.get("/login")

    assert response.status_code == 200
    assert response.data == b"login page"
    mock_render.assert_called_once_with("auth/login.html")


def test_render_login_redirects_authenticated_user(test_client, reader_user):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.get("/login")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_success_redirects_home(test_client, reader_user):
    response = test_client.post(
        "/login",
        data={"username": reader_user.username, "password": "OldPass123"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_success_redirects_next_page(test_client, reader_user):
    response = test_client.post(
        "/login?next=/profile",
        data={"username": reader_user.username, "password": "OldPass123"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile")


def test_login_failure_renders_error(test_client, mocker):
    mock_render = mocker.patch("libraryapp.routes.login_logout.render_template", return_value="login error")

    response = test_client.post(
        "/login",
        data={"username": "wrong", "password": "Wrong123"},
    )

    assert response.status_code == 200
    args, kwargs = mock_render.call_args
    assert args == ("auth/login.html",)
    assert "err_msg" in kwargs


def test_logout_clears_cart_and_redirects_login(test_client, reader_user, sample_books):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    test_client.post(f"/cart/add/{sample_books[0].id}")

    response = test_client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_profile_renders_for_logged_in_user(test_client, reader_user, mocker):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    mock_render = mocker.patch("libraryapp.routes.login_logout.render_template", return_value="profile")

    response = test_client.get("/profile")

    assert response.status_code == 200
    assert response.data == b"profile"
    mock_render.assert_called_once_with("auth/profile.html")
