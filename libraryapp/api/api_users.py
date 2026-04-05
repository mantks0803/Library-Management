from flask import Blueprint, jsonify, request
from libraryapp.utils import permission
from libraryapp.dao import users

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