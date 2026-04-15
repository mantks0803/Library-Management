from libraryapp.models import BorrowSlip, BorrowSlipDetail, BorrowSlipStatus, Book
from datetime import datetime
from libraryapp import db

# Tính phí phạt (ví dụ: 10.000đ/ngày quá hạn)
PENALTY_PER_DAY = 10000

def return_slip(slip_id, current_reader_id):
    try:
        slip = BorrowSlip.query.get(slip_id)

        if slip.reader_id != current_reader_id:
            return False, "Bạn không có quyền trả phiếu mượn này!"

        if not slip:
            return False, "Phiếu mượn không tồn tại!"

        if slip.status == BorrowSlipStatus.RETURNED:
            return False, "Phiếu mươn này đã được trả rồi!"

        details = BorrowSlipDetail.query.filter_by(borrow_slip_id=slip_id, is_returned=False).all()


        return_date = datetime.now()

        # Kiểm tra trả quá hạn
        is_overdue = return_date > slip.due_date

        # Tính phí phạt nếu quá hạn
        penalty_fee = 0
        if is_overdue:
            overdue_days = (return_date - slip.due_date).days
            penalty_fee = overdue_days * PENALTY_PER_DAY

        for detail in details:
            detail.is_returned = True
            detail.return_date = return_date

            # Trả sách vào kho
            book = Book.query.get(detail.book_id)
            if book:
                book.quantity += 1

        # Cập nhật trạng thái phiếu mượn
        slip.status = BorrowSlipStatus.OVERDUE if is_overdue else BorrowSlipStatus.RETURNED
        slip.penalty_fee = penalty_fee

        db.session.commit()

        if is_overdue:
            message = f"Trả sách thành công! Phí phạt quá hạn: {penalty_fee:,.0f}đ ({(return_date - slip.due_date).days} ngày quá hạn)"
        else:
            message = "Trả sách thành công!"

        return True, message

    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi trả sách: {e}")
        return False, f"Lỗi hệ thống khi xử lý trả sách: {str(e)}"
