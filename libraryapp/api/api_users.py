from flask import Blueprint, jsonify, request
from libraryapp.utils import permission,hash_password
from libraryapp.dao import users
from flask_login import  current_user

api_users_bp = Blueprint('api_users', __name__)

@api_users_bp.route('/api/users/<int:id>', methods=['PUT'])
@permission()
def update_infor_users(id):
    try:
        name = request.form.get("name")
        phone = request.form.get("phone")
        users.update_user(id, name, phone)
        return jsonify({"ok": True, "message": "Update user successfully"})
    except Exception as ex:
        return jsonify({"ok": False, "error": str(ex)})

#man
@api_users_bp.route('/api/users/change-password', methods=['PUT'])
@permission()
def change_password_api():
    try:
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if current_user.password != hash_password(old_password):
            return jsonify({"ok": False, "error": "Mật khẩu hiện tại không chính xác!"})
        if new_password != confirm_password:
            return jsonify({"ok": False, "error": "Mật khẩu xác nhận không khớp!"})
        users.change_password(current_user, new_password)

        return jsonify({"ok": True, "message": "Đổi mật khẩu thành công!"})

    except Exception as ex:
        return jsonify({"ok": False, "error": str(ex)})