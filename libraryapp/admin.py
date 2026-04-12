from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user
from libraryapp.models import UserRole



class StandardAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


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