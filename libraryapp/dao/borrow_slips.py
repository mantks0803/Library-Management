from datetime import datetime, timedelta
from libraryapp import db, app
from libraryapp.dao.borrow_history import get_borrow_slip_status_overdue
from libraryapp.models import BorrowSlip, BorrowSlipDetail, Book, Reader, User, UserRole, BorrowSlipStatus, ReaderStatus
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


def request_return_borrow_slip(slip_id):
    slip = BorrowSlip.query.get(slip_id)
    if slip and slip.status != BorrowSlipStatus.RETURNED:
        slip.status = BorrowSlipStatus.PENDING
        db.session.commit()
        return True, "Đã gửi yêu cầu trả sách. Vui lòng đợi Admin duyệt!"
    return False, "Phiếu không hợp lệ!"


def confirm_return_borrow_slip(slip_id):
    slip = BorrowSlip.query.get(slip_id)
    if not slip or slip.status != BorrowSlipStatus.PENDING:
        return False, "Phiếu không ở trạng thái chờ duyệt!"

    details = BorrowSlipDetail.query.filter_by(borrow_slip_id=slip_id, is_returned=False).all()
    for detail in details:
        detail.is_returned = True
        detail.return_date = datetime.now()
        book = Book.query.get(detail.book_id)
        if book:
            book.quantity += 1

    slip.status = BorrowSlipStatus.RETURNED

    remaining_overdue = len(get_borrow_slip_status_overdue(slip.reader_id))

    if remaining_overdue == 0:
        reader = Reader.query.get(slip.reader_id)
        if reader:
            reader.status = ReaderStatus.ACTIVE

    db.session.commit()
    return True, "Đã duyệt trả sách thành công!"


def check_and_update_overdue_slips():
    try:
        now = datetime.now().date()

        # Tìm tất cả phiếu BORROWING mà due_date < hôm nay
        overdue_slips = BorrowSlip.query.filter(
            and_(
                BorrowSlip.status.in_([
                    BorrowSlipStatus.BORROWING,
                    BorrowSlipStatus.OVERDUE
                ]),
                BorrowSlip.due_date < now
            )
        ).all()

        PENALTY_PER_DAY = 10000  # 10,000đ/ngày quá hạn

        for slip in overdue_slips:
            overdue_days = (now - slip.due_date.date()).days
            penalty_fee = overdue_days * PENALTY_PER_DAY

            # Cập nhật status và phí phạt
            slip.status = BorrowSlipStatus.OVERDUE
            slip.penalty_fee = penalty_fee

            reader = Reader.query.get(slip.reader_id)
            if reader:
                reader.status = ReaderStatus.LOCKED


        if overdue_slips:
            db.session.commit()
            print(f"✓ Cập nhật {len(overdue_slips)} phiếu quá hạn")

        return len(overdue_slips)

    except Exception as e:
        db.session.rollback()
        print(f"✗ Lỗi khi cập nhật quá hạn: {e}")
        return 0
