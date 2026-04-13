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
                status=BorrowSlipStatus.BORROWING,
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




def return_book(slip_detail_id, return_date=None):
    """
    Trả sách của phiếu mượn

    Args:
        slip_detail_id: ID của chi tiết phiếu mượn
        return_date: ngày trả (mặc định hôm nay)

    Returns:
        BorrowSlipDetail: đối tượng chi tiết đã cập nhật
    """
    if not return_date:
        return_date = datetime.now()

    slip_detail = BorrowSlipDetail.query.get(slip_detail_id)
    if not slip_detail:
        return None

    slip_detail.return_date = return_date
    slip_detail.is_returned = True

    book = Book.query.get(slip_detail.book_id)
    if book:
        book.quantity += 1

    # Cập nhật status của BorrowSlipDetail
    borrow_slip = BorrowSlip.query.get(slip_detail.borrow_slip_id)
    if borrow_slip:
        # Xác định status: Nếu trả trễ hạn của phiếu → status OVERDUE, ngược lại RETURNED
        if return_date > borrow_slip.due_date:
            slip_detail.status = BorrowSlipStatus.OVERDUE
        else:
            slip_detail.status = BorrowSlipStatus.RETURNED

        # Kiểm tra xem đã trả hết sách trong phiếu chưa
        all_returned = all(d.is_returned for d in borrow_slip.borrow_slip_details)
        if all_returned:
            # Tính phí phạt khi tất cả sách đã trả
            max_return_date = max(d.return_date for d in borrow_slip.borrow_slip_details)
            if max_return_date > borrow_slip.due_date:
                borrow_slip.penalty_fee = calculate_penalty_fee(borrow_slip.due_date, max_return_date)
            else:
                borrow_slip.penalty_fee = 0

    db.session.commit()
    return slip_detail


def calculate_penalty_fee(due_date, return_date, fee_per_day=10000):
    """
    Tính phí phạt dựa trên số ngày trễ
    
    Args:
        due_date: ngày hạn trả
        return_date: ngày trả thực tế
        fee_per_day: phí phạt/ngày (mặc định 10,000 đồng)
    
    Returns:
        float: số tiền phạt
    """
    if return_date <= due_date:
        return 0
    
    days_late = (return_date - due_date).days
    return days_late * fee_per_day


def get_overdue_borrow_slips(page=1):
    """
    Lấy danh sách phiếu mượn quá hạn
    
    Args:
        page: trang (mặc định 1)

    Returns:
        tuple: (list borrow_slips, count)
    """
    query = db.session.query(BorrowSlip).filter(
        and_(
            BorrowSlip.due_date < datetime.now(),
            BorrowSlip.borrow_slip_details.any(BorrowSlipDetail.is_returned == False)
        ))
    count = query.count()
    query = query.order_by(BorrowSlip.due_date)
    start = (page - 1) * app.config.get('PAGE_SIZE', 10)
    return query.slice(start, start + app.config.get('PAGE_SIZE', 10)).all(), count


def delete_borrow_slip(slip_id):
    """
    Xóa phiếu mươn
    
    Args:
        slip_id: ID của phiếu mượn

    Returns:
        BorrowSlip: đối tượng phiếu mượn đã xóa hoặc None
    """
    borrow_slip = BorrowSlip.query.get(slip_id)
    if not borrow_slip:
        return None

    db.session.delete(borrow_slip)
    db.session.commit()
    return borrow_slip


