from libraryapp.admin import AuthenticatedModelView, BorrowSlipView, StandardAdminIndexView
from libraryapp import db
from libraryapp.models import BorrowSlip, UserRole
from libraryapp.test.test_base import test_app


def test_standard_admin_accessible_for_admin(mocker):
    mocker.patch(
        "libraryapp.admin.current_user",
        mocker.Mock(is_authenticated=True, user_role=UserRole.ADMIN),
    )

    assert StandardAdminIndexView().is_accessible() is True


def test_standard_admin_not_accessible_for_reader(mocker):
    mocker.patch(
        "libraryapp.admin.current_user",
        mocker.Mock(is_authenticated=True, user_role=UserRole.READER),
    )

    assert StandardAdminIndexView().is_accessible() is False


def test_authenticated_model_view_accessible_for_admin(mocker):
    mocker.patch(
        "libraryapp.admin.current_user",
        mocker.Mock(is_authenticated=True, user_role=UserRole.ADMIN),
    )
    view = AuthenticatedModelView(BorrowSlip, db.session)

    assert view.is_accessible() is True


def test_standard_admin_index_redirects(test_app, mocker):
    mocker.patch(
        "libraryapp.admin.current_user",
        mocker.Mock(is_authenticated=True, user_role=UserRole.ADMIN),
    )
    mocker.patch("libraryapp.admin.url_for", return_value="/book/")

    with test_app.test_request_context("/admin/"):
        response = StandardAdminIndexView().index()

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/book/")


def test_borrow_slip_view_approve_return_success(test_app, mocker):
    mocker.patch(
        "libraryapp.admin.current_user",
        mocker.Mock(is_authenticated=True, user_role=UserRole.ADMIN),
    )
    mock_confirm = mocker.patch(
        "libraryapp.admin.confirm_return_borrow_slip",
        return_value=(True, "ok"),
    )
    mock_flash = mocker.patch("libraryapp.admin.flash")
    mocker.patch("libraryapp.admin.url_for", return_value="/admin/borrow-slip/")
    view = BorrowSlipView(BorrowSlip, db.session)

    with test_app.test_request_context("/admin/borrow-slip/approve_return/1"):
        response = view.approve_return(1)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/borrow-slip/")
    mock_confirm.assert_called_once_with(1)
    mock_flash.assert_called_once_with("ok", "success")


def test_borrow_slip_view_approve_return_failure(test_app, mocker):
    mocker.patch(
        "libraryapp.admin.current_user",
        mocker.Mock(is_authenticated=True, user_role=UserRole.ADMIN),
    )
    mocker.patch(
        "libraryapp.admin.confirm_return_borrow_slip",
        return_value=(False, "error"),
    )
    mock_flash = mocker.patch("libraryapp.admin.flash")
    mocker.patch("libraryapp.admin.url_for", return_value="/admin/borrow-slip/")
    view = BorrowSlipView(BorrowSlip, db.session)

    with test_app.test_request_context("/admin/borrow-slip/approve_return/1"):
        response = view.approve_return(1)

    assert response.status_code == 302
    mock_flash.assert_called_once_with("error", "error")
