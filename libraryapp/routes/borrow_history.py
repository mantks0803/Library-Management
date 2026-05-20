from flask import Blueprint, render_template, jsonify
from flask_login import current_user
from libraryapp.utils import permission
from libraryapp.dao.users import get_current_user
from libraryapp.dao.books import get_book
from libraryapp.dao.readers import get_reader
from libraryapp.dao.borrow_history import get_reader_borrow_slips
from libraryapp.models import BorrowSlipStatus, UserRole
from libraryapp.dao.borrow_slips import request_return_borrow_slip
from datetime import datetime

history_bp = Blueprint('borrow_history', __name__)

@history_bp.route('/history', methods=['GET'])
@permission(allow={
    "roles": [UserRole.READER],
    "access": True
})
def render_borrow_history():
    user = get_current_user(current_user.id)
    reader = get_reader(user.id)

    history_list = []

    if reader:
        borrow_slips, count = get_reader_borrow_slips(reader.id)

        for borrow_slip in borrow_slips:
            if borrow_slip.status == BorrowSlipStatus.RETURNED:
                status = 'Đã trả'
            elif borrow_slip.status == BorrowSlipStatus.OVERDUE:
                status = 'Quá hạn'
            elif borrow_slip.status == BorrowSlipStatus.PENDING:
                status = 'Chờ duyệt'
            else:
                status = 'Đang mượn'

            details = borrow_slip.borrow_slip_details
            books = []
            for detail in details:
                book = get_book(detail.book_id)
                if book:
                    books.append({
                        'detail_id': detail.id,
                        'title': book.title,
                        'return_date': detail.return_date.strftime('%d/%m/%Y') if detail.return_date else None,
                        'is_returned': detail.is_returned
                    })

            history_list.append({
                'slip_id': borrow_slip.id,
                'borrow_date': borrow_slip.borrow_date.strftime('%d/%m/%Y'),
                'due_date': borrow_slip.due_date.strftime('%d/%m/%Y'),
                'status': status,
                'penalty_fee': borrow_slip.penalty_fee,
                'books': books
            })

    return render_template("reader/history.html",
                          user=user,
                          reader=reader,
                          history_list=history_list)


@history_bp.route('/api/return-slip/<int:slip_id>', methods=['POST'])
@permission(allow={"roles": [UserRole.READER], "access": True})
def api_return_slip(slip_id):
    success, message = request_return_borrow_slip(slip_id, current_user.id)
    return jsonify({'success': success, 'message': message})
