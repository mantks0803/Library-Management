from flask import Blueprint, request
from libraryapp import login
from flask import render_template
from libraryapp.dao.users import get_current_user
from libraryapp.dao.books import get_list_books, count_books
import math

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '', type=str)
    author = request.args.get('author', '', type=str)
    type = request.args.get('type', '', type=str)
    
    # Lấy danh sách sách
    books = get_list_books(keyword=keyword if keyword else None, 
                           author=author if author else None, 
                           type=type if type else None,
                           page=page)
    
    # Đếm tổng số sách để tính số trang
    total_books = count_books(keyword=keyword if keyword else None, 
                              author=author if author else None, 
                              type=type if type else None)
    page_size = 6  # Số sách mỗi trang
    pages = math.ceil(total_books / page_size)
    
    return render_template("index.html", books=books, pages=pages, current_page=page)


@login.user_loader
def load_user(user_id):
    return get_current_user(user_id)