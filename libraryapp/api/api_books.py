from flask import Blueprint, request, jsonify
from libraryapp.dao import books

api_books_bp = Blueprint('api_books', __name__)


@api_books_bp.route('/api/books', methods=['GET'])
def get_books():
    """Lấy danh sách sách với tìm kiếm"""
    keyword = request.args.get('kw', '')
    author = request.args.get('author', '')
    type = request.args.get('type', '')
    page = int(request.args.get('page', 1))

    try:
        list_books = books.load_books(keyword=keyword if keyword else None,
                                      author=author if author else None,
                                      type=type if type else None,
                                      page=page)

        if list_books:
            result = [
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "type": book.type,
                    "publish_year": book.publish_year,
                    "quantity": book.quantity
                }
                for book in list_books
            ]
            return jsonify({"ok": True, "data": result})
        else:
            return jsonify({"ok": False, "message": "Không có sách nào"})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


@api_books_bp.route('/api/books/<int:book_id>', methods=['GET'])
def get_book_detail(book_id):
    """Lấy chi tiết một quyển sách"""
    try:
        book = books.get_infor_book(book_id)
        if book:
            result = {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "type": book.type,
                "publish_year": book.publish_year,
                "quantity": book.quantity
            }
            return jsonify({"ok": True, "data": result})
        else:
            return jsonify({"ok": False, "message": "Sách không tồn tại"})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})