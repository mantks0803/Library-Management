from datetime import datetime, timedelta

from libraryapp.dao.borrow_slips import check_and_update_overdue_slips
from libraryapp.models import BorrowSlip, BorrowSlipStatus, Reader, ReaderStatus, User, UserRole
from libraryapp.utils import hash_password
from libraryapp.test.test_base import sample_reader, test_app, test_session


def test_check_and_update_overdue_slips_locks_reader(test_session, sample_reader):
    slip = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now() - timedelta(days=10),
        due_date=datetime.now() - timedelta(days=3),
        status=BorrowSlipStatus.BORROWING,
        penalty_fee=0,
    )
    test_session.add(slip)
    test_session.commit()

    total = check_and_update_overdue_slips()

    updated_slip = BorrowSlip.query.get(slip.id)
    updated_reader = Reader.query.get(sample_reader.id)
    assert total == 1
    assert updated_slip.status == BorrowSlipStatus.OVERDUE
    assert updated_slip.penalty_fee == 30000
    assert updated_reader.status == ReaderStatus.LOCKED


def test_check_and_update_overdue_slips_returns_zero_when_none(test_session, sample_reader):
    slip = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=3),
        status=BorrowSlipStatus.BORROWING,
        penalty_fee=0,
    )
    test_session.add(slip)
    test_session.commit()

    total = check_and_update_overdue_slips()

    assert total == 0
    assert BorrowSlip.query.get(slip.id).status == BorrowSlipStatus.BORROWING


def test_check_and_update_overdue_slips_filters_by_reader(test_session, sample_reader):
    other_user = User(
        name="Other Reader",
        username="other_reader",
        password=hash_password("Password123"),
        phone="0900000001",
        email="other@gmail.com",
        user_role=UserRole.READER,
    )
    test_session.add(other_user)
    test_session.flush()
    other_reader = Reader(id=other_user.id, status=ReaderStatus.ACTIVE)
    test_session.add(other_reader)
    test_session.flush()

    sample_slip = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now() - timedelta(days=10),
        due_date=datetime.now() - timedelta(days=2),
        status=BorrowSlipStatus.BORROWING,
        penalty_fee=0,
    )
    other_slip = BorrowSlip(
        reader_id=other_reader.id,
        borrow_date=datetime.now() - timedelta(days=10),
        due_date=datetime.now() - timedelta(days=2),
        status=BorrowSlipStatus.BORROWING,
        penalty_fee=0,
    )
    test_session.add_all([sample_slip, other_slip])
    test_session.commit()

    total = check_and_update_overdue_slips(sample_reader.id)

    assert total == 1
    assert BorrowSlip.query.get(sample_slip.id).status == BorrowSlipStatus.OVERDUE
    assert BorrowSlip.query.get(other_slip.id).status == BorrowSlipStatus.BORROWING

def test_check_and_update_overdue_slips_rolls_back_on_error(test_session, sample_reader, mocker):
    slip = BorrowSlip(
        reader_id=sample_reader.id,
        borrow_date=datetime.now() - timedelta(days=10),
        due_date=datetime.now() - timedelta(days=3),
        status=BorrowSlipStatus.BORROWING,
        penalty_fee=0,
    )
    test_session.add(slip)
    test_session.commit()
    mocker.patch("libraryapp.dao.borrow_slips.db.session.commit", side_effect=Exception("db error"))
    mock_rollback = mocker.patch("libraryapp.dao.borrow_slips.db.session.rollback")

    total = check_and_update_overdue_slips()

    assert total == 0
    mock_rollback.assert_called_once()
