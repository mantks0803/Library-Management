from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask import redirect, url_for
from flask_login import current_user
from libraryapp.models import UserRole, Reader


class StandardAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    @expose('/')
    def index(self):
        return redirect(url_for('book.index_view'))  # QLsach


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