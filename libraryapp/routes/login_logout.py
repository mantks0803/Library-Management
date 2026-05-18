from flask import Blueprint, render_template, request, redirect
from libraryapp.dao.users import auth_user
from libraryapp.api.api_cart import clear_cart
from flask_login import login_user, logout_user, login_required, current_user

from libraryapp.utils import permission

login_logout_bp = Blueprint('login_logout', __name__)


@login_logout_bp.route('/login')
def render_login():
    if current_user.is_authenticated:
        return redirect('/')
    return render_template('auth/login.html')


@login_logout_bp.route('/logout')
def logout_process():
    clear_cart()
    logout_user()
    return redirect('/login')


@login_logout_bp.route('/login', methods=['POST'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')
    user = auth_user(username, password)

    if user:
        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page if next_page else '/')
    else:
        return render_template('auth/login.html', err_msg="Tên đăng nhập hoặc mật khẩu không chính xác!")



@login_logout_bp.route('/profile')
@permission()
def profile_view():
    return render_template('auth/profile.html')