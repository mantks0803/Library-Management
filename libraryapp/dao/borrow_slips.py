from datetime import datetime, timedelta
from libraryapp import db, app
from libraryapp.models import BorrowSlip, BorrowSlipDetail, Book, Reader, User, UserRole, BorrowSlipStatus
from sqlalchemy import and_, func, or_
from flask_login import current_user


def create_borrow_slip_multiple(reader_id, book_ids, borrow_date=None, days=7):

    if not book_ids:
        return None, []

    try:
        if not borrow_date:
            borrow_date = datetime.now()

        due_date = borrow_date + timedelta(days=days)

        borrow_slip = BorrowSlip(
            reader_id=reader_id,
            borrow_date=borrow_date,
            status=BorrowSlipStatus.BORROWING,
            penalty_fee=0,
            due_date=due_date
        )
        db.session.add(borrow_slip)
        db.session.flush()

        details = []
        for book_id in book_ids:
            book = Book.query.get(book_id)
            if not book or book.quantity <= 0:
                continue

            borrow_slip_detail = BorrowSlipDetail(
                borrow_slip_id=borrow_slip.id,
                book_id=book_id,
                return_date=None,
                is_returned=False
            )
            db.session.add(borrow_slip_detail)
            details.append(borrow_slip_detail)
            book.quantity -= 1

        db.session.commit()
        return borrow_slip, details
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi tạo phiếu mượn nhiều sách: {e}")
        return None, []

