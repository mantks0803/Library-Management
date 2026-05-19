from flask import Blueprint, render_template, session, jsonify, redirect, flash
from flask_login import current_user
from datetime import datetime, timedelta

from libraryapp.utils import permission
from libraryapp.dao.books import get_book
from libraryapp.dao.borrow_slips import create_borrow_slip_multiple, check_and_update_overdue_slips
from libraryapp.dao.borrow_history import count_reader_borrowing_books
from libraryapp.models import Reader, User, UserRole, BorrowSlip, BorrowSlipStatus
from libraryapp.api.api_cart import get_cart, save_cart
from libraryapp import db

borrow_bp = Blueprint('borrow', __name__)

@borrow_bp.route('/cart/view', methods=['GET'])
@permission(allow={
    "roles": [UserRole.READER],
    "access": True
})
def view_cart():

    cart = get_cart()

    books = []
    for book_id in cart:
        book = get_book(book_id)
        if book:
            books.append(book)

    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=7)
    borrow_date_str = borrow_date.strftime('%d/%m/%Y')
    due_date_str = due_date.strftime('%d/%m/%Y')

    # Đếm số sách đang mượn
    borrowing_count = count_reader_borrowing_books(current_user.id)
    total_books = borrowing_count + len(cart)

    return render_template('reader/borrow_cart.html',
                         books=books,
                         borrow_date=borrow_date_str,
                         due_date=due_date_str,
                         cart_count=len(cart),
                         borrowing_count=borrowing_count,
                         total_books=total_books)

@borrow_bp.route('/cart/confirm', methods=['POST'])
@permission(allow={
    "roles": [UserRole.READER],
    "access": True
})
def confirm():
    cart = get_cart()

    reader = Reader.query.get(current_user.id)

    if reader:
        check_and_update_overdue_slips(reader.id)



    if not reader or reader.status.name == 'LOCKED':
        return jsonify({
            'success': False,
            'message': 'Tài khoản của bạn đang bị khóa! Vui lòng liên hệ thư viện để được hỗ trợ.'
        })


    overdue_slip = db.session.query(BorrowSlip).filter(
        BorrowSlip.reader_id == reader.id,
        BorrowSlip.status == BorrowSlipStatus.OVERDUE
    ).first()

    if overdue_slip:
        return jsonify({
            'success': False,
            'message': f'Bạn không thể mượn sách! Vui lòng trả sách quá hạn trước (Phiếu mượn #{overdue_slip.id}).'
        })


    borrowing_count = count_reader_borrowing_books(reader.id)
    total_books = borrowing_count + len(cart)

    if total_books > 5:
        return jsonify({
            'success': False,
            'message': f'Bạn chỉ được mượn tối đa 5 quyển sách! Hiện tại bạn đang mượn {borrowing_count} quyển, thêm {len(cart)} quyển sẽ vượt quá giới hạn.'
        })


    borrow_slip, details = create_borrow_slip_multiple(
        reader_id=reader.id,
        book_ids=cart,
        days=7
    )

    if borrow_slip:
        save_cart([])
        return jsonify({
            'success': True,
            'message': 'Đã mượn sách thành công! Vui lòng đến thư viện để nhận sách.'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Lỗi khi tạo phiếu mượn. Vui lòng thử lại sau!'
        })


