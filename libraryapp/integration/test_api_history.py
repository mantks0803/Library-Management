from libraryapp.models import BorrowSlip, BorrowSlipStatus, Reader, ReaderStatus, User, UserRole
from libraryapp.utils import hash_password


def test_history_route_renders_reader_history(test_client, reader_user, borrowing_slip, mocker):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)
    mock_render = mocker.patch("libraryapp.routes.borrow_history.render_template", return_value="history")

    response = test_client.get("/history")

    assert response.status_code == 200
    args, kwargs = mock_render.call_args
    assert args == ("reader/history.html",)
    assert len(kwargs["history_list"]) == 1
    assert kwargs["history_list"][0]["slip_id"] == borrowing_slip.id


def test_history_return_slip_api_marks_slip_pending(test_client, reader_user, borrowing_slip):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.post(f"/api/return-slip/{borrowing_slip.id}")

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert BorrowSlip.query.get(borrowing_slip.id).status == BorrowSlipStatus.PENDING


def test_history_return_slip_api_rejects_other_reader_slip(test_client, test_session, borrowing_slip):
    from libraryapp.integration.conftest import login_as

    other_user = User(
        name="Other Reader",
        phone="0900000001",
        email="other@mail.com",
        username="other_reader",
        password=hash_password("OtherPass123"),
        user_role=UserRole.READER,
    )
    test_session.add(other_user)
    test_session.flush()
    test_session.add(Reader(id=other_user.id, status=ReaderStatus.ACTIVE))
    test_session.commit()

    login_as(test_client, other_user)

    response = test_client.post(f"/api/return-slip/{borrowing_slip.id}")

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is False
    assert "không có quyền" in data["message"]
    assert BorrowSlip.query.get(borrowing_slip.id).status == BorrowSlipStatus.BORROWING


def test_return_slip_route_returns_json(test_client, reader_user, borrowing_slip):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, reader_user)

    response = test_client.post(f"/return-slip/{borrowing_slip.id}")

    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert BorrowSlip.query.get(borrowing_slip.id).status == BorrowSlipStatus.RETURNED
