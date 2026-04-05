from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from libraryapp.utils import hash_password
from libraryapp.models import UserRole, User


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class BaseModelAdminView(ModelView):
    column_display_pk = True
    edit_modal = True
    page_size = 10