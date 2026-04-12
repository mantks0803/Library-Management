from libraryapp.models import BorrowSlip, BorrowSlipDetail
from libraryapp import db, app

def get_reader_borrow_slips(reader_id, page=1):

    query = BorrowSlip.query.filter(BorrowSlip.reader_id == reader_id)
    count = query.count()
    query = query.order_by(BorrowSlip.borrow_date.desc())
    start = (page - 1) * app.config.get('PAGE_SIZE', 10)
    return query.slice(start, start + app.config.get('PAGE_SIZE', 10)).all(), count


def get_borrow_slip(slip_id):
    return BorrowSlip.query.get(slip_id)


def get_borrow_slip_details(slip_id):
    return db.session.query(BorrowSlipDetail).filter(
        BorrowSlipDetail.borrow_slip_id == slip_id).all()


def get_all_reader_borrow_details(reader_id):

    return db.session.query(BorrowSlipDetail).join(
        BorrowSlip, BorrowSlipDetail.borrow_slip_id == BorrowSlip.id
    ).filter(BorrowSlip.reader_id == reader_id).all()
