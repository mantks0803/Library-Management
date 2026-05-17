from flask import Blueprint, request
from sqlalchemy import Null

from libraryapp import login
from flask import render_template
from libraryapp.dao.users import get_current_user
from libraryapp import app
import math
from libraryapp.dao import books

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    keyword = request.args.get("keyword")
    author = request.args.get("author")
    type = request.args.get("type")
    page = int(request.args.get("page", 1))
    err_msg = None


    if (((keyword and len(keyword.strip()) < 2) or (keyword == Null and type == Null))
            or ((author and len(author.strip()) < 2) or (keyword == Null and type == Null))):
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
        pages = math.ceil(books.count_books() / page_size) if books.count_books() > 0 else 1

    types = books.get_all_book_types()

    return render_template("index.html", books=data_books, pages=pages, types=types, err_msg=err_msg)


@login.user_loader
def load_user(user_id):
    return get_current_user(user_id)