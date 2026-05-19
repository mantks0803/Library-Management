from libraryapp.models import User


def test_register_get_route(test_client, mocker):
    mock_render = mocker.patch("libraryapp.routes.register.render_template", return_value="register")

    response = test_client.get("/register")

    assert response.status_code == 200
    mock_render.assert_called_once_with("auth/register.html", form={})


def test_register_post_success_creates_user(test_client):
    response = test_client.post(
        "/register",
        data={
            "name": "New Reader",
            "phone": "0912345678",
            "email": "newreader@mail.com",
            "username": "newreader",
            "password": "NewPass123",
            "confirm": "NewPass123",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert User.query.filter_by(username="newreader").first() is not None


def test_register_post_invalid_payload_renders_error(test_client, mocker):
    mock_render = mocker.patch("libraryapp.routes.register.render_template", return_value="register error")

    response = test_client.post(
        "/register",
        data={
            "name": "",
            "phone": "0912345678",
            "email": "newreader@mail.com",
            "username": "newreader",
            "password": "NewPass123",
            "confirm": "NewPass123",
        },
    )

    assert response.status_code == 200
    assert "err_msg" in mock_render.call_args.kwargs
