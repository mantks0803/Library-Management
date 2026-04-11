from libraryapp.models import Reader
from flask_login import current_user
from libraryapp import db, app
from sqlalchemy import and_


def get_reader(id):
    reader = Reader.query.get(id)
    return reader


def get_list_readers(full=False, page=1):
    query = Reader.query

    if not full:
        query = query.filter(Reader.id == current_user.id, Reader.active.is_(True))
    else:
        query = query.filter(Reader.active.is_(True))

    if page:
        page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size
        query = query.slice(start, start + page_size)

    return query.all()


def count_readers(full=False):
    return Reader.query.filter(Reader.active.is_(True)).count() if full \
        else Reader.query.filter(and_(Reader.active.is_(True), Reader.id == current_user.id)).count()


# def delete_soft_reader(id):
#     reader = Reader.query.get(id)
#     reader.active = False
#     db.session.commit()