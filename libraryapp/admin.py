from flask import redirect, request
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from wtforms import StringField, BooleanField
from wtforms.validators import Optional, DataRequired

from libraryapp import app, db
from libraryapp.utils import hash_password
from libraryapp.models import UserRole, User, Reader, Book


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


from wtforms import StringField, BooleanField, Form
from wtforms.validators import DataRequired, Optional

class ReaderView(AuthenticatedAdmin):
    column_list = ['id', 'user.name', 'user.username', 'user.email', 'user.phone', 'user.active']
    column_labels = {
        'user.name': 'Họ tên',
        'user.username': 'Tên đăng nhập',
        'user.email': 'Email',
        'user.phone': 'SĐT',
        'user.active': 'Kích hoạt',
    }
    column_searchable_list = ['user.name', 'user.username', 'user.email']
    column_filters = ['user.active']
    create_modal = True
    edit_modal = True

    def get_edit_form(self):
        from flask_admin.form import BaseForm
        form_class = type('ReaderEditForm', (BaseForm,), {
            'name':   StringField('Họ tên',        validators=[DataRequired()]),
            'phone':  StringField('Số điện thoại', validators=[DataRequired()]),
            'email':  StringField('Email',          validators=[Optional()]),
            'active': BooleanField('Kích hoạt'),
        })
        return form_class

    def edit_form(self, obj):
        form = super().edit_form(obj)
        if request.method == 'GET' and obj and obj.user:
            form.name.data = obj.user.name
            form.phone.data = obj.user.phone
            form.email.data = obj.user.email
            form.active.data = obj.user.active
        return form

    def on_model_change(self, form, model, is_created):
        if model.user:
            model.user.name   = form.name.data
            model.user.phone  = form.phone.data
            model.user.email  = form.email.data
            model.user.active = form.active.data
            db.session.add(model.user)
            db.session.commit()

class BookView(AuthenticatedAdmin):
    column_list = ['id', 'title', 'author', 'type', 'publish_year', 'quantity']

    column_searchable_list = ['title', 'author', 'type']
    column_filters = ['type', 'publish_year']

    column_labels = {
        'title': 'Tên sách',
        'author': 'Tác giả',
        'type': 'Thể loại',
        'publish_year': 'Năm xuất bản',
        'quantity': 'Số lượng',
    }

    column_sortable_list = ['title', 'author', 'publish_year', 'quantity']

    form_columns = ['title', 'author', 'type', 'publish_year', 'quantity', 'active']

    create_modal = True
    edit_modal = True

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

class BaseModelAdminView(ModelView):
    column_display_pk = True
    edit_modal = True
    page_size = 10

admin = Admin(app=app, name="Quản trị hệ thống thư viện")
admin.add_view(ReaderView(Reader, db.session, name='Quản lý đọc giả'))
admin.add_view(BookView(Book, db.session, name='Quản lý sách'))
admin.add_view(LogoutView(name='Đăng xuất'))