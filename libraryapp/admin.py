from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask import redirect, url_for, flash
from flask_login import current_user

from libraryapp.dao.borrow_slips import confirm_return_borrow_slip
from libraryapp.models import UserRole, Reader


class StandardAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    @expose('/')
    def index(self):
        return redirect(url_for('book.index_view'))


class AuthenticatedModelView(ModelView):
    column_display_pk = True
    edit_modal = True
    page_size = 10

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class BookView(AuthenticatedModelView):
    column_searchable_list = ['title', 'author']
    column_filters = ['type', 'quantity']


class UserView(AuthenticatedModelView):
    column_searchable_list = ['name', 'username', 'phone']
    column_exclude_list = ['password']


class BorrowSlipView(AuthenticatedModelView):
    column_list = ['id', 'reader_id', 'borrow_date', 'due_date', 'status', 'penalty_fee']
    column_filters = ['status']

    @expose('/approve_return/<int:slip_id>', methods=['POST'])
    def approve_return(self, slip_id):
        success, message = confirm_return_borrow_slip(slip_id)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('borrowslip.index_view'))