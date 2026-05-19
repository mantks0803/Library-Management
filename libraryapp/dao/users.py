from libraryapp.models import User, UserRole, Reader
from libraryapp import db
from libraryapp.utils import hash_password
import re


def validate_password(password, confirm_password=None):
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự!"

    # Check có số
    if not re.search(r"[0-9]", password):
        return False, "Mật khẩu phải chứa ít nhất một chữ số!"

    if not re.search(r"[a-z]", password):
        return False, "Mật khẩu phải chứa ít nhất một chữ thường!"

    if not re.search(r"[A-Z]", password):
        return False, "Mật khẩu phải chứa ít nhất một chữ hoa!"

    # Check xác nhận mật khẩu
    if confirm_password and password != confirm_password:
        return False, "Mật khẩu xác nhận không khớp!"

    return True, "OK"


def get_current_user(user_id):
    return User.query.get(user_id)


def auth_user(username, password):
    password = hash_password(password)
    return User.query.filter(User.username == username, User.password == password).first()


def add_user(name, phone, email, username, password, confirm):
    if not name or not name.strip():
        raise ValueError("Họ tên không được để trống!")

    if not username or not username.strip():
        raise ValueError("Tên đăng nhập không được để trống!")

    if not phone or not re.match(r"^(01|02|03|04|05|06|07|08|09)\d{8}$", phone):
        raise ValueError("Số điện thoại không hợp lệ!")

    valid, msg = validate_password(password, confirm)
    if not valid:
        raise ValueError(msg)

    if User.query.filter(User.username == username.strip()).first():
        raise ValueError("Username đã tồn tại!")

    password = hash_password(password)

    user = User(
        name=name.strip(),
        phone=phone.strip(),
        email=email.strip(),
        username=username.strip(),
        password=password,
        user_role=UserRole.READER
    )

    db.session.add(user)
    db.session.flush()

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
    valid, msg = validate_password(new_password)
    if not valid:
        raise ValueError(msg)
    user.password = hash_password(new_password)
    db.session.commit()