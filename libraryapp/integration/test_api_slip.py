from libraryapp import db
from libraryapp.models import BorrowSlip, BorrowSlipStatus


def test_slip_management_route_for_admin(test_client, admin_user, borrowing_slip, mocker):
    from libraryapp.integration.conftest import login_as

    login_as(test_client, admin_user)
    mocker.patch("libraryapp.routes.slip_management.check_and_update_overdue_slips")
    mock_render = mocker.patch("libraryapp.routes.slip_management.render_template", return_value="slip admin")

    response = test_client.get("/slip?status=borrowing")

    assert response.status_code == 200
    args, kwargs = mock_render.call_args
    assert args == ("admin/slip_management.html",)
    assert kwargs["total_slips"] == 1
    assert kwargs["status_filter"] == "borrowing"


def test_slip_approve_route_redirects(test_client, admin_user, borrowing_slip):
    from libraryapp.integration.conftest import login_as

    borrowing_slip.status = BorrowSlipStatus.PENDING
    db.session.commit()
    login_as(test_client, admin_user)

    response = test_client.post(f"/slip/approve/{borrowing_slip.id}")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/slip?status=pending")
    assert BorrowSlip.query.get(borrowing_slip.id).status == BorrowSlipStatus.RETURNED
