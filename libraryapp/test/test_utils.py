import pytest
from werkzeug.exceptions import Forbidden

from libraryapp.models import UserRole
from libraryapp.test.test_base import test_app, test_client
from libraryapp.utils import hash_password, is_image, permission


def test_hash_password_strips_before_hashing():
    assert hash_password(" pass ") == hash_password("pass")


def test_is_image_accepts_common_extensions():
    assert is_image("cover.JPG") is True
    assert is_image("cover.png") is True
    assert is_image("cover.txt") is False


def test_permission_redirects_guest(test_client, mocker):
    mocker.patch("libraryapp.utils.current_user", mocker.Mock(is_authenticated=False))

    @permission()
    def protected():
        return "ok"

    with test_client.application.test_request_context("/"):
        response = protected()

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_permission_blocks_role_when_access_false(test_client, mocker):
    mocker.patch(
        "libraryapp.utils.current_user",
        mocker.Mock(is_authenticated=True, user_role=UserRole.READER),
    )

    with test_client.application.test_request_context("/"):
        @permission(allow={"roles": [UserRole.READER], "access": False})
        def protected():
            return "ok"

        with pytest.raises(Forbidden):
            protected()


def test_permission_allows_other_role_when_access_false(test_client, mocker):
    mocker.patch(
        "libraryapp.utils.current_user",
        mocker.Mock(is_authenticated=True, user_role=UserRole.ADMIN),
    )

    with test_client.application.test_request_context("/"):
        @permission(allow={"roles": [UserRole.READER], "access": False})
        def protected():
            return "ok"

        response = protected()

    assert response == "ok"
