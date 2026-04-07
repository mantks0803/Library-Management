from libraryapp.models import Book
from libraryapp import db, app


def get_list_books(keyword=None, author=None, type=None, page=1):
    """Lấy danh sách sách với các bộ lọc"""
    query = Book.query.filter(Book.active.is_(True))

    if keyword:
        query = query.filter(Book.title.ilike(f'%{keyword}%'))

    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))

    if type:
        query = query.filter(Book.type.ilike(f'%{type}%'))

    if page:
        page_size = app.config.get('PAGE_SIZE', 6)
        start = (page - 1) * page_size
        query = query.slice(start, start + page_size)

    return query.all()


def count_books(keyword=None, author=None, type=None):
    """Đếm tổng số sách (dùng cho phân trang)"""
    query = Book.query.filter(Book.active.is_(True))

    if keyword:
        query = query.filter(Book.title.ilike(f'%{keyword}%'))

    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))

    if type:
        query = query.filter(Book.type.ilike(f'%{type}%'))

    return query.count()


def get_book(id):
    """Lấy chi tiết 1 quyển sách"""
    return Book.query.get(id)