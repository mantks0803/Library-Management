from flask import Blueprint, render_template, request
from flask_login import current_user

from libraryapp import app
from libraryapp.dao.users import get_current_user
from libraryapp.dao.books import get_book

book_bp = Blueprint('book-detal', __name__)


@book_bp.route('/book-detail/<int:id>', methods=['GET'])
def book_detail(id):
    book = get_book(id)
    user = get_current_user(current_user.id) if current_user.is_authenticated else None

    return render_template("reader/book_detail.html", book=book, user=user)
