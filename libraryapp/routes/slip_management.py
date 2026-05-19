from flask import Blueprint, render_template, request, redirect, flash, jsonify
from flask_login import current_user
from libraryapp import app
from libraryapp.models import UserRole, BorrowSlip, BorrowSlipStatus, BorrowSlipDetail, Book
from libraryapp.utils import permission
from libraryapp.dao.borrow_slips import confirm_return_borrow_slip, check_and_update_overdue_slips
from libraryapp import db
import math

slip_management_bp = Blueprint('slip_management', __name__)


@slip_management_bp.route('/slip', methods=['GET'])
@permission(allow={"roles": [UserRole.ADMIN], "access": True})
def slip_management():

    check_and_update_overdue_slips()

    status_filter = request.args.get("status", "all")
    page = int(request.args.get("page", 1))

    query = BorrowSlip.query

    if status_filter == "pending":
        query = query.filter(BorrowSlip.status == BorrowSlipStatus.PENDING)
    elif status_filter == "borrowing":
        query = query.filter(BorrowSlip.status == BorrowSlipStatus.BORROWING)
    elif status_filter == "returned":
        query = query.filter(BorrowSlip.status == BorrowSlipStatus.RETURNED)
    elif status_filter == "overdue":
        query = query.filter(BorrowSlip.status == BorrowSlipStatus.OVERDUE)

    total_slips = query.count()
    pages = math.ceil(total_slips / app.config['PAGE_SIZE']) if total_slips > 0 else 1


    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    slips = query.order_by(BorrowSlip.id.desc()).slice(start, start + page_size).all()


    total_pending = BorrowSlip.query.filter(BorrowSlip.status == BorrowSlipStatus.PENDING).count()
    total_borrowing = BorrowSlip.query.filter(BorrowSlip.status == BorrowSlipStatus.BORROWING).count()
    total_returned = BorrowSlip.query.filter(BorrowSlip.status == BorrowSlipStatus.RETURNED).count()
    total_overdue = BorrowSlip.query.filter(BorrowSlip.status == BorrowSlipStatus.OVERDUE).count()

    return render_template(
        "admin/slip_management.html",
        slips=slips,
        total_slips=total_slips,
        current_page=page,
        pages=pages,
        status_filter=status_filter,
        total_pending=total_pending,
        total_borrowing=total_borrowing,
        total_returned=total_returned,
        total_overdue=total_overdue
    )


@slip_management_bp.route('/slip/approve/<int:slip_id>', methods=['POST'])
@permission(allow={"roles": [UserRole.ADMIN], "access": True})
def approve_slip(slip_id):
    try:
        success, message = confirm_return_borrow_slip(slip_id)

        if success:
            flash(f" {message}", "success")
        else:
            flash(f" {message}", "danger")

    except Exception as e:
        flash(f"Lỗi hệ thống: {str(e)}", "danger")

    return redirect(f"/slip?status=pending")




