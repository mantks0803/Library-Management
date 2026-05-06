from libraryapp.models import User, UserRole, Reader
from libraryapp import db
from libraryapp.utils import hash_password
import re

def get_current_user(user_id):
    return User.query.get(user_id)

def auth_user(username, password):
    password = hash_password(password)
    return User.query.filter(User.username == username, User.password == password).first()

def add_user(name, phone, email, username, password):
    if len(password) < 8:
        raise ValueError('Password phải từ 8 kí tự trở lên!')
    if not re.search(r'[0-9]', password):
        raise ValueError('Password phải có số!')
    if not re.search(r'[a-z]', password):
        raise ValueError('Password phải có ký thường!')
    if not re.search(r'[A-Z]', password):
        raise ValueError('Password phải có ký tự hoa!')
    if User.query.filter(User.username.__eq__(username)).first():
        raise ValueError('Username đã tồn tại!')
    password = hash_password(password)
    user = User(name=name.strip(), phone=phone, email=email.strip(), username=username.strip(), password=password, user_role=UserRole.READER)

    db.session.add(user)
    db.session.flush()  # Để lấy user.id

    reader = Reader(id=user.id)
    db.session.add(reader)

    db.session.commit()

def update_user(user_id, name, phone):
    user = User.query.get(user_id)
    if not re.match(r'^0\d{9}$', phone):
        raise ValueError("Số điện thoại không hợp lệ!")
    user.name = name
    user.phone = phone
    db.session.commit()

def change_password(user, new_password):
    user.password = hash_password(new_password)
    db.session.commit()

def validate_username(username):
    return not User.query.filter(User.username==username).first()

def validate_phone(phone):
    return bool(re.match(r"^(01|02|03|04|05|06|07|08|09)\d{8}$", phone))

def validate_password(pwd, confirm):
    return pwd == confirm