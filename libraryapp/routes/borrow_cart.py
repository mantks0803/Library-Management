from flask import Blueprint, render_template, session, jsonify, redirect, flash
from flask_login import current_user
from datetime import datetime, timedelta

from libraryapp.utils import permission
from libraryapp.dao.books import get_book
from libraryapp.dao.borrow_slips import create_borrow_slip_multiple
from libraryapp.models import Reader, User, UserRole
from libraryapp.api.api_cart import get_cart, save_cart

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

    return render_template('reader/borrow_cart.html',
                         books=books,
                         borrow_date=borrow_date_str,
                         due_date=due_date_str,
                         cart_count=len(cart))

@borrow_bp.route('/cart/confirm', methods=['POST'])
@permission(allow={
    "roles": [UserRole.READER],
    "access": True
})
def confirm():
    cart = get_cart()

    reader = Reader.query.get(current_user.id)

    # Tạo phiếu mượn
    borrow_slip, details = create_borrow_slip_multiple(
        reader_id=reader.id,
        book_ids=cart,
        days=7
    )

    if borrow_slip:
        save_cart([])
        flash("Đã mượn sách thành công! Vui lòng đến thư viện để nhận sách và xem thông tin phiếu mượn trong trang cá nhân.")
        return redirect('/')
    else:
        flash("Lỗi khi tạo phiếu mượn. Vui lòng thử lại sau!")
        return redirect('/')
