from libraryapp.models import Book
from libraryapp import db, app
from sqlalchemy import and_


def get_list_books(full=False, page=1, keyword=None, author=None, type=None):
    """
    Lấy danh sách sách với tìm kiếm và phân trang
    - Có thể tìm theo: tên sách, tác giả, thể loại
    - Tối đa 50 bản ghi mỗi trang
    """
    query = Book.query

    if not full:
        query = query.filter(Book.active.is_(True))
    else:
        query = query.filter(Book.active.is_(True))

    if keyword and len(keyword.strip()) >= 2:
        query = query.filter(Book.title.ilike(f'%{keyword.strip()}%'))

    if author and len(author.strip()) >= 2:
        query = query.filter(Book.author.ilike(f'%{author.strip()}%'))

    if type and len(type.strip()) >= 2:
        query = query.filter(Book.type.ilike(f'%{type.strip()}%'))

    if page:
        page_size = app.config['PAGE_SIZE']  # 50 bản ghi/trang
        start = (page - 1) * page_size
        query = query.slice(start, start + page_size)

    return query.all()


def count_books():
    return Book.query.count()


def get_book(id):
    return Book.query.get(id)


def get_all_book_types():
    types = db.session.query(Book.type).filter(Book.active.is_(True)).distinct().all()
    return [t[0] for t in types if t[0]]



