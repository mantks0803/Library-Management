from flask import Blueprint, render_template, request
from flask_login import current_user

from libraryapp import app
from libraryapp.models import UserRole
from libraryapp.utils import permission
from libraryapp.dao.users import get_current_user
from libraryapp.dao.readers import get_list_readers, count_readers
import math

infor_user_bp = Blueprint('infor_user', __name__)

@infor_user_bp.route('/user', methods=['GET'])
@permission()
def render_user():
    user = get_current_user(current_user.id)
    page = int(request.args.get("page", 1))
    readers = get_list_readers(page=page)
    pages = math.ceil(count_readers() / app.config['PAGE_SIZE'])
    return render_template("reader/reader.html", user=user, readers=readers, pages=pages)

@infor_user_bp.route('/user/infor', methods=['GET'])
@permission()
def render_edit_infor():
    user = get_current_user(current_user.id)
    return render_template("auth/update_infor_user.html", user=user)