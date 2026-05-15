from datetime import datetime, timedelta

from libraryapp import BorrowSlip, db
from libraryapp.dao.books import get_all_book_types
from libraryapp.dao.borrow_slips import request_return_borrow_slip, confirm_return_borrow_slip
from libraryapp.dao.return_slips import return_slip
from libraryapp.models import BorrowSlipStatus, Book
from libraryapp.test.test_base import sample_slip, sample_slip_pending, sample_borrow_details,\
    test_session, test_app,\
    sample_slip_borrowing, sample_details_return, sample_reader, sample_books_borrow

def test_request_return_success(test_session, sample_slip):
    ok, msg = request_return_borrow_slip(sample_slip.id)

    assert ok is True
    assert "Đã gửi yêu cầu trả sách. Vui lòng đợi Admin duyệt!" in msg

    updated = BorrowSlip.query.get(sample_slip.id)
    assert updated.status == BorrowSlipStatus.PENDING

def test_request_return_already_returned(test_session, sample_slip):
    sample_slip.status = BorrowSlipStatus.RETURNED
    test_session.commit()

    ok, msg = request_return_borrow_slip(sample_slip.id)

    assert ok is False
    assert msg == "Phiếu không hợp lệ!"

def test_confirm_return_success(test_session, sample_slip_pending, sample_borrow_details):
    book_id = sample_borrow_details[0].book_id
    old_qty = Book.query.get(book_id).quantity

    ok, msg = confirm_return_borrow_slip(sample_slip_pending.id)

    assert ok is True
    assert "thành công" in msg


    updated_slip = BorrowSlip.query.get(sample_slip_pending.id)
    assert updated_slip.status == BorrowSlipStatus.RETURNED


    detail = sample_borrow_details[0]
    assert detail.is_returned is True
    assert detail.return_date is not None


    assert Book.query.get(book_id).quantity == old_qty + 1

def test_confirm_return_not_found(test_session):
    ok, msg = confirm_return_borrow_slip(99999)

    assert ok is False
    assert msg == "Phiếu không ở trạng thái chờ duyệt!"

def test_confirm_return_wrong_status(test_session, sample_slip_pending):
    sample_slip_pending.status = BorrowSlipStatus.BORROWING
    test_session.commit()

    ok, msg = confirm_return_borrow_slip(sample_slip_pending.id)

    assert ok is False

def test_confirm_return_no_details(test_session, sample_slip_pending):
    ok, msg = confirm_return_borrow_slip(sample_slip_pending.id)
    assert ok is True

def test_return_slip_success(test_session, sample_slip_borrowing, sample_details_return):
    book_id = sample_details_return[0].book_id
    old_qty = Book.query.get(book_id).quantity

    ok, msg = return_slip(sample_slip_borrowing.id, sample_slip_borrowing.reader_id)

    assert ok is True
    assert "Trả sách thành công" in msg

    updated = BorrowSlip.query.get(sample_slip_borrowing.id)
    assert updated.status == BorrowSlipStatus.RETURNED

    d = sample_details_return[0]

    assert d.is_returned is True
    assert d.return_date is not None
    assert Book.query.get(book_id).quantity == old_qty + 1

def test_return_slip_wrong_user(test_session, sample_slip_borrowing):

    ok, msg = return_slip(sample_slip_borrowing.id, current_reader_id=999)

    assert ok is False
    assert "không có quyền" in msg

def test_return_slip_not_found(test_session):
    ok, msg = return_slip(99999, 1)

    assert ok is False
    assert msg == "Phiếu mượn không tồn tại!"

def test_return_slip_already_returned(test_session, sample_slip_borrowing):
    sample_slip_borrowing.status = BorrowSlipStatus.RETURNED
    test_session.commit()

    ok, msg = return_slip(sample_slip_borrowing.id, sample_slip_borrowing.reader_id)

    assert ok is False
    assert "đã được trả rồi" in msg

def test_return_slip_overdue(test_session, sample_slip_borrowing, sample_details_return):
    sample_slip_borrowing.due_date = datetime.now() - timedelta(days=2)
    test_session.commit()

    ok, msg = return_slip(sample_slip_borrowing.id, sample_slip_borrowing.reader_id)

    assert ok is True
    assert "Phí phạt" in msg

    updated = BorrowSlip.query.get(sample_slip_borrowing.id)
    assert updated.status == BorrowSlipStatus.OVERDUE
    assert updated.penalty_fee > 0

def test_return_slip_exception(test_session, sample_slip_borrowing, sample_details_return, mocker):
    mocker.patch.object(db.session, "commit", side_effect=Exception("DB error"))

    ok, msg = return_slip(sample_slip_borrowing.id, sample_slip_borrowing.reader_id)

    assert ok is False
    assert "Lỗi hệ thống" in msg

def test_get_all_book_types(test_session):
    books = [
        Book(title="A", author="a", type="Programming", active=True),
        Book(title="B", author="b", type="Programming", active=True),
        Book(title="C", author="c", type="Novel", active=True),
    ]

    test_session.add_all(books)
    test_session.commit()

    result = get_all_book_types()

    assert "Programming" in result
    assert "Novel" in result
    assert len(result) == 2


