from flask import Blueprint, session, jsonify
from flask_login import login_required, current_user
from libraryapp.utils import permission
from libraryapp.dao.books import get_book
from libraryapp.models import User, UserRole

api_cart_bp = Blueprint('api_cart', __name__)

CART_SESSION_KEY = 'borrow_cart'


def get_cart():
    return session.get(CART_SESSION_KEY, [])


def save_cart(cart):
    session[CART_SESSION_KEY] = cart
    session.modified = True


@api_cart_bp.route('/cart/add/<int:book_id>', methods=['POST'])
@permission(allow={
    "roles": [UserRole.READER],
    "access": True
})
def add_to_cart(book_id):

    book = get_book(book_id)

    if book.quantity <= 0:
        return jsonify({'success': False, 'message': 'Sách đã hết!'})

    cart = get_cart()

    if book_id in cart:
        return jsonify({'success': False, 'message': 'Sách đã có trong giỏ mượn!'})

    if len(cart) >= 5:
        return jsonify({'success': False, 'message': 'Bạn chỉ có thể mượn tối đa 5 cuốn sách!'})

    cart.append(book_id)
    save_cart(cart)

    return jsonify({
        'success': True,
        'message': f'Đã thêm "{book.title}" vào giỏ mượn!',
        'cart_count': len(cart)
    })

@api_cart_bp.route('/cart/remove/<int:book_id>', methods=['POST'])
@permission(allow={
    "roles": [UserRole.READER],
    "access": True
})
def remove_from_cart(book_id):
    cart = get_cart()

    if book_id in cart:
        cart.remove(book_id)
        save_cart(cart)
        return jsonify({'success': True, 'message': 'Đã xóa sách khỏi giỏ!', 'cart_count': len(cart)})

    return jsonify({'success': False, 'message': 'Sách không có trong giỏ!'})


@api_cart_bp.route('/cart/clear', methods=['POST'])
@permission(allow={
    "roles": [UserRole.READER],
    "access": True
})
def clear_cart():
    save_cart([])
    return jsonify({'success': True, 'message': 'Giỏ mượn đã được xóa!'})

@api_cart_bp.route('/cart/count', methods=['GET'])
@permission(allow={
    "roles": [UserRole.READER],
    "access": True
})
def get_cart_count():
    cart = get_cart()
    return jsonify({'count': len(cart)})


