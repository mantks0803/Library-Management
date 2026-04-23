from flask import Blueprint, render_template, request, redirect, flash
from flask_login import current_user
from libraryapp import app
from libraryapp.models import UserRole
from libraryapp.utils import permission
from libraryapp.dao.books import get_list_books, count_books, add_book
from libraryapp.utils import is_image
import math

book_management_bp = Blueprint('book_management', __name__)


@book_management_bp.route('/book', methods=['GET'])
@permission(allow={"roles": [UserRole.ADMIN], "access": True})
def book_management():
    page = int(request.args.get("page", 1))
    books = get_list_books(full=True, page=page)
    total_books = count_books()
    pages = math.ceil(total_books / app.config['PAGE_SIZE']) if total_books > 0 else 1

    return render_template(
        "admin/book_management.html",
        books=books,
        total_books=total_books,
        current_page=page,
        pages=pages
    )


@book_management_bp.route('/book/add', methods=['POST'])
@permission(allow={"roles": [UserRole.ADMIN], "access": True})
def add_book_process():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    type_book = request.form.get("type", "").strip()
    publish_year = request.form.get("publish_year", "").strip()
    quantity = request.form.get("quantity", "1").strip()
    avatar = request.form.get("avatar", "").strip()

    # Validation
    if not title:
        flash("Tên sách không được để trống!", "danger")
        return redirect("/book")

    if not author:
        flash("Tác giả không được để trống!", "danger")
        return redirect("/book")

    if not type_book:
        flash("Thể loại không được để trống!", "danger")
        return redirect("/book")

    if not is_image(avatar.filename):
        return render_template("admin/book_management.html", err_msg="File không hợp lệ!")

    try:
        publish_year = int(publish_year) if publish_year else None
        quantity = int(quantity) if quantity and quantity.isdigit() else 1

        if quantity < 1:
            flash("Số lượng phải lớn hơn 0!", "danger")
            return redirect("/book")

        # Thêm sách
        success, result = add_book(
            title=title,
            author=author,
            type=type_book,
            publish_year=publish_year,
            quantity=quantity,
            avatar=avatar
        )

        if success:
            flash(f"✅ Thêm sách '{title}' thành công!", "success")
        else:
            flash(f"❌ Lỗi: {result}", "danger")

    except ValueError:
        flash("Năm xuất bản và số lượng phải là số!", "danger")
    except Exception as e:
        flash(f"❌ Lỗi hệ thống: {str(e)}", "danger")

    return redirect("/book")

