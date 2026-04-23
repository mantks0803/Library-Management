from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme

import cloudinary

app = Flask(__name__)

app.secret_key = "!@#$%jasbej%$^(+eiwqbacjfas12399HBAS59^##GSDFG%%jjs;zs4$$"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:08032005@localhost/librarydb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE'] = 50

db = SQLAlchemy(app=app)
login = LoginManager(app=app)
babel = Babel(app, locale_selector=lambda: request.accept_languages.best_match(['vi', 'en']))

from libraryapp.admin import StandardAdminIndexView, BookView, UserView,BorrowSlipView
from libraryapp.models import Book, User,BorrowSlip

admin = Admin(
    app=app,
    name="QUẢN TRỊ THƯ VIỆN",
    theme=Bootstrap4Theme(swatch='flatly'),
    index_view=StandardAdminIndexView()
    )
admin.add_view(BookView(Book, db.session, name="Quản Lý Sách"))
admin.add_view(UserView(User, db.session, name="Quản Lý Người dùng"))
admin.add_view(BorrowSlipView(BorrowSlip, db.session, name="Duyệt Trả Sách"))
# cloudinary.config(
#     cloud_name='dt1pa28g2',
#     api_key='824465552867193',
#     api_secret='A9MAKfzfQok2sZCjtIuhsDBTzis'
# )