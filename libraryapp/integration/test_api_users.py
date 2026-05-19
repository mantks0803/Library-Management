from libraryapp.models import User
from libraryapp.utils import hash_password


def test_update_user_success_returns_json_and_updates_database(test_client, reader_user):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.put(
        f"/api/users/{reader_user.id}",
        data={"name": "Reader Updated", "phone": "0912345678"},
    )

    assert response.status_code == 200
    assert response.get_json()["ok"] is True

    updated_user = User.query.get(reader_user.id)
    assert updated_user.name == "Reader Updated"
    assert updated_user.phone == "0912345678"


def test_update_user_invalid_phone_returns_error_json(test_client, reader_user):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.put(
        f"/api/users/{reader_user.id}",
        data={"name": "Reader Updated", "phone": "123"},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is False
    assert "Số điện thoại không hợp lệ" in data["error"]


def test_update_user_requires_login(test_client, reader_user):
    response = test_client.put(
        f"/api/users/{reader_user.id}",
        data={"name": "No Login", "phone": "0912345678"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_change_password_success_returns_json_and_updates_password(test_client, reader_user):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.put(
        "/api/users/change-password",
        data={
            "old_password": "OldPass123",
            "new_password": "NewPass123",
            "confirm_password": "NewPass123",
        },
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is True

    updated_user = User.query.get(reader_user.id)
    assert updated_user.password == hash_password("NewPass123")


def test_change_password_wrong_old_password_returns_error_json(test_client, reader_user):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.put(
        "/api/users/change-password",
        data={
            "old_password": "WrongPass123",
            "new_password": "NewPass123",
            "confirm_password": "NewPass123",
        },
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is False
    assert "Mật khẩu hiện tại không chính xác" in data["error"]


def test_change_password_confirm_mismatch_returns_error_json(test_client, reader_user):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.put(
        "/api/users/change-password",
        data={
            "old_password": "OldPass123",
            "new_password": "NewPass123",
            "confirm_password": "Different123",
        },
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is False
    assert "Mật khẩu xác nhận không khớp" in data["error"]


def test_change_password_invalid_new_password_returns_error_json(test_client, reader_user):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.put(
        "/api/users/change-password",
        data={
            "old_password": "OldPass123",
            "new_password": "short",
            "confirm_password": "short",
        },
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is False
    assert "Mật khẩu" in data["error"]
