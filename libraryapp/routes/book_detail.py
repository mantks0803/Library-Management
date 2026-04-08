from flask import Blueprint
from flask import render_template

book_bp = Blueprint('book', __name__)


@book_bp.route('/book')
def book():
    return render_template("book_detail.html")
