from flask import Blueprint, request

from libraryapp import login
from flask import render_template

from libraryapp.dao.borrow_history import get_borrow_slip_status_overdue
from libraryapp.dao.borrow_slips import check_and_update_overdue_slips
from libraryapp.dao.readers import get_reader
from libraryapp.dao.users import get_current_user
from libraryapp import app
import math
from libraryapp.dao import books
from flask_login import current_user
home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    check_and_update_overdue_slips()
    remaining_overdue = 0

    if current_user.is_authenticated:
        user = get_current_user(current_user.id)
        reader = get_reader(user.id)

        if reader:
            remaining_overdue = len(get_borrow_slip_status_overdue(reader.id))

    keyword = request.args.get("keyword")
    author = request.args.get("author")
    type = request.args.get("type")
    page = int(request.args.get("page", 1))


    err_msg = None

    is_searching = 'keyword' in request.args

    if is_searching:
        if not keyword and not author and not type:
            err_msg = "Vui lòng nhập ít nhất 1 điều kiện để tìm kiếm!"
        elif (keyword and len(keyword) < 2) or (author and len(author) < 2):
            err_msg = "Vui lòng nhập ít nhất 2 ký tự đối với tên sách hoặc tên tác giả!"

    if (keyword and len(keyword.strip()) < 2) or (author and len(author.strip()) < 2):
        err_msg = "Vui lòng nhập ít nhất 2 ký tự để tìm kiếm!"
        data_books = []
        pages = 0
    else:
        data_books = books.get_list_books(
            page=page,
            keyword=keyword,
            author=author,
            type=type
        )

        page_size = app.config['PAGE_SIZE']
        total_books = books.count_books(keyword=keyword, author=author, type=type)
        pages = math.ceil(total_books / page_size) if total_books > 0 else 1

    types = books.get_all_book_types()

    return render_template("index.html", books=data_books, pages=pages, types=types, err_msg=err_msg, remaining_overdue=remaining_overdue,
                           keyword=keyword, author=author, type=type)


@login.user_loader
def load_user(user_id):
    return get_current_user(user_id)