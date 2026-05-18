from flask import current_app

from libraryapp.models import BorrowSlip, BorrowSlipDetail, BorrowSlipStatus
from libraryapp import db, app
from sqlalchemy import and_

def get_reader_borrow_slips(reader_id, page=1):

    query = BorrowSlip.query.filter(BorrowSlip.reader_id == reader_id)
    count = query.count()
    query = query.order_by(BorrowSlip.borrow_date.desc())
    start = (page - 1) * current_app.config.get('PAGE_SIZE', 10)
    return query.slice(start, start + current_app.config.get('PAGE_SIZE', 10)).all(), count


def get_borrow_slip_status_overdue(reader_id):
    slips = BorrowSlip.query.filter(
        and_(
            BorrowSlip.reader_id == reader_id,
            BorrowSlip.status == BorrowSlipStatus.OVERDUE
        )
    )
    return slips.all()


def get_borrow_slip_details(slip_id):
    return db.session.query(BorrowSlipDetail).filter(
        BorrowSlipDetail.borrow_slip_id == slip_id).all()


def get_all_reader_borrow_details(reader_id):

    return db.session.query(BorrowSlipDetail).join(
        BorrowSlip, BorrowSlipDetail.borrow_slip_id == BorrowSlip.id
    ).filter(BorrowSlip.reader_id == reader_id).all()


def count_reader_borrowing_books(reader_id):
    count = db.session.query(BorrowSlipDetail).join(
        BorrowSlip, BorrowSlipDetail.borrow_slip_id == BorrowSlip.id
    ).filter(
        BorrowSlip.reader_id == reader_id,
        BorrowSlipDetail.is_returned == False,
        BorrowSlip.status.in_([BorrowSlipStatus.BORROWING, BorrowSlipStatus.PENDING])
    ).count()
    return count

