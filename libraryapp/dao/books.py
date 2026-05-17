from libraryapp.models import Book
from libraryapp import db, app
import cloudinary.uploader
from sqlalchemy import and_


def get_list_books(full=False, page=1, keyword=None, author=None, type=None):

    query = Book.query

    if not full:
        query = query.filter(Book.active.is_(True))

    if keyword and len(keyword.strip()) >= 2:
        query = query.filter(Book.title.ilike(f'%{keyword.strip()}%'))

    if author and len(author.strip()) >= 2:
        query = query.filter(Book.author.ilike(f'%{author.strip()}%'))

    if type and len(type.strip()) >= 2:
        query = query.filter(Book.type.ilike(f'%{type.strip()}%'))

    if page:
        page_size = app.config['PAGE_SIZE']
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

def add_book(title, author, type, publish_year=None, quantity=1, avatar=None):
    try:
        new_book = Book(title=title, author=author, type=type, publish_year=publish_year, quantity=quantity)
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            new_book.avatar = res.get("secure_url")
        db.session.add(new_book)
        db.session.commit()

        return True, new_book

    except Exception as e:
        db.session.rollback()
        return False, str(e)



